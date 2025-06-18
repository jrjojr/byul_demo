cmake_minimum_required(VERSION 3.10)

# Project name
project(core C)

# GLib 설정
find_package(PkgConfig REQUIRED)
pkg_check_modules(GLIB REQUIRED glib-2.0)

# 소스 파일 설정
set(SOURCES
    ${PROJECT_NAME}.c
)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# 스태틱 라이브러리 생성
add_library(${PROJECT_NAME} STATIC ${PROJECT_NAME}.c)

# 헤더 파일 디렉토리 추가
target_include_directories(${PROJECT_NAME} PUBLIC
    ${GLIB_INCLUDE_DIRS}
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_BINARY_DIR}/include/routefinder
)

target_link_libraries(${PROJECT_NAME} PUBLIC
    ${GLIB_LIBRARIES}
)

target_compile_definitions(${PROJECT_NAME} PRIVATE ${GLIB_CFLAGS_OTHER})
target_compile_options(${PROJECT_NAME} PRIVATE ${GLIB_CFLAGS_OTHER})

add_subdirectory(tests)

target_compile_definitions(${PROJECT_NAME} PRIVATE BYUL_STATIC)