#ifndef BYUL_CONFIG_H
#define BYUL_CONFIG_H

#include <glib.h>

// 플랫폼 감지
#if defined(_WIN32) || defined(_WIN64)
  #define BYUL_PLATFORM_WINDOWS 1
#else
  #define BYUL_PLATFORM_WINDOWS 0
#endif

#if defined(__linux__)
  #define BYUL_PLATFORM_LINUX 1
#else
  #define BYUL_PLATFORM_LINUX 0
#endif

#if defined(__APPLE__)
  #define BYUL_PLATFORM_MACOS 1
#else
  #define BYUL_PLATFORM_MACOS 0
#endif

// 정적 라이브러리 여부 감지
#if defined(BYUL_STATIC)
  #define BYUL_API
#else
  // DLL Export 설정
  #if BYUL_PLATFORM_WINDOWS
    #ifdef BYUL_EXPORTS
      #define BYUL_API __declspec(dllexport)
    #else
      #define BYUL_API __declspec(dllimport)
    #endif
  #else
    #define BYUL_API __attribute__((visibility("default")))
  #endif
#endif

// 버전 정보
#define BYUL_VERSION_MAJOR 0
#define BYUL_VERSION_MINOR 1
#define BYUL_VERSION_PATCH 0
#define BYUL_VERSION "0.1.0"

// 디버그 여부
#ifdef DEBUG
  #define BYUL_DEBUG 1
#else
  #define BYUL_DEBUG 0
#endif

// 문자열 매크로
#define BYUL_STRINGIFY(x) #x
#define BYUL_TOSTRING(x) BYUL_STRINGIFY(x)

// 디버깅 출력
#if BYUL_DEBUG
  #define DBG_PRINT(...) g_print(__VA_ARGS__)
#else
  #define DBG_PRINT(...) ((void)0)
#endif

#endif // BYUL_CONFIG_H
