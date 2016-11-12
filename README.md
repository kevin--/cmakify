# cmakify #

**cmakify** is used to generate a starting point for a CMake-based configuration of a pre-existing source tree.

In the case where you are fine with globbing your files, then this tool probably isn't for you, but if you're looking for some kind of glorified `sed`, then here you go.

There are two main options; with no argument specified, a single top-level `CMakeLists.txt` is generated. The other is `--target-per-dir` wherein a `CMakeLists.txt` will be generated for every directory in the tree you specify. This is recommended if your source is already modularized into directories.

Of course, **cmakify** is not smart, so it is up to you to define target relationships, etc, after you generate the basic file lists.

# Source Tree Walking Behavior #

The first argument is the root of your source tree. By default, sources in all sub-folders are gathered, and a flat top-level `CMakeLists.txt` is generated that includes all source in a single executable target.

There are a few rules that guide this.

1. Headers are determined by the header extension list. The default is `h`, `hpp`, and `in`
2. Sources are everything else. An extension list can be specified if you want.
3. You can use the `--exclude-dir` and `--exclude-file` to exclude directories and files from consideration, respectively. (See below)
4. If any `CMakeLists.txt` are encountered in the tree, references are added to them via `add_subdirectory`

## Excluded stuff ##
The arguments `--exclude-dir` and `--exclude-file` allow you to set a list of `fnmatch` expressions that will be used to ignore things.

These are useful if you want to ignore certain directories of your project. There are some defaults baked in, which are listed below.

Be aware that `--exclude-dir` and `--exclude-file` override these lists, so you may want to re-include these.

*Alternatively, you could just edit `constants.py`*

### Default Exclusion Lists ###
- Hidden files and dirs (aka starting with ".")
- Directories
 - `*.framework`
 - `lib`
 - `libs`
 - `bin`
 - `doc`
 - `*.xcodeproj`
 - `*.xcassets`
- Files
 - `*.sln`
 - `*.vcproj`
 - `*.vcxproj`
 - `Makefile*`
 - `*.lproj`
 - `*.a`
 - `*.dll`
 - `*.lib`
 - `*.exe`
 - `*.dylib`

### Future Exclusion Work ###
It would be smart to have `-axd` and `-axf` or something to append the default exclusion lists

It would be smart to read `.gitignore` if present

# CMake Dialect and Generation Behavior #

**cmakify** will output `project`, `add_subdirectory`, `list`, `add_executable` and `add_library` directives.

## Target Types ##

`add_executable` is used for the top level project, and `add_library` is used for all subdirectories.
This behavior can be set to a single type using `--target-type`

## File Macros ##
You can control how the files are added to your `CMakeLists.txt` using the `--file-macro` and `--file-with-header-macro`.

### --file-macro ###
This is the normal use case. It defaults to `list(APPEND {0} {1})`, where
- `{0}` is substituted with a CMake variable
- `{1}` is substituted with the relative file path
You can override this if you have a preferred way of doing things

### --file-with-header-macro ###
This is a special case, and is undefined by default, which disables this behavor.

When a source file is encountered that has a matching header, and this macro is specified, then this macro will be used instead, *AND*, the header file will not be specified in any future directives.

The macro is the same as above, but adds
- `{2}` the relative path of the header file

Probably not for everyone, but if you already have some CMake macros you use for this use case, then you can apply this.

# Command Line #

try `./cmakify.py -h` to see this info:

    usage: cmakify.py [-h] [--target-per-dir] [--target-type {executable,library}]
                      [--header [HEADER [HEADER ...]]]
                      [--source [SOURCE [SOURCE ...]]] [--project PROJECT]
                      [-xd [EXCLUDE_DIR [EXCLUDE_DIR ...]]]
                      [-xf [EXCLUDE_FILE [EXCLUDE_FILE ...]]]
                      [--file-macro FILE_MACRO]
                      [--file-with-header-macro FILE_WITH_HEADER_MACRO]
                      [--no-recurse] [--dump-sources]
                      path
    
    cmakify is used to generate a starting point for a CMake-based configuration
    of a pre-existing source tree.
    
    positional arguments:
      path                  the working path to generate CMakeLists.txt for
    
    optional arguments:
      -h, --help            show this help message and exit
      --target-per-dir      when specified, each directory will be treated as a
                            target, and a CMakeLists.txt will be placed in each
                            directory.
      --target-type {executable,library}
                            when set, overrides the target type selection.
      --header [HEADER [HEADER ...]]
                            specify the file extension(s) for header files.
      --source [SOURCE [SOURCE ...]]
                            when set, specifies the source file extension(s). By
                            default, everything that is not a header is considered
      --project PROJECT     the name of the project for CMake. If not set, the
                            path's directory name will be used. targets will be
                            generated in the format of "<project>-<dir>"
      -xd [EXCLUDE_DIR [EXCLUDE_DIR ...]], --exclude-dir [EXCLUDE_DIR [EXCLUDE_DIR ...]]
                            ignore directories matching the specified pattern(s).
      -xf [EXCLUDE_FILE [EXCLUDE_FILE ...]], --exclude-file [EXCLUDE_FILE [EXCLUDE_FILE ...]]
                            ignore files matching the specified pattern(s).
      --file-macro FILE_MACRO
                            for each file to be added, use this macro for the line
                            in the generated CMakeLists.txt. {0} is replaced with
                            the variable, {1} is the current file. DEFAULT IS:
                            "list(APPEND {0} {1})"
      --file-with-header-macro FILE_WITH_HEADER_MACRO
                            if specified, and a source file has a matching header
                            file in the directory, this macro will be used instead
                            of file-macro. Same syntax, but with the addition of
                            {2} which is the header file. In addition, the header
                            file will not be included in a separate directive.
      --no-recurse          specify to disable directory recursion. disables
                            --target-per-dir
      --dump-sources        specify to dump the gathered source information to
                            stdout
