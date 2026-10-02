cmake_minimum_required(VERSION 3.20)
project(byu-hpt-27-telemetry VERSION 0.1 LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

enable_testing()

include(FetchContent)

FetchContent_Declare(
    doctest
    GIT_REPOSITORY https://github.com/doctest/doctest.git
    GIT_TAG v2.5.3
)

FetchContent_MakeAvailable(doctest)

add_executable(hpt_tests
    tests/test_main.cpp
    src/hpt/data/sensor_check.cpp
)
target_include_directories(hpt_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)


target_link_libraries(hpt_tests PRIVATE
    doctest::doctest
)

add_test(NAME hpt_tests COMMAND hpt_tests)
