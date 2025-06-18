#ifndef ROUTE_H
#define ROUTE_H

#include "byul_config.h"
#include "internal/coord.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum e_route_dir{
    ROUTE_DIR_UNKNOWN, 
    ROUTE_DIR_RIGHT,
    ROUTE_DIR_TOP_RIGHT,
    ROUTE_DIR_TOP,
    ROUTE_DIR_TOP_LEFT,
    ROUTE_DIR_LEFT,
    ROUTE_DIR_DOWN_LEFT,
    ROUTE_DIR_DOWN,
    ROUTE_DIR_DOWN_RIGHT,
    ROUTE_DIR_COUNT
} route_dir_t;

typedef struct s_route {
    GList*   coords;     // 순서 있는 좌표 리스트 (coord*)
    gfloat   cost;       // 총 비용
    gboolean success;    // 경로 탐색 성공 여부

    GList* visited_order;   // 방문 순서 : 이건 단순 log이다
    GHashTable* visited_count;           ///< 방문 횟수

   float avg_vec_x;
    float avg_vec_y;
    int   vec_count;    
} route_t;

typedef route_t* route;

/* 생성자 */
BYUL_API route route_new(void);

// 비용과 방문 순서를 기록할지 여부
BYUL_API route route_new_full(gfloat cost);

BYUL_API void route_free(const route p);

BYUL_API guint route_hash(const route a);

BYUL_API gboolean route_equal(const route a, const route b);

BYUL_API route route_copy(const route p);

/* 기본 get/set */
BYUL_API void route_set_cost(route p, gfloat cost);

BYUL_API gfloat route_get_cost(const route p);

BYUL_API void route_set_success(route p, gboolean success);

BYUL_API gboolean route_get_success(const route p);

BYUL_API void route_set_coords(const route p, const GList* coords);

BYUL_API GList* route_get_coords(const route p);

BYUL_API GList* route_get_visited_order(const route p);

BYUL_API void route_set_visited_order(route p, const GList* visited_order);

BYUL_API GHashTable* route_get_visited_count(const route p);

BYUL_API void route_set_visited_count(route p, const GHashTable* visited_count);

BYUL_API gboolean route_add_coord(route p, const coord c);

BYUL_API void route_clear_coords(route p);

// 방문 횟수와 방문 순서를 로깅.
BYUL_API gboolean route_add_visited(route p, const coord c);

BYUL_API void route_clear_visited(route p);

BYUL_API gint route_length(const route p);

// 마지막 좌표를 반환 (NULL 가능성 있음)
BYUL_API coord route_get_last(const route p);

// 다른 route의 모든 좌표를 병합
BYUL_API void route_append(route dest, const route src);

/**
 * @brief 경로를 중복 없이 이어 붙입니다.
 *
 * 주어진 src 경로의 좌표들을 dest 경로에 순차적으로 추가합니다.  
 * 단, dest의 마지막 좌표와 src의 첫 좌표가 동일한 경우  
 * 해당 좌표는 중복 추가하지 않습니다.
 *
 * @param dest 이어붙일 대상 경로 (기존 경로)
 * @param src  이어붙일 원본 경로 (추가할 경로)
 *
 * @note 좌표는 내부적으로 coord_copy()를 통해 복사됩니다.
 */
BYUL_API void route_append_nodup(route dest, const route src);

// 모든 경로를 출력한다.
BYUL_API void route_print(const route p);

/**
 * @brief 경로 상의 index → index+1 방향을 반환합니다.
 *        단, 마지막 index의 경우 index-1과 동일한 방향을 반환합니다 (관성 유지).
 *
 * @param p      route 객체
 * @param index  현재 인덱스 (0 ≤ index < length)
 * @return coord 구조체 (dx, dy). 유효하지 않으면 NULL.
 */
BYUL_API coord route_look_at(route p, int index);

/**
 * @brief 방향 벡터(dx, dy)를 8방향 enum으로 변환합니다.
 *
 * @param dxdy 방향 벡터 (x, y)
 * @return route_dir_t ROUTE_DIR_*
 */
BYUL_API route_dir_t route_get_direction_enum(const coord dxdy);

/**
 * @brief 경로 상의 index 방향을 8방향 enum으로 반환합니다.
 *        마지막 index의 경우 이전 방향을 반환합니다. (관성 유지)
 *
 * @param p      route 객체
 * @param index  경로 인덱스
 * @return route_dir_t ROUTE_DIR_*
 */
BYUL_API route_dir_t route_get_direction(route p, int index);

/**
 * @brief 이동 경로의 방향이 변경되었는지 판단합니다.
 *
 * - 이전 위치와 현재 위치로부터 벡터를 계산하고,
 * - 내부적으로 평균 방향 벡터와 비교하여
 *   지정된 각도 이상 차이 나면 변경으로 판단합니다.
 *
 * @param p       route 객체
 * @param from    이전 좌표
 * @param to      현재 좌표
 * @param angle_threshold_deg 허용 편차 각도 (도 단위, 기본 10도)
 * @return TRUE = 변경 감지됨 / FALSE = 유지 중
 */
BYUL_API gboolean route_has_changed(
    route p, const coord from,
    const coord to, gfloat angle_threshold_deg);

/**
 * @brief 경로가 변경되었는지 판단하고, 현재 방향과 평균 방향 간의 각도를 반환합니다.
 *
 * - 평균 벡터와 현재 벡터의 각도 차이를 비교해 변경 여부 판단
 * - 변경 여부는 임계값 각도보다 큰지 여부로 판단
 * - 각도는 출력 파라미터로 함께 반환됨
 *
 * @param p       route 객체
 * @param from    이전 위치
 * @param to      현재 위치
 * @param angle_threshold_deg 변경 기준 각도 (deg)
 * @param out_angle_deg 실제 각도 값 저장할 포인터 (nullable 아님)
 * @return TRUE = 변경 감지됨 / FALSE = 경로 유지 중
 */
BYUL_API gboolean route_has_changed_with_angle(
    route p,
    const coord from,
    const coord to,
    gfloat angle_threshold_deg,
    gfloat* out_angle_deg);


/**
 * @brief 현재 이동 벡터를 평균 벡터 누적에 반영합니다.
 *
 * @param p    route 객체
 * @param from 이전 좌표
 * @param to   현재 좌표
 */
BYUL_API void route_update_average_vector(
    route p, const coord from, const coord to);

/**
 * @brief 경로 객체에서 index 위치의 coord를 반환합니다.
 *
 * @param p route 객체
 * @param index  추출할 인덱스
 * @return coord (실패 시 NULL)
 */
BYUL_API coord route_get_coord_at(route p, int index);

/**
 * @brief 평균 벡터 누적을 index 기반으로 수행합니다.
 *
 * @param p 경로 객체
 * @param index_from 시작 인덱스
 * @param index_to 끝 인덱스
 */
BYUL_API void route_update_average_vector_by_index(
    route p, int index_from, int index_to);

/**
 * @brief 경로 변경 여부를 index 기반으로 판단합니다.
 *
 * @param p 경로 객체
 * @param index_from 시작 인덱스
 * @param index_to 끝 인덱스
 * @param angle_threshold_deg 허용 오차 각도 (도 단위)
 * @return TRUE = 변경 감지 / FALSE = 경로 유지
 */
BYUL_API gboolean route_has_changed_by_index(
    route p, int index_from, int index_to, gfloat angle_threshold_deg);

/**
 * @brief 경로 변경 여부를 판단하고 각도를 반환합니다 (index 기반).
 *
 * @param p 경로 객체
 * @param index_from 시작 인덱스
 * @param index_to 끝 인덱스
 * @param angle_threshold_deg 허용 오차 각도 (도 단위)
 * @param out_angle_deg 실제 각도 (출력값)
 * @return TRUE = 변경 감지 / FALSE = 유지 중
 */
BYUL_API gboolean route_has_changed_with_angle_by_index(
    route p,
    int index_from,
    int index_to,
    gfloat angle_threshold_deg,
    gfloat* out_angle_deg);

/**
 * @brief 경로 상에서 최근 좌표와 과거 좌표 간의 방향 각도를 계산합니다.
 *
 * - history만큼 과거로 거슬러간 좌표와 가장 마지막 좌표를 비교하여
 *   방향 벡터를 만들고, 해당 벡터의 각도를 계산합니다.
 * - 좌표 수가 부족한 경우 가장 앞 좌표(index 0)와 비교합니다.
 *
 * @param p route 객체
 * @param history 조회할 과거 좌표 수 (최소 1)
 * @return float 각도 값 (도 단위, -180.0 ~ 180.0). 실패 시 0.0f 반환.
 */
BYUL_API gfloat route_calc_average_dir(route p, int history);

/**
 * @brief 경로 상에서 최근 좌표와 과거 좌표 간의 방향을 계산합니다.
 *
 * - history만큼 과거로 거슬러간 좌표와 가장 마지막 좌표를 비교하여
 *   방향 벡터를 만들고, 해당 벡터에 대응하는 8방향 enum을 반환합니다.
 * - 좌표 수가 부족할 경우, 가장 앞 좌표(index 0)와 비교합니다.
 * - 방향이 정의되지 않거나 (0,0)이면 ROUTE_DIR_UNKNOWN을 반환합니다.
 *
 * @param p route 객체
 * @param history 조회할 과거 좌표 수 (최소 1)
 * @return route_dir_t 방향 enum. 실패 시 ROUTE_DIR_UNKNOWN.
 */
BYUL_API route_dir_t route_calc_average_facing(route p, int history);

/**
 * @brief 두 좌표 간의 8방향 방향을 계산합니다.
 *
 * - 입력된 start와 goal 좌표의 차이를 기반으로 방향 벡터 (dx, dy)를 생성하고,
 * - 해당 벡터를 8방향 enum(`route_dir_t`) 중 하나로 매핑합니다.
 * - 방향 벡터가 (0,0)이거나 유효하지 않으면 ROUTE_DIR_UNKNOWN을 반환합니다.
 *
 * @param start 기준 좌표 (시작점)
 * @param goal  목표 좌표 (도착점)
 * @return route_dir_t  방향 enum (ROUTE_DIR_RIGHT 등), 실패 시 ROUTE_DIR_UNKNOWN
 */
BYUL_API route_dir_t calc_direction(const coord start, const coord goal);

BYUL_API coord direction_to_coord(route_dir_t route_dir);

#ifdef __cplusplus
}
#endif

#endif // ROUTE_H