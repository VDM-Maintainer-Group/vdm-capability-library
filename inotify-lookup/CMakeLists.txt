cmake_minimum_required(VERSION 3.12) #for FindPython feature
##
project(vdm-inotify-lookup VERSION 0.1.0)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)
# set(INSTALL_DIRECTORY "vdm/capability")
## Find the library
find_package(PkgConfig REQUIRED)

## build kernel module of inotify capability
add_subdirectory("inotify-hook")


## build userspace library of inotify capability
# file(GLOB DAEMON_API "./*.h")
add_library(vdm-inotify-lookup SHARED inotify_lookup.c)
set_target_properties(vdm-inotify-lookup PROPERTIES
                    PUBLIC_HEADER "inotify_lookup.h;")
configure_file(cmake/VDMInotifyLookupConfig.cmake
                ${CMAKE_CURRENT_BINARY_DIR}/VDMInotifyLookupConfig.cmake)
INSTALL(TARGETS vdm-inotify-lookup
        LIBRARY DESTINATION lib/${INSTALL_DIRECTORY}
        PUBLIC_HEADER DESTINATION include/${INSTALL_DIRECTORY})
INSTALL(FILES ${CMAKE_CURRENT_BINARY_DIR}/VDMInotifyLookupConfig.cmake
        DESTINATION lib/cmake/${INSTALL_DIRECTORY})

## build userspace application
if(CONFIG_BUILD_BINARIES)
    add_executable(test-example example.c)
    target_link_libraries(test-example PUBLIC vdm-inotify-lookup)
    #INSTALL(TARGETS test-example DESTINATION bin)
endif(CONFIG_BUILD_BINARIES)
