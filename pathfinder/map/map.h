#ifndef MAP_H
#define MAP_H

#include "byul_config.h"
#include "core.h"

#include "internal/coord.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief 격자 기반 맵 구조체
 *
 * 맵의 크기, 차단된 좌표 및 장애물을 관리하며
 * 좌표 기반 탐색과 배치 기능을 제공한다.
 */
typedef enum {
    MAP_NEIGHBOR_4,
    MAP_NEIGHBOR_8
} map_neighbor_mode_t;

typedef struct {
    guint8 type;     // 1 byte: 지형 종류 (0 = 평지, 1 = 숲, 2 = 산 등)
    gint8 height;    // 1 byte: 고도 (-128~127)
    guint8 flags;    // 1 byte: 비트마스크 (위험지역, 장식 등)
    guint8 extra;    // 1 byte: 확장용 또는 예약
} tile_t;

typedef tile_t* tile;

BYUL_API tile tile_new(void);

BYUL_API tile tile_new_full(guint8 type, gint8 height,
    guint8 flags, guint8 extra);

BYUL_API void tile_free(tile t);

typedef struct s_map {
    gint width;
    gint height;
    map_neighbor_mode_t mode;

    // coord를 hashset에 추가한다
    GHashTable* blocked_coords;

    GHashTable* tiles;           // key = coord*, value = tile_t*
    tile_t default_tile;         // 해시테이블에 없을 때 사용하는 기본값
} map_t;

typedef map_t* map;

/* 생성자 */

// 기본적으로 0x0의 맵과 MAP_NEIGHBOR_4로 설정
BYUL_API map map_new(void);

// 0 x 0 ~ INT_MAX x INT_MAX
// 0 x 0 이란건 무한대의 맵이라는 것이다. 한계가 없다.
BYUL_API map map_new_full(gint width, gint height, map_neighbor_mode_t mode);

BYUL_API void map_free(const map m);

// flud 관련

BYUL_API guint map_hash(const map m);

BYUL_API gboolean map_equal(const map ma, const map mb);

BYUL_API map map_copy(const map m);

// 전용 함수들

BYUL_API gint map_get_width(const map m);

BYUL_API void map_set_width(map m, gint width);

BYUL_API gint map_get_height(const map m);

BYUL_API void map_set_height(map m, gint height);

BYUL_API map_neighbor_mode_t map_get_neighbor_mode(const map m);

BYUL_API void map_set_neighbor_mode(map m, map_neighbor_mode_t mode);

// 모든 막힌 좌표들을 반환한다.
BYUL_API const GHashTable* map_get_blocked_coords(const map m);

// 해당 좌표를 막는다 기본 장애물이 자동으로 생긴다.
BYUL_API gboolean map_block_coord(map m, gint x, gint y);

BYUL_API gboolean map_unblock_coord(map m, gint x, gint y);

/**
 * @brief 지정 좌표가 장애물인지 확인합니다.
 *
 * @param m   맵 객체
 * @param x   X 좌표
 * @param y   Y 좌표
 * @return TRUE이면 해당 좌표는 차단됨 (장애물)
 */
BYUL_API gboolean map_is_blocked(const map m, gint x, gint y);


/// @brief 주어진 좌표가 맵 내부에 포함되는지 확인
/// width 또는 height가 0이면 해당 축은 무한대로 간주
BYUL_API gboolean map_is_inside(const map m, gint x, gint y);

/**
 * @brief 주어진 좌표의 인접한 유효 좌표들을 반환합니다.
 *
 * 현재 맵에서 (x, y)를 기준으로 4방향 또는 8방향(맵 모드에 따라 다름)의  
 * 인접 좌표 중, 맵 내부에 있으며 장애물이 없는 좌표만을 리스트로 반환합니다.
 * 반환되는 리스트의 각 원소는 `coord` 포인터이며, 호출자가 직접 해제해야 합니다.
 *
 * @param m 맵 객체
 * @param x 기준 좌표의 x값
 * @param y 기준 좌표의 y값
 * @return GList* 유효한 인접 좌표들의 리스트 (coord*).  
 *         실패 시 NULL. 호출 후 반드시 
 *          g_list_free_full(..., coord_free)로 해제해야 합니다.
 */
BYUL_API GList* map_clone_neighbors(const map m, gint x, gint y);


// 모든 막힌 좌표들을 제거한한다.
BYUL_API void map_clear(map m);

BYUL_API gboolean map_set_tile(map m, coord c, const tile_t* tile);

BYUL_API guint8 map_get_tile_type(const map m, gint x, gint y);

BYUL_API gint8 map_get_tile_height(const map m, gint x, gint y);

BYUL_API guint8 map_get_tile_flags(const map m, gint x, gint y);

BYUL_API guint8 map_get_tile_extra(const map m, gint x, gint y);


/**
 * @brief 인접한 좌표들을 반환합니다 (장애물 포함).
 *
 * 이 함수는 주어진 좌표 (x, y)를 기준으로, 맵 내부의 인접한 좌표들을 모두 반환합니다.  
 * MAP_NEIGHBOR_4 또는 MAP_NEIGHBOR_8 설정에 따라 4방향 또는 8방향 이웃을 탐색합니다.  
 * 기존 map_clone_neighbors()와는 달리, **장애물로 표시된 좌표도 포함**하여 반환합니다.
 *
 * 반환되는 리스트의 각 원소는 coord* 타입이며, 
 * 사용 후 반드시 coord_free()로 해제해야 합니다.
 *
 * @param m 탐색할 맵
 * @param x 기준 좌표의 X값
 * @param y 기준 좌표의 Y값
 * @return GList* coord* 포인터들의 리스트. 맵 범위를 벗어난 좌표는 제외되며,
 *         NULL일 수 있습니다. 리스트 자체는 g_list_free_full()로, 
 *      coord는 coord_free()로 해제해야 합니다.
 */
BYUL_API GList* map_clone_neighbors_all(const map m, gint x, gint y);

/**
 * @brief 중심 좌표 (x, y)를 기준으로 range 이내 모든 좌표의 이웃을 수집합니다.
 *
 * 내부적으로 각 (cx, cy)에 대해 map_clone_neighbors_all()를 호출하고,
 * 그 결과를 하나의 GList로 합치되, 좌표 중복은 제거합니다.
 *
 * @param m      맵 객체
 * @param x      중심 x 좌표
 * @param y      중심 y 좌표
 * @param range  반지름 범위 (0 이상)
 *  0이면 중심좌표의 이웃만 확인한다.
 * @return       coord* GList. 중복 없음. 
 *                  사용 후 g_list_free_full(..., coord_free) 해야 함.
 */
BYUL_API GList* map_clone_neighbors_all_range(map m, 
    gint x, gint y, gint range);

#ifdef __cplusplus
}
#endif

#endif // MAP_H
