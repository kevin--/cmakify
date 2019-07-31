#!/usr/bin/env python3

###
### cmakify
### Kevin Dixon
### 11/05/2016
###

import constants
import source_collector
import cmake_generator

import pprint
import os

def getArgs():
    import argparse
    parser = argparse.ArgumentParser(description="cmakify is used to generate a starting point for a CMake-based configuration of a pre-existing source tree.")
    parser.add_argument('path', help="the working path to generate CMakeLists.txt for")
    parser.add_argument('--target-per-dir', action='store_true', help="when specified, each directory will be treated as a target, and a CMakeLists.txt will be placed in each directory.")
    parser.add_argument('--target-type', choices=[constants.kTargetType_Executable, constants.kTargetType_Library], help="when set, overrides the target type selection.")
    parser.add_argument('--header', nargs='*', default=constants.kDefaultHeaderExtensions, help="specify the file extension(s) for header files.")
    parser.add_argument('--source', nargs='*', help="when set, specifies the source file extension(s). By default, everything that is not a header is considered")
    parser.add_argument('--project', help="the name of the project for CMake. If not set, the path's directory name will be used. targets will be generated in the format of \"<project>-<dir>\"")
    parser.add_argument('-xd', '--exclude-dir', nargs='*', action='append', default=constants.kExcludeDirectoryList, help="ignore directories matching the specified pattern(s).")
    parser.add_argument('-xf', '--exclude-file', nargs='*', action='append', default=constants.kExcludeFileList, help="ignore files matching the specified pattern(s).")
    parser.add_argument('--file-macro', default=constants.kFileEntryMacro, help="for each file to be added, use this macro for the line in the generated CMakeLists.txt. {0} is replaced with the variable, {1} is the current file. DEFAULT IS: \""+constants.kFileEntryMacro+"\"")
    parser.add_argument('--file-with-header-macro', help="if specified, and a source file has a matching header file in the directory, this macro will be used instead of file-macro. Same syntax, but with the addition of {2} which is the header file. In addition, the header file will not be included in a separate directive.")
    parser.add_argument('--no-recurse', action='store_false', dest='recurse', help="specify to disable directory recursion. disables --target-per-dir")
    parser.add_argument('--dump-sources', action='store_true', help="specify to dump the gathered source information to stdout, and does not generate any CMakeLists.txt (dry run)")

    return parser.parse_args()

if __name__ == '__main__':

    args = getArgs()


    if not os.path.isdir(args.path):
        raise IOError('path '+args.path+' is not a directory!')

    root = os.path.normpath(args.path)

    directoryContents = {}
    source_collector.collectSourceFiles(directoryContents, args, root, '.', args.recurse)

    if args.dump_sources:
        pprint.pprint(directoryContents)
    else:
        cmake_generator.writeAll(args, directoryContents, root)
