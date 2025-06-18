# CMakeLists.txt for the test project

cmake_minimum_required(VERSION 3.10)

# Set the project name
project(test_coord C)

# Link the test executable with the external flud library and glib
find_package(PkgConfig REQUIRED)
pkg_check_modules(GLIB REQUIRED glib-2.0)

# Add the test executable
add_executable(${PROJECT_NAME} ${PROJECT_NAME}.c)

# 컴파일·링크 옵션에 ASan 추가
# win11과 우분투는 다르다
if (CMAKE_SYSTEM_NAME MATCHES "Windows")
    message(STATUS 
    "${PROJECT_NAME} Applying ASan for Windows (no leak sanitizer)")

    target_compile_options(${PROJECT_NAME} PRIVATE
        -fsanitize=address
        -g
        -O1
    )
    target_link_options(${PROJECT_NAME} PRIVATE
        -fsanitize=address
    )
else()
    message(STATUS "${PROJECT_NAME} Applying ASan + LSan for Unix-like")
    target_compile_options(${PROJECT_NAME} PRIVATE
        -fsanitize=address
        -fsanitize=leak
        -g
        -O1
    )
    target_link_options(${PROJECT_NAME} PRIVATE
        -fsanitize=address
        -fsanitize=leak
    )
endif()

target_include_directories(${PROJECT_NAME} PRIVATE 
    ${GLIB_INCLUDE_DIRS}
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_BINARY_DIR}/include/routefinder
    )

# Ensure glib.h can be included
target_link_directories(${PROJECT_NAME} PRIVATE 
    ${GLIB_LIBRARY_DIRS}
    ${CMAKE_BINARY_DIR}/routefinder/coord
    )

# Link libraries
target_link_libraries(${PROJECT_NAME} PRIVATE 
    ${GLIB_LIBRARIES}
    coord
    )

target_compile_definitions(${PROJECT_NAME} PRIVATE ${GLIB_CFLAGS_OTHER})

# Add a test goal CTest
add_test(NAME AllTests COMMAND ${PROJECT_NAME})

target_compile_definitions(${PROJECT_NAME} PRIVATE BYUL_STATIC)
