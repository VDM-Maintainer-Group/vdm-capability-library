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
        CONFIGURE_COMMAND pip3 install maturin
        BUILD_IN_SOURCE true
        BUILD_ALWAYS false
        BUILD_COMMAND maturin build --release --manylinux off --out ${CMAKE_CURRENT_BINARY_DIR}
        INSTALL_COMMAND "" #pip3 install -U ${CMAKE_CURRENT_BINARY_DIR}/*linux*.whl
        TEST_COMMAND "" #cargo test
        LOG_BUILD ON)
