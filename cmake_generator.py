#!/usr/bin/env python3

import constants
import os

def getRelativeFilename(args, cwd, filename):
    relFilename = filename
    if not args.target_per_dir and not args.recurse:
        relFilename = os.path.join(cwd, filename)
    return relFilename

def getFileEntry(args, variable, cwd, filename):
    return args.file_macro.format(variable, getRelativeFilename(args, cwd, filename))

def getFileWithHeaderEntry(args, variable, cwd, sourceFilename, headerFilename):
    source = getRelativeFilename(args, cwd, sourceFilename)
    header = getRelativeFilename(args, cwd, headerFilename)
    return args.file_with_header_macro.format(variable, source, header)

def writeFileEntryForCategory(args, directoryContents, root, cwd, category, variable, outputFile):
    if category in directoryContents[root][cwd]:
        for s in directoryContents[root][cwd][category]:
            outputFile.write(getFileEntry(args, variable, cwd, s) + "\n")

def findAndRemoveMatchingHeader(directoryContents, root, cwd, sourceFilename):
    workingSet = directoryContents[root][cwd]
    if not constants.kHeaderKey in workingSet:
        return None

    baseName = os.path.splitext(sourceFilename)[0] + "."
    foundHeader = None
    for h in workingSet[constants.kHeaderKey]:
        if h.startswith(baseName):
            foundHeader = h
            break

    if foundHeader != None:
        workingSet[constants.kHeaderKey].remove(foundHeader)

    return foundHeader

def writeFileEntryForSource(args, directoryContents, root, cwd, variable, outputFile):
    if args.file_with_header_macro == None:
        writeFileEntryForCategory(args, directoryContents, root, cwd, constants.kSourceKey, variable, outputFile)
        return

    category = constants.kSourceKey
    if category in directoryContents[root][cwd]:
        for s in directoryContents[root][cwd][category]:
            header = findAndRemoveMatchingHeader(directoryContents, root, cwd, s)
            if header == None:
                outputFile.write(getFileEntry(args, variable, cwd, s) + "\n")
            else:
                outputFile.write(getFileWithHeaderEntry(args, variable, cwd, s, header) + "\n")

def writeFileGroup(args, directoryContents, root, cwd, variable, outputFile):
    writeFileEntryForSource(args, directoryContents, root, cwd, variable, outputFile)
    writeFileEntryForCategory(args, directoryContents, root, cwd, constants.kHeaderKey, variable, outputFile)
    sourceGroupName = cwd.replace("/", "\\\\")
    outputFile.write("source_group(" + sourceGroupName + " FILES ${" + variable + "})\n")

def dirHasCMakeListsFile(directoryContents, root, cwd):
    if not root in directoryContents:
        return False
    if not cwd in directoryContents[root]:
        return False
    if constants.kCMakeListsKey in directoryContents[root][cwd]:
        return True
    return False

def isRootTarget(args, root, cwd):
    normRoot = os.path.normpath(root)
    normCwd = os.path.normpath(os.path.join(root, cwd))
    return normRoot == normCwd

def getProjectName(args, root):
    if args.project == None:
        return os.path.basename(os.path.abspath(root))
    else:
        return args.project

def getTargetName(args, root, cwd):
    targetName = None
    if isRootTarget(args, root, cwd):
        targetName = getProjectName(args, root)
    else:
        targetName = getProjectName(args, root) + "-" + os.path.basename(cwd)

    if targetName == None:
        raise Exception("failed to determine target name")

    return targetName

def getTargetMacro(args, root, cwd):
    targetType = None
    if args.target_type != None:
        targetType = args.target_type
    elif isRootTarget(args, root, cwd):
        targetType = constants.kTargetType_Executable
    else:
        targetType = constants.kTargetType_Library

    return "add_" + targetType + "({0} {1})"

def getTargetEntry(args, root, cwd, fileVariables):

    targetName = getTargetName(args, root, cwd)
    macro = getTargetMacro(args, root, cwd)

    resolvedFileVariables = []
    for v in fileVariables:
        resolvedFileVariables.append("${" + v + "}")

    return macro.format(targetName, " ".join(resolvedFileVariables))+'\n'

def getFilesVariableName(cwd):
    normCwd = os.path.normpath(cwd)
    normCwd = normCwd.replace(" ", "_")
    normCwd = normCwd.replace("-", "_")
    normCwd = normCwd.replace(".", "_")
    normCwd = normCwd.replace("/", "_")
    return "FILES_{0}".format(normCwd)

def writeCMakeLists_target(args, directoryContents, root, cwd, outputFile):

    variableName = getFilesVariableName(cwd)

    writeFileGroup(args, directoryContents, root, cwd, variableName, outputFile)
    outputFile.write(getTargetEntry(args, root, cwd, [variableName]))


def writeCMakeLists(args, directoryContents, root, cwd):
    localFile = os.path.normpath(os.path.join(root, cwd, kCMakeListsFile))
    with open(localFile, "w") as output:
        writeCMakeLists_target(args, directoryContents, root, cwd, output)

def shouldAddDirectoryToCMake(args, directoryContents, root, cwd):
    if not root in directoryContents:
        return False
    if not cwd in directoryContents[root]:
        return False
    dirContents = directoryContents[root][cwd]
    ## if it contains a CMakeLists already, or if it has source/header we will generate for
    shouldAdd = constants.kCMakeListsKey in dirContents
    if args.target_per_dir and not shouldAdd:
        shouldAdd = constants.kSourceKey in dirContents or constants.kHeaderKey in dirContents

    return shouldAdd

def writeAddSubdirectory(args, directoryContents, root, cwd, outputFile):

    if not constants.kDirectoryKey in directoryContents[root][cwd]:
        return

    for subdir in directoryContents[root][cwd][constants.kDirectoryKey]:
        cwdKey = os.path.normpath(os.path.join(cwd, subdir))
        if not cwdKey in directoryContents[root]:
            continue

        if shouldAddDirectoryToCMake(args, directoryContents, root, cwd):
            outputFile.write('add_subdirectory(' + os.path.basename(subdir) + ')\n')

def writeCMakeListsContent(args, directoryContents, root, cwd, outputFile):

    sourceGroups = []

    workingSet = directoryContents[root][cwd]

    writeAddSubdirectory(args, directoryContents, root, cwd, outputFile)
    outputFile.write('\n')

    if constants.kSourceKey in workingSet or constants.kHeaderKey in workingSet:
        var = getFilesVariableName(cwd)
        sourceGroups.append(var)
        writeFileGroup(args, directoryContents, root, cwd, var, outputFile)
        outputFile.write('\n')

    return sourceGroups

def writeProjectEntry(args, root, cwd, outputFile):
    outputFile.write("project(" + getTargetName(args, root, cwd) + ")\n\n")

def writeFlatCMakeLists(args, directoryContents, root):
    localFile = os.path.normpath(os.path.join(root, constants.kCMakeListsFile))
    with open(localFile, "w") as output:

        writeProjectEntry(args, root, '.', output)

        sourceGroups = []

        for cwd in directoryContents[root]:
            sourceGroups.extend(writeCMakeListsContent(args, directoryContents, root, cwd, output))

        output.write(getTargetEntry(args, root, '.', sourceGroups))

def writeRecursiveCMakeLists(args, directoryContents, root, cwd):

    workingSet = directoryContents[root][cwd]

    cmakelistFile = os.path.normpath(os.path.join(root, cwd, constants.kCMakeListsFile))
    with open(cmakelistFile, "w") as output:
        writeProjectEntry(args, root, cwd, output)
        sourceGroups = writeCMakeListsContent(args, directoryContents, root, cwd, output)
        output.write(getTargetEntry(args, root, cwd, sourceGroups))

    if constants.kDirectoryKey in workingSet:
        for directChild in workingSet[constants.kDirectoryKey]:
            childCwd = os.path.normpath(os.path.join(cwd, directChild))
            if shouldAddDirectoryToCMake(args, directoryContents, root, childCwd) and not dirHasCMakeListsFile(directoryContents, root, cwd):
                writeRecursiveCMakeLists(args, directoryContents, root, childCwd)

def writeAll(args, directoryContents, root):

    if not args.target_per_dir:
        writeFlatCMakeLists(args, directoryContents, root)
    else:
        writeRecursiveCMakeLists(args, directoryContents, root, '.')
