cmake_minimum_required(VERSION 3.10)
##
project(vdm-capability-library VERSION 0.1.0)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(INSTALL_DIRECTORY "vdm/capability")
## Find the library
find_package(PkgConfig REQUIRED)

add_subdirectory("inotify-lookup")
#add_subdirectory("window-helper")
#add_subdirectory("browser-helper")
#add_subdirectory("system-tweaker")
