# sys-hlr-trace.py
#
# This script prints the sys to hlr traceability matrix

import os, argparse, re, sys, csv
import pandas as pd

hlr_name = "ADT High-Level Software Requirements"
id_column_name = "ID"
sys_id_column_name = "Abs-Num"
sys_name = "ATU System Requirements"

def main(argv):
  # Create the argument parser
  parser = argparse.ArgumentParser(description='Example Argument Parser')
  # Add the hlr file option
  parser.add_argument('--hlr', help='HLR file (.xlsx)')
  # Add the sys file option
  parser.add_argument('--sys', help='SYS requirement file (.xlsx)')
  # Add the uncovered sys option
  parser.add_argument('--uncovered', action="store_true", help='only print the uncovered SYS requirements')
  # Parse the arguments
  args = parser.parse_args()
  if args.hlr:
    hlrFileName = args.hlr
  else:
    print('no HLR file given (--hlr)')
    sys.exit()
  if args.sys:
    sysFileName = args.sys
  else:
    print('no SYS requirement file given (--sys)')
    sys.exit()
  if args.uncovered:
    output_uncovered_sys = True
  else:
    output_uncovered_sys = False

  GenerateTrace(hlrFileName, sysFileName, output_uncovered_sys)
      
def GenerateTrace( hlrFileName, sysFileName, output_uncovered_sys ):
  sys_data_frame = pd.read_excel(sysFileName)
  hlr_data_frame = pd.read_excel(hlrFileName)
  # print first row of hlr data frame
  # print(hlr_data_frame)
  try:
    testVal = hlr_data_frame.at[0, id_column_name]
  except:
    print('HLR file does not have column \'' + id_column_name + '\'')
    sys.exit()
  try:
    testVal = sys_data_frame.at[0, sys_id_column_name]
  except:
    print('SYS file does not have column \'' + sys_id_column_name + '\'')
    sys.exit()
  try:
    testVal = hlr_data_frame.at[0, 'LBA SYS']
  except:
    print('HLR file does not have LBA SYS column')
    sys.exit()
  try:
    testVal = hlr_data_frame.at[0, hlr_name]
  except:
    print('HLR file does not have a definition column \'' + hlr_name + '\'')
    sys.exit()
  sys_max_id = 0
  sys_reqs = []
  hlrs = []
  for row in sys_data_frame.iterrows():
    abs_num = row[1][sys_id_column_name]
    try:
      allocation = row[1]['Allocation']
    except:
      print('Couldn\'t find an allocation for ' + str(abs_num))
      continue
    if not pd.isna(abs_num) and type(allocation) is str and allocation.find('SW') != -1:
      sys_reqs.append([int(abs_num), row[1][sys_name]])
      if int(abs_num) > sys_max_id:
        sys_max_id = int(abs_num)
  # print('highest SYS: ' + str(sys_max_id))

  # go through all HLRs and capture the number of each one that links a system requirement in the list spot for that system requirement
  sys_req_references = [[] for _ in range(sys_max_id + 1)]
  
  for row in hlr_data_frame.iterrows():
    refs = row[1]['LBA SYS']
    hlr_def = row[1][hlr_name]
    hlr_num = int(row[1][id_column_name])
    if len(hlrs) <= hlr_num:
      hlrs += [''] * (hlr_num - len(hlrs) + 1)
    hlrs[hlr_num] = hlr_def

    if type(refs) is str: 
      refs = row[1]['LBA SYS'].split('\n')
    elif type(refs) is float or type(refs) is int:
      refs = [refs]
    while len(refs) > 0:
      ref = refs.pop()
      if (not pd.isna(ref) and type(ref) is float) or (type(ref) is str and ref.isdigit()):
        ref = int(ref)
        if ref > sys_max_id:
          print("HLR " + str(hlr_num) + " references invalid sys req: " + str(ref))
        else:
          sys_req_references[ref].append(hlr_num)

  # for sys in sys_req_references:
  #   print(', '.join(sys))
  # for sys_req in sys_reqs:
  #   print('SYS-' + str(sys_req[0]) + ': ' + str(sys_req[1]))
  if output_uncovered_sys:
    for req in sys_reqs:
      if len(sys_req_references[req[0]]) == 0:
        print('SYS-' + str(req[0]))
  else:
    for req in sys_reqs:
      print('------------'*15)
      print('SYS-' + str(req[0]))# + ": " + str(req[1]))
      for hlr_ref in sys_req_references[req[0]]:
        print('---------------')
        print('HLR-' + str(hlr_ref))# + ': ' + hlrs[hlr_ref])
      print('')

#########################################################
#                           Main
#########################################################
if __name__ == "__main__":
  main(sys.argv[1:])
