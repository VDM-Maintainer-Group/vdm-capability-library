project(Package serde_wrapper_test)
cmake_minimum_required(VERSION 3.0)

include_directories("include")
add_executable(test test.cpp)

enable_testing()
add_test(NAME test
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
        COMMAND test
)
