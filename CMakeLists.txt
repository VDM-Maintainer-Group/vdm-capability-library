cmake_minimum_required(VERSION 3.10)
##
project(vdm-capability-library VERSION 0.1.1)
set(INSTALL_DIRECTORY "vdm/capability")

## Global configurations
include(JSONParser.cmake)
include(ExternalProject)
option(ENABLE_BINARIES_BUILD "Build capability example binaries" OFF)

## build capability wrapper
add_subdirectory("__wrapper__")

## Inotify Lookup Library
option(ENABLE_INOTIFY_LOOKUP "Enalbe Library Inotify-Lookup" ON)
if(ENABLE_INOTIFY_LOOKUP)
    add_subdirectory("inotify-lookup")
endif(ENABLE_INOTIFY_LOOKUP)

#add_subdirectory("window-helper")
#add_subdirectory("browser-helper")
#add_subdirectory("system-tweaker")
