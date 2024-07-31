# map_hlr_links.py
#
# This script maps HLRs in a new project to LLRs based on links of identical HLRs to LLRs in a previous project. It uses the output of the inter_project_hlr_mapper.py as an HLR map

import os, argparse, sys, io, csv, re, inter_project_hlr_mapper

CODE_ID_STRING = 'CodeID:'
REQUIREMENT_STRING = 'Requirement:'
JIRA_STRING = 'Jira Ticket:'
HLR_STRING = 'HLR:'
A429_STRING = 'A429 Library:'
PDI_STRING = 'PDI Library:'

HLR_PREFIX = 'ADT-SW-HLR-'

def main(argv):
  # Create the argument parser
  parser = argparse.ArgumentParser(description='Example Argument Parser')
  # Add the modules directory option
  parser.add_argument('--src_dir', help='Source directory')
  # Add the hlr file option
  parser.add_argument('--hlr_map', help='old to new HLR mapping file (.csv)')
  # Add the old llrs_extraction file option
  parser.add_argument('--llrs_extraction', help='old llrs extraction file (llrs_extraction.csv)')
  # Parse the arguments
  args = parser.parse_args()
  # Access the values of the options
  if args.src_dir:
    srcDirectory = args.src_dir + '/'
  else:
    print('no source directory given (--src_dir)')
    sys.exit()
  if args.hlr_map:
    hlr_map_file = args.hlr_map
  else:
    print('no HLR map file given (--hlr_map)')
    sys.exit()
  if args.llrs_extraction:
    old_llrs_file = args.llrs_extraction
  else:
    print('no llrs_extraction file given (--llrs_extraction)')
    sys.exit()

  for (dirpath, dirnames, filenames) in os.walk(srcDirectory):
    for name in filenames:
      if name[-2:] == '.c' or name[-4:] == '.asm' or name[-4:] == '.icf' or name[-2:] == '.s':
        # print(dirpath + '/' + name)
        AddHlrLinks(dirpath + '/' + name, GetFileAsCsvReader(old_llrs_file), GetFileAsCsvReader(hlr_map_file))
        
        
def GetFileText( fileName ):
  file = open(fileName, "r")
  fileText = file.read()
  file.close()
  return fileText

def GetFileAsCsvReader( fileName ):
  with open(fileName, encoding='utf-8-sig') as csv_file:
    csv_reader = csv.reader(csv_file)
    csv_data = []
    for row in csv_reader:
      csv_data.append(row)
  csv_file.close()
  return csv_data
  
def AddHlrLinks (filename, old_llrs, hlr_map):
  text = GetFileText(filename)
  new_text = ""

  llr_id_idx = text.find(CODE_ID_STRING)
  while llr_id_idx != -1:
    llr_id = text[llr_id_idx + len(CODE_ID_STRING) : text.find(REQUIREMENT_STRING, llr_id_idx)].strip().rstrip()
    new_text += text[:llr_id_idx]
    text = text[llr_id_idx:]
    hlr_link_idx = text.find(HLR_STRING)
    if hlr_link_idx == -1:
      print("no HLR field for LLR " + llr_id)
      sys.exit()
    else:
      hlr_links_end_idx = text.find('\n', hlr_link_idx)
      hlr_links = text[hlr_link_idx + len(HLR_STRING) : hlr_links_end_idx].strip().rstrip()
      if not hlr_links:
        new_text += text[:hlr_link_idx + len(HLR_STRING)] + ' ' + GetNewHlrs(llr_id, old_llrs, hlr_map)
        text = text[hlr_link_idx + len(HLR_STRING):]
        if text[0] == ' ':
          text = text[1:]
      else:
        new_text += text[:hlr_link_idx + len(HLR_STRING)]
        text = text[hlr_link_idx + len(HLR_STRING):]
        if text[0] == ' ':
          text = text[1:]
    llr_id_idx = text.find(CODE_ID_STRING)
  new_text += text
  WriteToFile(filename, new_text)

def GetNewHlrs(llr_id, old_llrs, hlr_map):
  new_hlr_link_numbers = []
  new_hlr_links = ''
  hlr_old_id_column = [(idx) for idx, name in enumerate(hlr_map[0]) if name == inter_project_hlr_mapper.map_old_id_column_name][0]
  hlr_new_id_column = [(idx) for idx, name in enumerate(hlr_map[0]) if name == inter_project_hlr_mapper.map_new_id_column_name][0]
  llr_id_column = [(idx) for idx, name in enumerate(old_llrs[0]) if 'CodeID' in name][0]
  hlr_link_column = [(idx) for idx, name in enumerate(old_llrs[0]) if 'HLR' in name][0]
  old_hlr_links = None

  for row in old_llrs:
    if row[llr_id_column] == llr_id:
      old_hlr_links = row[hlr_link_column]
      # print('old links: ' + str(old_hlr_links))
      break
  if old_hlr_links is not None:
    old_links_tuple = re.findall(r'ADT-SW-HLR-([0-9]+)', old_hlr_links)
    missing_old_hlr_links = []
    for link in old_links_tuple:
      new_link = [(row[hlr_new_id_column]) for row in hlr_map if row[hlr_old_id_column] == link]
      if len(new_link) > 0:
        new_link = new_link[0].strip()
        new_hlr_link_numbers.append(new_link)
      else:
        missing_old_hlr_links.append(link)
    if len(missing_old_hlr_links) > 0 and len(new_hlr_link_numbers) > 0:
      print("Missing new link for old HLR(s) " + str(missing_old_hlr_links) + " in " + str(llr_id))
    new_hlr_link_numbers = sorted(set(new_hlr_link_numbers))
    if len(new_hlr_link_numbers) > 0:
      new_hlr_links = HLR_PREFIX
    new_hlr_links = new_hlr_links + f', {HLR_PREFIX}'.join(new_hlr_link_numbers)
  # print('new links: ' + new_hlr_links)
  return new_hlr_links

def WriteToFile( filePath, text ):
  # open file to write
  with io.open(filePath, 'w', newline='\r\n') as file:
    file.write(text) #overwrites whole file
    file.close()
#########################################################
#                           Main
#########################################################
if __name__ == "__main__":
  main(sys.argv[1:])
