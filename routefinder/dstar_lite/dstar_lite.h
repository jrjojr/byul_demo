// dstar_lite.h
//
// Copyright (c) 2025 별이아빠 (byuldev@outlook.kr)
// This file is part of the Byul World project.
// Licensed under the Byul World 공개 라이선스 v1.0
// See the LICENSE file for details.

/**
 * @file dstar_lite.h
 * @brief D* Lite 알고리즘 헤더
 *
 * 1. dstar_lite에 대한 고찰
 *    - 최초에 경로를 계산한 이후, 맵 상의 장애물이 동적으로 변경될 경우,
 *      경로를 빠르게 재탐색할 수 있도록 설계된 알고리즘입니다.
 *    - 이 재탐색을 위해 핵심적으로 사용되는 것이 update_vertex() 함수이며,
 *      장애물이 변경된 위치를 기준으로 일정 범위(max_range) 내 노드들을 갱신해야 합니다.
 *
 * 2. max_range 설정에 대한 실용적 기준 (by 별이엄마)
 *    - 적당한 max_range는 맵의 크기와 장애물 분포에 따라 달라질 수 있습니다.
 *    - 일반적으로 다음 기준을 참고할 수 있습니다:
 *
 *      ● 정적/큰 맵 (예: 100x100 이상)  → max_range = 10~20
 *      ● 중형 맵 (예: 50x50)           → max_range = 5~10
 *      ● 실시간/작은 맵 (예: 20x20 이하) → max_range = 3~5
 *
 *    - 공식적인 계산 방식은 없으나, 다음과 같은 근사치를 고려할 수 있습니다:
 *
 *        max_range ≈ ( |goal.x - start.x| + |goal.y - start.y| ) / 10
 *
 *      예를 들어 start=(0,0), goal=(40,40)라면 max_range ≈ 8
 *
 *    - 결국 최적값은 실험을 통해 조정해야 하며,
 *      너무 작으면 경로를 못 찾고, 너무 크면 계산량이 과도해질 수 있습니다.
 *
 *    - 별이엄마는 초기 설정값으로 10을 권장합니다.
 */

#ifndef DSTAR_LITE_H
#define DSTAR_LITE_H

#include "byul_config.h"
#include "internal/core.h"

#include "internal/map.h"
#include "internal/coord.h"
#include "internal/route.h"
#include "internal/dstar_lite_key.h"
#include "internal/dstar_lite_pqueue.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*move_func)(const coord c, gpointer userdata);

typedef GList* (*changed_coords_func)(gpointer userdata);

typedef gfloat (*dsl_cost_func)(
    const map m, const coord start, const coord goal, gpointer userdata);

typedef gfloat (*dsl_heuristic_func)(
    const coord start, const coord goal, gpointer userdata);

typedef gboolean (*dsl_is_blocked_func)(
    const map m, gint x, gint y, gpointer userdata);

typedef struct s_dstar_lite {
    // 맵
    map m;

    coord start;
    coord goal;

    gfloat km;
    GHashTable* g_table;    // coord* → gfloat*
    GHashTable* rhs_table;  // coord* → gfloat*
    
    // 탐색 프론티어 (우선순위 큐)
    dstar_lite_pqueue        frontier;

    // 비용 함수
    dsl_cost_func cost_fn;
    gpointer cost_fn_userdata;

    dsl_is_blocked_func is_blocked_fn;
    gpointer is_blocked_fn_userdata;

    // 휴리스틱 함수
    dsl_heuristic_func heuristic_fn;
    gpointer heuristic_fn_userdata;    

    // find 함수내에서 루프시에 실행될 move_fn
    move_func move_fn;
    gpointer move_fn_userdata;

    // find 함수내에서 루프시에 실행될 changed_coords_fn
    changed_coords_func changed_coords_fn;
    gpointer changed_coords_fn_userdata;

    // 초기 경로
    route proto_route;

    // 실제 실시간 장애물 반영 경로
    route real_route;

    // find()내에서 잠시 멈춤 실시간 이동시에 속도 대응
    gint interval_msec;

    gint real_loop_max_retry;

    gint compute_max_retry;

    gint reconstruct_max_retry;

    gint proto_compute_retry_count;

    gint real_compute_retry_count;

    gint real_loop_retry_count;

    gint reconstruct_retry_count;
    
    // 루프 강제 종료
    gboolean force_quit;
    
    // update_vertex_auto_range() 
    //      함수 내부에서 update_vertex_range()를 호출할때 사용
    // dstar_lite_find() 함수 내부에서 아래의 두개 함수를 호출할때 사용
    //      dstar_lite_find_target()
    //      dstar_lite_find_route_incremental()
    gint max_range;

    gboolean debug_mode_enabled;  // ✅ 디버그 출력을 켤지 여부

    // ✅ 디버깅용: 각 좌표별 update_vertex() 호출 횟수 저장
    GHashTable* update_count_table;  // key: coord* → value: gint*
} dstar_lite_t;

typedef dstar_lite_t* dstar_lite;

/**
 * @brief 기본 설정값으로 D* Lite 설정 객체를 생성합니다.
 *
 * map이 없으면 NULL
 * 
 * 이 함수는 다음과 같은 기본값으로 구성된 D* Lite 설정 구조체를 생성합니다:
 * - start : (0, 0)
 * - goal : (0, 0)
 * - km: 0.0f
 * - max_range: 0 중심좌표의 이웃만 확인한다.
 * - real_loop_max_retry: 0 반복 탐색 하지 않는다.
 * - width : 0 무한대의 맵
 * - height : 0 무한대의 맵
 * 
 *
 * 8방향, 유클리드 거리, dstar lite 비용, 디버그 모드 FALSE
 * 생성된 설정 객체는 이후 알고리즘에 전달되어 사용됩니다.
 *
 * @return 새로 생성된 dstar_lite 객체. 
 *      사용 후 dstar_lite_free()로 해제 필요.
 */
BYUL_API dstar_lite dstar_lite_new(map m);

/**
 * @brief 사용자 정의 값으로 D* Lite 설정 객체를 생성합니다.
 *
 * map이 없으면 NULL
 * 
 * @param debug_mode_enabled  디버그 모드 활성화 여부
 * @return 새로 생성된 dstar_lite 객체. 
 *      사용 후 dstar_lite_free()로 해제 필요.
 */
BYUL_API dstar_lite dstar_lite_new_full(map m, 
    dsl_cost_func cost_fn, dsl_heuristic_func heuristic_fn,
    gboolean debug_mode_enabled);

BYUL_API void dstar_lite_free(dstar_lite dsl);

BYUL_API coord dstar_lite_get_start(const dstar_lite dsl);

BYUL_API void  dstar_lite_set_start(dstar_lite dsl, const coord c);

BYUL_API coord dstar_lite_get_goal(const dstar_lite dsl);

BYUL_API void  dstar_lite_set_goal(dstar_lite dsl, const coord c);

BYUL_API GHashTable* dstar_lite_get_g_table(const dstar_lite dsl);

BYUL_API GHashTable* dstar_lite_get_rhs_table(const dstar_lite dsl);

BYUL_API dstar_lite_pqueue dstar_lite_get_frontier(const dstar_lite dsl);

BYUL_API void     dstar_lite_set_frontier(
    dstar_lite dsl, dstar_lite_pqueue frontier);

BYUL_API gfloat dstar_lite_get_km(const dstar_lite dsl);
BYUL_API void   dstar_lite_set_km(dstar_lite dsl, gfloat km);

BYUL_API gint   dstar_lite_get_max_range(const dstar_lite dsl);
BYUL_API void   dstar_lite_set_max_range(dstar_lite dsl, gint value);

// find_loop 함수내에서 루프시에 최대 루프 횟수
// 실시간으로 시속 4kmh로 이동할때 interval_msec에 
// 정한 횟수만큼 곱한 시간 만큼 계속 루프 돈다. 오래 돈다는 거다
// 이걸 개선 필요하다 10x10에서 100 정도는 되야 할 거같다.
BYUL_API gint   dstar_lite_get_real_loop_max_retry(const dstar_lite dsl);
BYUL_API void   dstar_lite_set_real_loop_max_retry(
    dstar_lite dsl, gint value);
BYUL_API     gint dstar_lite_real_loop_retry_count(dstar_lite dsl);

// 10x10의 맵에서 100은 되어야 잘 찾는거 같다.
BYUL_API gint dstar_lite_get_compute_max_retry(const dstar_lite dsl);
BYUL_API void dstar_lite_set_compute_max_retry(
    const dstar_lite dsl, gint v);

BYUL_API     gint dstar_lite_proto_compute_retry_count(dstar_lite dsl);

BYUL_API     gint dstar_lite_real_compute_retry_count(dstar_lite dsl);

// proto route 생성할때 reconstruct_route한다. 여기에 사용하는 루프
// 10x10에서 100은 오버고 10은 너무 작고 대충 40 정도면 되겠다.
BYUL_API gint dstar_lite_get_reconstruct_max_retry(const dstar_lite dsl);
BYUL_API void dstar_lite_set_reconstruct_max_retry(
    const dstar_lite dsl, gint v);
BYUL_API     gint dstar_lite_reconstruct_retry_count(dstar_lite dsl);

BYUL_API gboolean dstar_lite_get_debug_mode_enabled(const dstar_lite dsl);

BYUL_API void     dstar_lite_set_debug_mode_enabled(
    dstar_lite dsl, gboolean enabled);

BYUL_API GHashTable* dstar_lite_get_update_count_table(const dstar_lite dsl);

BYUL_API void         dstar_lite_add_update_count(
    dstar_lite dsl, const coord c);

BYUL_API void         dstar_lite_clear_update_count(dstar_lite dsl);

BYUL_API gint         dstar_lite_get_update_count(
    dstar_lite dsl, const coord c);

BYUL_API const map    dstar_lite_get_map(const dstar_lite dsl);

BYUL_API const route dstar_lite_get_proto_route(const dstar_lite dsl);

BYUL_API const route dstar_lite_get_real_route(const dstar_lite dsl);

// 설정 값들 시작, 목표 ,맵등을 유지하고
// 해시테이블들과, 우선순위큐를 초기화한다.
BYUL_API void         dstar_lite_reset(dstar_lite dsl);

BYUL_API gint dstar_lite_get_interval_msec(dstar_lite dsl);

BYUL_API void dstar_lite_set_interval_msec(dstar_lite dsl, gint interval_msec);

// 함수 포인터

BYUL_API gfloat dstar_lite_cost(
    const map m, const coord start, const coord goal, gpointer userdata);
BYUL_API dsl_cost_func    dstar_lite_get_cost_func(const dstar_lite dsl);
BYUL_API void dstar_lite_set_cost_func(dstar_lite dsl, dsl_cost_func fn);
BYUL_API gpointer    dstar_lite_get_cost_func_userdata(const dstar_lite dsl);
BYUL_API void dstar_lite_set_cost_func_userdata(
    dstar_lite dsl, gpointer userdata);    

BYUL_API gboolean dstar_lite_is_blocked(
    dstar_lite dsl, gint x, gint y, gpointer userdata);    
BYUL_API dsl_is_blocked_func dstar_lite_get_is_blocked_func(dstar_lite dsl);
BYUL_API void dstar_lite_set_is_blocked_func(
    dstar_lite dsl, dsl_is_blocked_func fn);
BYUL_API gpointer dstar_lite_get_is_blocked_func_userdata(dstar_lite dsl);
BYUL_API void dstar_lite_set_is_blocked_func_userdata(
    dstar_lite dsl, gpointer userdata);

BYUL_API gfloat dstar_lite_heuristic(
    const coord start, const coord goal, gpointer userdata);
BYUL_API dsl_heuristic_func dstar_lite_get_heuristic_func(
    const dstar_lite dsl);
BYUL_API void         dstar_lite_set_heuristic_func(
    dstar_lite dsl, dsl_heuristic_func func);
BYUL_API gpointer dstar_lite_get_heuristic_func_userdata(dstar_lite dsl);
BYUL_API void dstar_lite_set_heuristic_func_userdata(
    dstar_lite dsl, gpointer userdata);    

BYUL_API void move_to(const coord c, gpointer userdata);
BYUL_API move_func dstar_lite_get_move_func(const dstar_lite dsl);
BYUL_API void dstar_lite_set_move_func(dstar_lite dsl, move_func fn);
BYUL_API gpointer dstar_lite_get_move_func_userdata(const dstar_lite dsl);
BYUL_API void dstar_lite_set_move_func_userdata(
    dstar_lite dsl, gpointer userdata);

// get_changed_coords_fn 콜백 예제 함수
BYUL_API GList* get_changed_coords(gpointer userdata);
BYUL_API changed_coords_func dstar_lite_get_changed_coords_func(
    const dstar_lite dsl);
BYUL_API void dstar_lite_set_changed_coords_func(
    dstar_lite dsl, changed_coords_func fn);
BYUL_API gpointer dstar_lite_get_changed_coords_func_userdata(
    const dstar_lite dsl);
BYUL_API void dstar_lite_set_changed_coords_func_userdata(
    dstar_lite dsl, gpointer userdata);

/**
 * @brief D* Lite용 우선순위 키 계산 함수
 *
 * g[s]와 rhs[s] 중 더 작은 값을 k2로 하고,
 * k1 = k2 + heuristic(start, s) + km
 *
 * @param dsl D* Lite 객체
 * @param s   대상 좌표
 * @return 계산된 dstar_lite_key_t 구조체
 */
BYUL_API dstar_lite_key dstar_lite_calculate_key(dstar_lite dsl, const coord s);

BYUL_API void dstar_lite_init(dstar_lite dsl);

/**
 * @brief 주어진 노드의 rhs 값을 재계산하고 필요시 open 리스트 갱신
 * @param al 알고리즘 컨텍스트
 * @param u 업데이트할 좌표
 */
BYUL_API void dstar_lite_update_vertex(const dstar_lite dsl, const coord u);

/**
 * @brief 특정 좌표를 중심으로 주어진 범위 내 모든 좌표에 대해 update_vertex() 수행
 * 
 * @param al         알고리즘 컨텍스트
 * @param s          중심 좌표
 * @param max_range  범위 (0이면 s만 갱신)
 */
BYUL_API void dstar_lite_update_vertex_range(const dstar_lite dsl, 
    const coord s, gint max_range);

/**
 * @brief config에 지정된 max_range를 기준으로 update_vertex_range() 수행
 * 
 * @param al 알고리즘 컨텍스트
 * @param s 중심 좌표
 */
BYUL_API void dstar_lite_update_vertex_auto_range(
    const dstar_lite dsl, const coord s);

/**
 * @brief open list에 따라 최단 경로 계산을 수행합니다.
 * 
 * @param al 알고리즘 컨텍스트
 */    
BYUL_API void dstar_lite_compute_shortest_route(dstar_lite dsl);

/**
 * @brief 두 좌표 사이의 경로를 재구성합니다.
 *
 * g ≈ rhs 조건이 만족되었을 때, 실제 경로를 추출하여 반환합니다.
 * 조건이 만족되지 않으면 NULL을 반환합니다.
 *
 * @param dsl 알고리즘 컨텍스트
 * @return route 유효한 경로 객체, 실패 시 NULL
 */
BYUL_API route dstar_lite_reconstruct_route(const dstar_lite dsl);

// 1회용 경로 찾기 가장 단순한 형태 정적인 경로 찾기와 같다.
BYUL_API route dstar_lite_find(const dstar_lite dsl);

// find_proto와 find_loop로 나뉜 경로 찾기를 통합했다
BYUL_API void dstar_lite_find_full(const dstar_lite dsl);

// 동적인 경로를 찾기 위해 초기 경로를 생성한다.
BYUL_API void dstar_lite_find_proto(const dstar_lite dsl);

// 동적인 경로를 찾기 위해 초기 경로로 생성된 경로를 통해 동적인 경로를 찾는다
// dstar_lite_find_proto먼저 실행되어야 한다.
// 그렇지 않으면 길찾기 실패한다.
// 왜 find_proto를 따로 실행해야 하냐고 물어보면 고급 사용자를 위해서라고 대답하겠다.
// find_proto와 find_loop사이에 어떤 작업을 하고 싶은 사람이 있을 것이다.
// 왜 콜백함수 포인터를 사용하지 않고 라고 다시 물어보면
// 그걸위해 또 리팩토링 하기 싫어서 라고 말하겠다.
// 나중에 콜백함수가 추가될수도 있다.
// 동적인 경로를 얻고 싶으면 dstar_lite_find_full()을 사용하면 된다.
BYUL_API void dstar_lite_find_loop(const dstar_lite dsl);

/**
 * @brief 주어진 경로에 포함된 모든 좌표에 대해 update_vertex 수행
 *
 * @param al 알고리즘 컨텍스트
 * @param p 갱신할 경로
 */
BYUL_API void dstar_lite_update_vertex_by_route(dstar_lite dsl, route p);

// 루프를 강제종료한다.
BYUL_API void dstar_lite_force_quit(dstar_lite dsl);

// 강제 종료가 요청되었나?
BYUL_API gboolean dstar_lite_is_quit_forced(dstar_lite dsl);

BYUL_API void dstar_lite_set_force_quit(dstar_lite dsl, gboolean v);

#ifdef __cplusplus
}
#endif

#endif // DSTAR_LITE_H
