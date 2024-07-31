# inter_project_hlr_mapper.py
#
# This script creates a table of identity relationships between HLRs of two different documents.
# The IDs between the two documents are mapped together for making the LLR traceability process easier in a new project.
# Note: the following HLR relationships were created manually because the script's algorithm just isn't sophisticated enough to deal with HLRs that have slightly more inconsequential detail etc.:
# old_id	new_id
# 206,	  13
# 677,	  36
# 542,	  47
# 552,	  57
# 553,	  58
# 475,	  190
# 478,	  206
# 601,	  206
# 480,	  206
# 88,	    226
# 107,	  236
# 103,	  206
# 144,	  233

import os, argparse, re, sys, csv
import pandas as pd

hlr_column_text = "High-Level"
id_column_name = "ID"
map_old_id_column_name = 'old_id'
map_new_id_column_name = 'new_id'

class HlrInfo:
  def __init__(self, hlr_filename):
    self.id_column_idx = -1
    self.description_column_idx = -1
    self.dataframe = pd.read_excel(hlr_filename)
    if self.dataframe.empty:
      raise Exception('Failed to read Excel file ' + hlr_filename)
    headers = self.dataframe.head(1)
    for column_idx, name in enumerate(headers):
      if hlr_column_text in name:
        self.description_column_idx = column_idx
        self.dataframe.rename(columns={self.dataframe.columns[column_idx]: 'description'}, inplace=True)
      if id_column_name == name:
        self.id_column_idx = column_idx
        self.dataframe.rename(columns={self.dataframe.columns[column_idx]: 'id'}, inplace=True)
    if self.id_column_idx == -1:
      raise Exception('HLR file does not have column with \'' + id_column_name + '\' in it')
    if self.description_column_idx == -1:
      raise Exception('HLR file does not have a definition column with \'' + hlr_column_text + '\' in it')

def main(argv):
  # Create the argument parser
  parser = argparse.ArgumentParser(description='Example Argument Parser')
  # Add the old hlr file option
  parser.add_argument('--old_hlrs', help='Old HLR file (.xlsx)')
  # Add the new hlr file option
  parser.add_argument('--new_hlrs', help='New HLR file (.xlsx)')
  # Parse the arguments
  args = parser.parse_args()
  if args.old_hlrs:
    old_hlr_filename = args.old_hlrs
  else:
    print('no old HLR file given (--old_hlrs)')
    sys.exit()
  if args.new_hlrs:
    new_hlr_filename = args.new_hlrs
  else:
    print('no new HLR file given (--new_hlrs)')
    sys.exit()

  output_filename = "hlr_map.csv"
  GenerateMap(old_hlr_filename, new_hlr_filename, output_filename)
      
def GenerateMap( old_hlr_filename, new_hlr_filename, output_filename ):
  try:
    old_hlrs = HlrInfo(old_hlr_filename)
  except Exception as error:
    print(error)
    sys.exit()
  try:
    new_hlrs = HlrInfo(new_hlr_filename)
  except Exception as error:
    print(error)
    sys.exit()

  id_map = []
  # new_hlrs.dataframe.set_index('description', inplace=True)
  # go through all old HLRs and find any matches in new HLRs. Log the indices together  
  for row in old_hlrs.dataframe.iterrows():
    row = row[1]
    hlr_def = str(row[old_hlrs.description_column_idx])
    old_hlr_id = str(row[old_hlrs.id_column_idx])
    # find the index of the row in new_hlrs that has a matching description
    if len(hlr_def.split("shall ")) > 1:
      hlr_def = hlr_def.split("shall ")[1]
    elif len(hlr_def.split("must ")) > 1:
      hlr_def = hlr_def.split("must ")[1]
    hlr_def = hlr_def.split("(DOC")[0]
    hlr_def = hlr_def.split("A429 D")[0]
    hlr_def = hlr_def.split("DOC")[0]
    hlr_def = hlr_def.split("\n")[0]
    hlr_def = hlr_def.split("_x000D_")[0]
    hlr_def = hlr_def.strip().casefold()
    mask = new_hlrs.dataframe['description'].str.casefold().str.contains(hlr_def, regex=False, case=False)
    filtered_df = new_hlrs.dataframe[mask]
    # if len(new_hlr_id) > 1: # doesn't apply to the loc method for getting a row
    #   print("Too many HLRs in new file with the description '" + hlr_def + "'")
    #   print("All HLR IDs found with the definition: " + str(new_hlr_id))
    #   sys.exit()
    # try:
    #   new_row = new_hlrs.dataframe.loc[hlr_def]
    # except:
    #   continue
    # new_hlr_id = new_row['id']
    if not filtered_df.empty:
      new_hlr_id = filtered_df['id'].values
      if type(new_hlr_id) is not int:
        new_hlr_id = new_hlr_id[0]
        new_hlr_id = int(new_hlr_id)
      id_map.append([old_hlr_id, new_hlr_id, hlr_def])

  with open(output_filename, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    # write the first row
    writer.writerow([map_old_id_column_name, map_new_id_column_name, "description"])
    # write the new rows
    for row in id_map:
      writer.writerow(row)
    # close the file
    csvfile.close()

#########################################################
#                           Main
#########################################################
if __name__ == "__main__":
  main(sys.argv[1:])
