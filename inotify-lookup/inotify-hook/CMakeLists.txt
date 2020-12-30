cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)
##
project(vdm-inotify-hook VERSION 0.1.0)
execute_process(COMMAND uname -r OUTPUT_VARIABLE KERNVER
                OUTPUT_STRIP_TRAILING_WHITESPACE)
set(KDIR "/lib/modules/${KERNVER}/build")
set(INSTALL_DIRECTORY "/lib/modules/${KERNVER}/updates")
# failure check
find_file(kernel_makefile NAMES Makefile
            PATHS ${KDIR} NO_DEFAULT_PATH)
if(NOT kernel_makefile)
    message(FATAL_ERROR "There is no Makefile in ${KDIR}!")
endif()

## directly call the Kbuild
set(DRIVER_FILE inotify_hook.ko)
set(KBUILD_CMD $(MAKE) -C ${KDIR} modules M=${CMAKE_CURRENT_BINARY_DIR} src=${CMAKE_CURRENT_SOURCE_DIR})
# add custom command/target
add_custom_command(OUTPUT ${DRIVER_FILE}
        COMMAND ${KBUILD_CMD}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        DEPENDS main.c netlink_comm.c VERBATIM)
add_custom_target(module ALL DEPENDS ${DRIVER_FILE}) #default
add_custom_target(module-clean COMMAND ${KBUILD_CMD} clean)  #clean
add_custom_target(insmod COMMAND sudo insmod ${DRIVER_FILE}) #test insmod
add_custom_target(rmmod COMMAND sudo rmmod ${DRIVER_FILE})
# install kernel module
INSTALL(FILES ${DRIVER_FILE}
        DESTINATION ${INSTALL_DIRECTORY})