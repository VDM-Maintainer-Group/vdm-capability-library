cmake_minimum_required(VERSION 3.10)
##
project(vdm-capability-library VERSION 0.1.1)
set(INSTALL_DIRECTORY "vdm/capability")

## Global configurations
include(JSONParser.cmake)
include(ExternalProject)
option(ENABLE_BINARIES_BUILD "Build capability example binaries" OFF)
#
function(read_manifest in_folder_name out_manifest)
    file(STRINGS ${in_folder_name}/manifest.json manifest-json)
    sbeParseJson(manifest manifest-json)
    set(${out_manifest} manifest PARENT_SCOPE)
endfunction()

## build capability wrapper
add_subdirectory("__wrapper__")

## Inotify Lookup Library
option(ENABLE_INOTIFY_LOOKUP "Enalbe Library Inotify-Lookup" ON)
if(ENABLE_INOTIFY_LOOKUP)
    add_subdirectory("inotify-lookup")
    # read_manifest("inotify-lookup" inotify-manifest)
    # ExternalProject_add(
    #     inotify-Lookup
    # )
endif(ENABLE_INOTIFY_LOOKUP)

#add_subdirectory("window-helper")
#add_subdirectory("browser-helper")
#add_subdirectory("system-tweaker")
