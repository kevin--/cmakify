#!/usr/bin/env python3

import constants

def endsWithExtension(filename, extensionList):
    import os
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
    return filename == constants.kCMakeListsFile

def verifyDictPath(inOutDirectoryContents, categoryKey, root, cwd):
    if not root in inOutDirectoryContents:
        inOutDirectoryContents[root] = {}

    if not cwd in inOutDirectoryContents[root]:
        inOutDirectoryContents[root][cwd] = {}

    if not categoryKey in inOutDirectoryContents[root][cwd]:
        inOutDirectoryContents[root][cwd][categoryKey] = []

def addToDict(inOutDirectoryContents, categoryKey, root, cwd, filename):
    verifyDictPath(inOutDirectoryContents, categoryKey, root, cwd)
    inOutDirectoryContents[root][cwd][categoryKey].append(filename)

def filenameMatchesMaskList(filename, masklist):
    import fnmatch
    for pattern in masklist:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False

def ignoreFile(args, filename):
    if 'exclude_file' in args and args.exclude_file != None:
        return filenameMatchesMaskList(filename, args.exclude_file)
    return False

def ignoreDirectory(args, directoryname):
    if 'exclude_dir' in args and args.exclude_dir != None:
        return filenameMatchesMaskList(directoryname, args.exclude_dir)
    return False

def collectFile(inOutDirectoryContents, args, root, cwd, filename):

    if ignoreFile(args, filename):
        return

    if isCmakeLists(filename):
        addToDict(inOutDirectoryContents, constants.kCMakeListsKey, root, cwd, filename)
    elif isHeader(args, filename):
        addToDict(inOutDirectoryContents, constants.kHeaderKey, root, cwd, filename)
    elif isSource(args, filename):
        addToDict(inOutDirectoryContents, constants.kSourceKey, root, cwd, filename)

def collectSourceFiles(inOutDirectoryContents, args, root, cwd, recurse):
    import os
    
    normCwd = os.path.normpath(cwd)

    if os.path.exists(os.path.join(root, normCwd, constants.kCMakeListsFile)):
        collectFile(inOutDirectoryContents, args, root, cwd, constants.kCMakeListsFile)
        return

    for d in os.scandir(os.path.join(root, normCwd)):

        if d.name.startswith('.'):
            continue

        if d.is_file():
            collectFile(inOutDirectoryContents, args, root, cwd, d.name)
         
        elif d.is_dir() and recurse and not ignoreDirectory(args, d.name):
            addToDict(inOutDirectoryContents, constants.kDirectoryKey, root, cwd, d.name)
            nextCwd = os.path.normpath(os.path.join(cwd, d.name))
            collectSourceFiles(inOutDirectoryContents, args, root, nextCwd, True)
