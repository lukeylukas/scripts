# doStuff.py

import os, io, argparse, re, sys

def main(argv):
  # Create the argument parser
  parser = argparse.ArgumentParser(description='Example Argument Parser')
  # Add the modules directory option
  parser.add_argument('--srcDir', help='Source directory')
  # Parse the arguments
  args = parser.parse_args()
  # Access the values of the options
  if args.srcDir:
    srcDirectory = args.srcDir + '/'
  else:
    print('no source directory given (--srcDir)')
    sys.exit()
  # walk through all files in the top directory recursively
  for (dirpath, dirnames, filenames) in os.walk(srcDirectory):
    for name in filenames:
      if name[-2:] == '.c' or name[-4:] == '.asm' or name[-4:] == '.icf' or name[-2:] == '.s':
        # get the file text
        fileText = GetFileText(dirpath + '/' + name)
        print('Working in ' + dirpath + '/' + name)
        # perform the desired operation(s)
        newText = UpdateFileText(fileText)
        WriteToFile(dirpath + '/' + name, newText)
        # break
    # break
        
def GetFileText( fileName ):
  file = open(fileName, "r")
  fileText = file.read()
  file.close()
  return fileText

def UpdateFileText( fileText ):
  newText = fileText
  tempText = DoStuff(newText)
  if tempText:
    newText = tempText
  return newText

def DoStuff( fileText ):
  return fileText
  # sample action below
  # return re.sub(r'HLR:[\s\w\-\,]*A429 Library:', 'HLR: \nA429 Library:', fileText)
  # do whatever here

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
