cmake_minimum_required(VERSION 3.5)

project(dummy LANGUAGES C CXX)

find_package(ZLIB REQUIRED)

add_executable(main_c main.c)
target_link_libraries(main_c PRIVATE ZLIB::ZLIB)

add_subdirectory(sub1)
