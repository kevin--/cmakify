#!/usr/bin/env python3

global kCMakeListsFile
kCMakeListsFile = "CMakeLists.txt"

global kHeaderKey
kHeaderKey = "headers"
global kSourceKey
kSourceKey = "source"
global kDirectoryKey
kDirectoryKey = "dir"
global kCMakeListsKey
kCMakeListsKey = "cmake"

global kTargetType_Executable
kTargetType_Executable = "executable"
global kTargetType_Library
kTargetType_Library = "library"

global kFileEntryMacro
kFileEntryMacro = "list(APPEND {0} {1})"

global kExcludeDirectoryList
kExcludeDirectoryList = ['*.framework', 'lib', 'libs', 'bin', 'doc', '*.xcodeproj', '*.xcassets']

global kExcludeFileList
kExcludeFileList = ['*.sln', '*.vcproj', '*.vcxproj*', 'Makefile*', '*.lproj', '*.a', '*.dll', '*.lib', '*.exe', '*.dylib']
