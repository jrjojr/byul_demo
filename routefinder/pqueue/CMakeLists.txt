cmake_minimum_required(VERSION 3.10)

# 프로젝트 이름과 언어 설정
project(pqueue C)

# glib 포함 디렉토리 추가
find_package(PkgConfig REQUIRED)
pkg_check_modules(GLIB REQUIRED glib-2.0)

# 소스 파일 설정
set(SOURCES
    ${PROJECT_NAME}.c
)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# 스태틱 라이브러리 생성
add_library(${PROJECT_NAME} STATIC ${SOURCES})

# 헤더 파일 디렉토리 추가
target_include_directories(${PROJECT_NAME} PRIVATE 
    ${GLIB_INCLUDE_DIRS}
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_BINARY_DIR}/include/routefinder
)

target_link_directories(${PROJECT_NAME} PRIVATE 
    ${GLIB_LIBRARY_DIRS}
    ${CMAKE_BINARY_DIR}/core
)

target_link_libraries(${PROJECT_NAME} PRIVATE 
    ${GLIB_LIBRARIES}
    core
    # m
)

# 컴파일러 플래그 추가
target_compile_options(${PROJECT_NAME} PRIVATE ${GLIB_CFLAGS_OTHER})

target_compile_definitions(${PROJECT_NAME} PRIVATE ${GLIB_CFLAGS_OTHER})

add_subdirectory(tests)

target_compile_definitions(${PROJECT_NAME} PRIVATE BYUL_STATIC)