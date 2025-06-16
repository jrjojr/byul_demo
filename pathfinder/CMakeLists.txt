cmake_minimum_required(VERSION 3.10)

# Project name
project(pathfinder C)

enable_testing()

# 최상단 또는 프로젝트 선언 이후
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    add_definitions(-DDEBUG)
    message(STATUS "DEBUG mode enabled")
endif()

# 코드 인텔리센스에 도움이 된다 vscode에서...
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 중단점 디버깅 을위해 루트에 한번만 설정하면 된다.
set(CMAKE_C_FLAGS_DEBUG "-g -O0")

# uninstall 타겟 생성
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake.in
    ${CMAKE_BINARY_DIR}/cmake_uninstall.cmake
    IMMEDIATE @ONLY
)
add_custom_target(uninstall
    COMMAND ${CMAKE_COMMAND} -P ${CMAKE_BINARY_DIR}/cmake_uninstall.cmake
)

# GLib 설정
find_package(PkgConfig REQUIRED)
pkg_check_modules(GLIB REQUIRED glib-2.0)

# 빌드 디렉토리 설정
set(${PROJECT_NAME}_BUILD_INCLUDE_DIR 
    ${CMAKE_BINARY_DIR}/include/${PROJECT_NAME})

set(${PROJECT_NAME}_BUILD_INTERNAL_DIR 
    ${${PROJECT_NAME}_BUILD_INCLUDE_DIR}/internal)

set(${PROJECT_NAME}_BUILD_LIB_DIR ${CMAKE_BINARY_DIR}/lib)

file(MAKE_DIRECTORY ${${PROJECT_NAME}_BUILD_INTERNAL_DIR})
file(MAKE_DIRECTORY ${${PROJECT_NAME}_BUILD_LIB_DIR})

# 내부 헤더 복사 매크로
macro(copy_headers module)
    file(GLOB HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/${module}/*.h")
    foreach(hdr ${HEADERS})
        get_filename_component(hname ${hdr} NAME)
        file(COPY ${hdr} DESTINATION ${${PROJECT_NAME}_BUILD_INTERNAL_DIR})
    endforeach()
endmacro()

# 내부 모듈 추가
add_subdirectory(core)
add_subdirectory(coord)
add_subdirectory(map)
add_subdirectory(path)
add_subdirectory(pqueue)
add_subdirectory(dstar_lite)

# 각 모듈 헤더 복사
copy_headers(core)
copy_headers(coord)
copy_headers(map)
copy_headers(path)
copy_headers(pqueue)
copy_headers(dstar_lite)

# pathfinder.h 복사
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_NAME}.h 
    DESTINATION ${${PROJECT_NAME}_BUILD_INCLUDE_DIR})

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# 라이브러리 생성
add_library(${PROJECT_NAME} SHARED ${PROJECT_NAME}.c)

# include 경로 설정
target_include_directories(${PROJECT_NAME} PUBLIC
    ${GLIB_INCLUDE_DIRS}
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${${PROJECT_NAME}_BUILD_INCLUDE_DIR}
    ${${PROJECT_NAME}_BUILD_INTERNAL_DIR}
)

target_link_directories(${PROJECT_NAME} PRIVATE 
    ${GLIB_LIBRARY_DIRS}
    ${PROJECT_NAME}_BUILD_LIB_DIR
)

# 정적 라이브러리 통합 링크 (GNU/Clang 계열)
target_link_libraries(${PROJECT_NAME} PUBLIC
    ${GLIB_LIBRARIES}
    -Wl,--whole-archive
    coord map path dstar_lite
    -Wl,--no-whole-archive
)

target_compile_definitions(${PROJECT_NAME} PRIVATE ${GLIB_CFLAGS_OTHER})
target_compile_options(${PROJECT_NAME} PRIVATE ${GLIB_CFLAGS_OTHER})

# 빌드 후 pathfinder 라이브러리를 lib로 복사
add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${PROJECT_NAME}> 
    ${${PROJECT_NAME}_BUILD_LIB_DIR}/lib${PROJECT_NAME}.a
)

file(COPY byul_config.h DESTINATION ${${PROJECT_NAME}_BUILD_INCLUDE_DIR})

# 설치 설정
if (WIN32)
    set(HOME_DIR "$ENV{USERPROFILE}")
else()
    set(HOME_DIR "$ENV{HOME}")
endif()

set(CMAKE_INSTALL_PREFIX "${HOME_DIR}/byul_world" 
    CACHE PATH "Install path" FORCE)

install(TARGETS ${PROJECT_NAME}
    LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}/lib
    ARCHIVE DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/${PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}/bin
)

# ${PROJECT_NAME}_BUILD_INCLUDE_DIR 내부의 internal/ 
# 디렉토리 및 그 안의 .h 파일들도 모두 복사돼요.
install(DIRECTORY ${${PROJECT_NAME}_BUILD_INCLUDE_DIR}/
    DESTINATION ${CMAKE_INSTALL_PREFIX}/include
)

# pkg-config 설정
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/pathfinder.pc.in
               ${CMAKE_BINARY_DIR}/pathfinder.pc @ONLY)

message ("설치 디렉토리는 ${CMAKE_INSTALL_PREFIX} 이다")
install(FILES ${CMAKE_BINARY_DIR}/pathfinder.pc DESTINATION 
    ${CMAKE_INSTALL_PREFIX}/lib/pkgconfig)

target_compile_definitions(${PROJECT_NAME} PRIVATE BYUL_EXPORTS)

# add_subdirectory(tests)