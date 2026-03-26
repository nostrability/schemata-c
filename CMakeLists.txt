cmake_minimum_required(VERSION 3.14)
project(schemata-c LANGUAGES C VERSION "0.1.0")

set(CMAKE_C_STANDARD 99)

add_library(schemata STATIC src/schemata.c)
target_include_directories(schemata PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

option(SCHEMATA_BUILD_TESTS "Build tests" ON)

if (SCHEMATA_BUILD_TESTS)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(CMOCKA REQUIRED cmocka)

    enable_testing()
    add_executable(test_registry tests/test_registry.c)
    target_link_libraries(test_registry PRIVATE schemata ${CMOCKA_LIBRARIES})
    target_include_directories(test_registry PRIVATE ${CMOCKA_INCLUDE_DIRS})
    target_link_directories(test_registry PRIVATE ${CMOCKA_LIBRARY_DIRS})
    add_test(NAME test_registry COMMAND test_registry)
endif()

install(TARGETS schemata EXPORT schemata-targets
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)
install(DIRECTORY include/schemata DESTINATION include)
install(EXPORT schemata-targets
    FILE schemata-config.cmake
    DESTINATION lib/cmake/schemata
)
