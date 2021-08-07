cmake_minimum_required(VERSION 3.0.0)
##
project(vdm-inotify-lookup VERSION 0.2.0)

## build kernel module of inotify capability
add_subdirectory("inotify-hook")
