cmake_minimum_required(VERSION 3.19)

project(dummy LANGUAGES C)

find_package(ZLIB REQUIRED)

add_executable(main main.c)
target_link_libraries(main PRIVATE ZLIB::ZLIB)