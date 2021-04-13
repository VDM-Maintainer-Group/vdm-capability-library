cmake_minimum_required(VERSION 3.10) #for FindPython feature
##
project(vdm-inotify-lookup VERSION 0.2.0)
# set(INSTALL_DIRECTORY "vdm/capability")

## build kernel module of inotify capability
add_subdirectory("inotify-hook")

include(ExternalProject)
ExternalProject_Add(
        inotify-lookup
        DOWNLOAD_COMMAND ""
        CONFIGURE_COMMAND "pip3 install maturin"
        BUILD_COMMAND maturin build COMMAND maturin build --release
        BINARY_DIR "${CMAKE_SOURCE_DIR}"
        INSTALL_COMMAND "" #${CMAKE_SOURCE_DIR}target/wheels/*.whl
        TEST_COMMAND cargo test
        LOG_BUILD ON)

## build userspace library of inotify capability
add_library(vdm-inotify-lookup SHARED inotify_lookup.c)
set_target_properties(vdm-inotify-lookup PROPERTIES
                    PUBLIC_HEADER "inotify_lookup.h;")
# configure_file(cmake/VDMInotifyLookupConfig.cmake
                # ${CMAKE_CURRENT_BINARY_DIR}/VDMInotifyLookupConfig.cmake)
INSTALL(TARGETS vdm-inotify-lookup
        LIBRARY DESTINATION lib/${INSTALL_DIRECTORY}
        PUBLIC_HEADER DESTINATION include/${INSTALL_DIRECTORY})
# INSTALL(FILES ${CMAKE_CURRENT_BINARY_DIR}/VDMInotifyLookupConfig.cmake
        # DESTINATION lib/cmake/VDMInotifyLookup)

## build userspace application
if(ENABLE_BINARIES_BUILD)
    add_executable(test-example example.c)
    target_link_libraries(test-example PUBLIC vdm-inotify-lookup)
    #INSTALL(TARGETS test-example DESTINATION bin)
endif(ENABLE_BINARIES_BUILD)
