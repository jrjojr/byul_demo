#ifndef DSTAR_LITE_UTILS_H
#define DSTAR_LITE_UTILS_H

#include "byul_config.h"
#include "internal/core.h"
#include "internal/map.h"
#include "internal/coord.h"
#include "internal/route.h"
#include "internal/dstar_lite.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief g_table에 저장된 모든 좌표의 g 값을 출력합니다.
 *
 * @param m        맵 객체
 * @param g_table  좌표별 g값을 저장한 GHashTable
 */
BYUL_API void print_all_g_table_internal(const map m, GHashTable* g_table);

/**
 * @brief rhs_table에 저장된 모든 좌표의 rhs 값을 출력합니다.
 *
 * @param m         맵 객체
 * @param rhs_table 좌표별 rhs값을 저장한 GHashTable
 */
BYUL_API void print_all_rhs_table_internal(
    const map m, GHashTable* rhs_table);

/**
 * @brief D* Lite 내부 상태를 상세하게 출력합니다.
 *
 * 모든 테이블과 주요 변수들을 포함한 전체 상태를 출력하며,
 * 디버깅 목적에 적합합니다.
 *
 * @param m           맵 객체
 * @param start       시작 좌표
 * @param goal        도착 좌표
 * @param km          현재까지 이동한 km 값
 * @param g_table     g 값 테이블
 * @param rhs_table   rhs 값 테이블
 * @param frontier    우선순위 큐
 * @param max_range   탐색 허용 범위
 * @param real_loop_max_retry   최대 재시도 횟수
 * @param debug_mode_enabled 디버그 모드 활성화 여부
 * @param update_count_table update_vertex 호출 횟수 테이블
 */
BYUL_API void print_all_dsl_internal_full(
    const map m,
    const coord start,
    const coord goal,
    gfloat km,
    GHashTable* g_table,
    GHashTable* rhs_table,
    dstar_lite_pqueue frontier,
    gint max_range,
    gint real_loop_max_retry,
    gboolean debug_mode_enabled,
    GHashTable* update_count_table);

/**
 * @brief D* Lite 내부 상태를 간략하게 출력합니다.
 *
 * km, g/rhs 테이블, 우선순위 큐 정보만 출력됩니다.
 *
 * @param m         맵 객체
 * @param start     시작 좌표
 * @param goal      도착 좌표
 * @param km        현재 km 값
 * @param g_table   g 테이블
 * @param rhs_table rhs 테이블
 * @param frontier  우선순위 큐
 */
BYUL_API void print_all_dsl_internal(
    const map m, const coord start, const coord goal,
    gfloat km, GHashTable* g_table, GHashTable* rhs_table,
    dstar_lite_pqueue frontier);

/**
 * @brief dstar_lite 객체의 상태를 출력합니다.
 *
 * 내부 모든 정보 출력. 디버깅용.
 *
 * @param dsl dstar_lite 객체
 */
BYUL_API void print_all_dsl(const dstar_lite dsl);

/**
 * @brief 맵을 단순 ASCII 형태로 출력합니다.
 *
 * 차단된 좌표는 `#`, 통과 가능한 좌표는 `.`으로 출력됩니다.
 *
 * @param m 맵 객체
 */
BYUL_API void dsl_print_ascii_only_map(const dstar_lite dsl);

/**
 * @brief 경로와 시작/도착 지점을 포함하여 맵을 출력합니다.
 *
 * - `#`: 장애물
 * - `.`: 일반 셀
 * - `*`: 경로 셀
 * - `S`: 시작 지점
 * - `E`: 도착 지점
 *
 * @param dsl   D* Lite 객체
 * @param p     경로 객체 (성공한 경우만 유효)
 */
BYUL_API void dsl_print_ascii(const dstar_lite dsl, const route p);

/**
 * @brief update_vertex 호출 횟수를 포함한 ASCII 맵 출력
 *
 * 각 셀에 대해 다음 중 하나로 출력됩니다:
 * - `S`: 시작 지점
 * - `E`: 도착 지점
 * - `*`: 경로 셀
 * - `#`: 장애물
 * - ` . `: 업데이트된 적 없는 셀
 * - 정수: update_vertex 호출 횟수 (최대 2자리)
 *      debug_mode_enabled 가 FALSE이면 호출 횟수는 출력하지 않습니다.
 *
 * @param dsl D* Lite 객체
 * @param p   경로 객체 (NULL 허용)
 */
BYUL_API void dsl_print_ascii_uv(const dstar_lite dsl, const route p);

#ifdef __cplusplus
}
#endif

#endif // DSTAR_LITE_UTILS_H
