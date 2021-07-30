cmake_minimum_required(VERSION 3.10) #for FindPython feature
##
project(vdm-inotify-lookup VERSION 0.2.0)
# set(INSTALL_DIRECTORY "vdm/capability")

## build kernel module of inotify capability
add_subdirectory("inotify-hook")

include(ExternalProject)
ExternalProject_Add(
        inotify-lookup
        SOURCE_DIR ${PROJECT_SOURCE_DIR}
        CONFIGURE_COMMAND ""
        BUILD_IN_SOURCE true
        BUILD_ALWAYS false
        BUILD_COMMAND cargo build --release
        INSTALL_COMMAND ""
        TEST_COMMAND "" #cargo test
        LOG_BUILD ON)
