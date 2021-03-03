cmake_minimum_required(VERSION 3.10)
##
project(vdm-capability-library VERSION 0.1.0)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(INSTALL_DIRECTORY "vdm/capability")

## Global Configurations
option(ENABLE_BINARIES_BUILD "Build capability example binaries" OFF)

## Inotify Lookup Library
option(ENABLE_INOTIFY_LOOKUP "Enalbe Library Inotify-Lookup" ON)
if(ENABLE_INOTIFY_LOOKUP)
    add_subdirectory("inotify-lookup")
endif(ENABLE_INOTIFY_LOOKUP)

#add_subdirectory("window-helper")
#add_subdirectory("browser-helper")
#add_subdirectory("system-tweaker")
