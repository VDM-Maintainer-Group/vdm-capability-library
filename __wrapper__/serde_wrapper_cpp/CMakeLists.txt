project(Package CXX)
cmake_minimum_required(VERSION 3.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include_directories("include")
add_executable(wrapper_test test.cpp)

enable_testing()
add_test(NAME wrapper_test
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
        COMMAND wrapper_test
)
