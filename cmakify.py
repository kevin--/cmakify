#!/usr/bin/env python3

###
### cmakify
### Kevin Dixon
### 11/05/2016
###

kCMakeListsFile = "CMakeLists.txt"

kHeaderKey = "headers"
kSourceKey = "source"
kCMakeListsKey = "cmake"

def getArgs():
    import argparse
    parser = argparse.ArgumentParser(description="cmakify is used to generate a starting point for a CMake-based configuration of a pre-existing source tree.")
    parser.add_argument('path', help="the working path to generate CMakeLists.txt for")
    parser.add_argument('-f', '--flat', action='store_true', help="when specified, all directives will be placed in <path>/CMakeLists.txt. If not specified, a CMakeLists.txt will be placed in every subdirectory")
    parser.add_argument('--target-per-dir', action='store_true', help="when specified, each directory will be treated as a target")
    parser.add_argument('--target-type', choices=["executable", "library"], help="when set, overrides the target type selection.")
    parser.add_argument('--header', nargs='*', default=['h','hpp','in'], help="specify the file extension(s) for header files.")
    parser.add_argument('--source', nargs='*', help="when set, specifies the source file extension(s). By default, everything that is not a header is considered")
    parser.add_argument('--project', help="the name of the project for CMake. If not set, the path's directory name will be used.")
    parser.add_argument('--ignore-dirs', nargs='*', default=['*.framework', 'lib', 'libs', 'bin'], help="ignore directories matching the specified pattern(s)")

    return parser.parse_args()

def endsWithExtension(filename, extensionList):
    basefilepath, extension = os.path.splitext(filename)
    for x in extensionList:
        dotX = "."+x
        if dotX == extension:
            return True

    return False

def isHeader(args, filename):
    return endsWithExtension(filename, args.header)

def isSource(args, filename):
    if 'source' in args and args.source != None:
            return endsWithExtension(filename, args.source)
    return True

def isCmakeLists(filename):
    return filename == kCMakeListsFile

def verifyDictPath(inOutDirectoryContents, categoryKey, root, cwd):
    if not categoryKey in inOutDirectoryContents:
        inOutDirectoryContents[categoryKey] = {}

    if not root in inOutDirectoryContents[categoryKey]:
        inOutDirectoryContents[categoryKey][root] = {}

    if not cwd in inOutDirectoryContents[categoryKey][root]:
        inOutDirectoryContents[categoryKey][root][cwd] = []

def addToDict(inOutDirectoryContents, categoryKey, root, cwd, filename):
    verifyDictPath(inOutDirectoryContents, categoryKey, root, cwd)
    inOutDirectoryContents[categoryKey][root][cwd].append(filename)

def collectFile(inOutDirectoryContents, args, root, cwd, filename):
    if isCmakeLists(filename):
        addToDict(inOutDirectoryContents, kCMakeListsKey, root, cwd, filename)
    elif isHeader(args, filename):
        addToDict(inOutDirectoryContents, kHeaderKey, root, cwd, filename)
    elif isSource(args, filename):
        addToDict(inOutDirectoryContents, kSourceKey, root, cwd, filename)

def ignoreDirectory(args, directoryname):
    import fnmatch
    if 'ignore_dirs' in args and args.ignore_dirs != None:
        for pattern in args.ignore_dirs:
            if fnmatch.fnmatch(directoryname, pattern):
                return True
    return False

def collectSourceFiles(inOutDirectoryContents, args, root, cwd, recurse):
    import os
    
    normCwd = os.path.normpath(cwd)

    if os.path.exists(os.path.join(root, normCwd, kCMakeListsFile)):
        collectFile(inOutDirectoryContents, args, root, cwd, kCMakeListsFile)
        return

    for d in os.scandir(os.path.join(root, normCwd)):

        if d.name.startswith('.'):
            continue

        if d.is_file():
            collectFile(directoryContents, args, root, cwd, d.name)
         
        elif d.is_dir() and recurse and not ignoreDirectory(args, d.name):
            if(args.flat):
                nextRoot = os.path.normpath(os.path.join(root, cwd))
                nextCwd = d.name
            else:
                nextRoot = root
                nextCwd = os.path.normpath(os.path.join(cwd, d.name))

            collectSourceFiles(directoryContents, args, nextRoot, nextCwd, True)


if __name__ == '__main__':

    args = getArgs()

    import os

    if not os.path.isdir(args.path):
        raise IOError('path '+args.path+' is not a directory!')

    root = os.path.normpath(args.path)


    directoryContents = {}
    collectSourceFiles(directoryContents, args, root, '.', True)

    import pprint
    pprint.pprint(directoryContents)







