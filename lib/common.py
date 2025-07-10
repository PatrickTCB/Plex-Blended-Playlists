import sys

def stringToFile(fileName, contentsRaw):
    contents = str(contentsRaw)
    with open(fileName, "w+") as output_file:
        output_file.write(contents)
        output_file.close()

def fileToString(fileName) :
    fileContents = ""
    with open(fileName, 'r') as myfile:
        fileContents = myfile.read()
    return str(fileContents)

def parseArgs(allArgs):
    adict = {}
    adict["v"] = False
    i = 1
    for arg in allArgs:
        if arg[0] == "-":
            try:
                adict[arg[1:]] = allArgs[i]
            except IndexError:
                adict[arg[1:]] = True
            except Exception as e:
                print("Couldn't parse {}.\n{}", arg, e)
                sys.exit(3)
        i = i + 1
    return adict