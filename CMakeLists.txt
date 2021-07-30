cmake_minimum_required(VERSION 3.10)
##
project(vdm-capability-library VERSION 0.1.1)
set(INSTALL_DIRECTORY "vdm/capability")

include(ExternalProject)
ExternalProject_Add(
    capability-library
    SOURCE_DIR ${PROJECT_SOURCE_DIR}
    CONFIGURE_COMMAND pip3 install halo
    BUILD_IN_SOURCE true
    BUILD_ALWAYS true
    BUILD_COMMAND python3 build.py build
    INSTALL_COMMAND "" #python3 build.py install
    TEST_COMMAND "" #python3 build.py test
    LOG_BUILD ON
)

## Inotify Lookup Library
option(ENABLE_INOTIFY_LOOKUP "Enalbe Library Inotify-Lookup" ON)
if(ENABLE_INOTIFY_LOOKUP)
    add_subdirectory("inotify-lookup")
endif(ENABLE_INOTIFY_LOOKUP)
