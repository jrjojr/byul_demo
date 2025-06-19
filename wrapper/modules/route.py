from ffi_core import ffi, C
from pathlib import Path
import os
from typing import Any

from coord import c_coord
from ffi_core import ffi
from list import c_list
from dict import c_dict

from enum import IntEnum

class RouteDir(IntEnum):
    UNKNOWN = 0
    RIGHT = 1
    TOP_RIGHT = 2
    TOP = 3
    TOP_LEFT = 4
    LEFT = 5
    DOWN_LEFT = 6
    DOWN = 7
    DOWN_RIGHT = 8
    COUNT = 9

ffi.cdef("""
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
         
    typedef struct s_route* route;
    typedef struct s_route { 
         GList * coords ; 
         float cost ; 
         int success ; 
         GList * visited_order ; 
         GHashTable * visited_count ;
        GHashTable * algo_specific_dict ;
         
        
   float avg_vec_x;
    float avg_vec_y;
    int   vec_count;             
        } route_t;
         
    route route_new(void);
     route route_new_full(float cost);
     void route_free(const route p);
     unsigned int route_hash(const route a);
     int route_equal(const route a, const route b);
     route route_copy(const route p);
     flud flud_new_route(const route s);
     flud flud_wrap_route(const route s);
     int flud_fetch_route(const flud d, route *out);
     const route flud_get_route(const flud d);
     int flud_set_route(flud d, const route s);
     int flud_is_route(const flud d);
     void route_set_cost(route p, float cost);
     float route_get_cost(const route p);
     void route_set_success(route p, int success);
     int route_get_success(const route p);
     void route_set_coords(const route p, const GList* coords);
     GList* route_get_coords(const route p);
     GList* route_get_visited_order(const route p);
     void route_set_visited_order(route p, const GList* visited_order);
     GHashTable* route_get_visited_count(const route p);
     void route_set_visited_count(route p, const GHashTable* visited_count);
     int route_add_coord(route p, const coord c);
     void route_clear_coords(route p);
     int route_add_visited(route p, const coord c);
     void route_clear_visited(route p);
     int route_length(const route p);
     
    void route_append(route dest, const route src);
    void route_append_nodup(route dest, const route src);
     
    void route_print(const route p);
         
/**
 * @brief 경로 상의 index → index+1 방향을 반환합니다.
 *        단, 마지막 index의 경우 index-1과 동일한 방향을 반환합니다 (관성 유지).
 *
 * @param p      route 객체
 * @param index  현재 인덱스 (0 ≤ index < length)
 * @return coord 구조체 (dx, dy). 유효하지 않으면 NULL.
 */
coord route_look_at(route p, int index);

/**
 * @brief 방향 벡터(dx, dy)를 8방향 enum으로 변환합니다.
 *
 * @param dxdy 방향 벡터 (x, y)
 * @return int ROUTE_DIR_*
 */
int route_get_direction_by_coord(const coord dxdy);

/**
 * @brief 경로 상의 index 방향을 8방향 enum으로 반환합니다.
 *        마지막 index의 경우 이전 방향을 반환합니다. (관성 유지)
 *
 * @param p      route 객체
 * @param index  경로 인덱스
 * @return int ROUTE_DIR_*
 */
int route_get_direction_by_index(route p, int index);

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
gboolean route_has_changed(
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
gboolean route_has_changed_with_angle(
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
void route_update_average_vector(
    route p, const coord from, const coord to);

/**
 * @brief 경로 객체에서 index 위치의 coord를 반환합니다.
 *
 * @param p route 객체
 * @param index  추출할 인덱스
 * @return coord (실패 시 NULL)
 */
coord route_get_coord_at(route p, int index);

/**
 * @brief 평균 벡터 누적을 index 기반으로 수행합니다.
 *
 * @param p 경로 객체
 * @param index_from 시작 인덱스
 * @param index_to 끝 인덱스
 */
void route_update_average_vector_by_index(
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
gboolean route_has_changed_by_index(
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
gboolean route_has_changed_with_angle_by_index(
    route p,
    int index_from,
    int index_to,
    gfloat angle_threshold_deg,
    gfloat* out_angle_deg);

int route_calc_average_facing(route p, int history);
         
int calc_direction(const coord start, const coord goal);
         
coord direction_to_coord(route_dir_t route_dir);         

void route_insert(route p, int index, const coord c);
void route_remove_at(route p, int index);
void route_remove_value(route p, const coord c);
gboolean route_contains(const route p, const coord c);
gint route_find(const route p, const coord c);
void route_slice(route p, int start, int end);
         
""")

def route_set_coords(p: Any, coords: Any) -> None:
    return C.route_set_coords(p, coords)


def route_get_coords(p: Any) -> Any:
    return C.route_get_coords(p)


def route_get_visited_order(p: Any) -> Any:
    return C.route_get_visited_order(p)


def route_set_visited_order(p: Any, visited_order: Any) -> None:
    return C.route_set_visited_order(p, visited_order)


def route_get_visited_count(p: Any) -> Any:
    return C.route_get_visited_count(p)

def route_set_visited_count(p: Any, visited_count: Any) -> None:
    return C.route_set_visited_count(p, visited_count)

class c_route:
    def __init__(self, cost: float = 0.0, raw_ptr=None):
        self._p = raw_ptr if raw_ptr else C.route_new_full(cost)

    @property
    def cost(self):
        return C.route_get_cost(self._p)

    @cost.setter
    def cost(self, value):
        C.route_set_cost(self._p, value)

    @property
    def success(self):
        return C.route_get_success(self._p) != 0

    @success.setter
    def success(self, value: bool):
        C.route_set_success(self._p, int(value))

    @property
    def total_retry_count(self):
        return C.route_get_total_retry_count(self._p)
    
    @total_retry_count.setter
    def total_retry_count(self, v:int):
        C.route_set_total_retry_count(self._p, v)

    def add_coord(self, coord):
        C.route_add_coord(self._p, coord.ptr())

    def add_visited(self, coord):
        C.route_add_visited(self._p, coord.ptr())

    def get_coords(self) -> list[c_coord]:
        head = C.route_get_coords(self._p)
        if head == ffi.NULL:
            return []
        
        result = []
        node = head
        while node != ffi.NULL:
            coord_ptr = ffi.cast("coord", node.data)
            result.append(c_coord(raw_ptr=coord_ptr))
            node = node.next
        return result

    def clear_coords(self):
        C.route_clear_coords(self._p)

    def clear_visited(self):
        C.route_clear_visited(self._p)

    def copy(self):
        return c_route(raw_ptr=C.route_copy(self._p))

    def __eq__(self, other):
        return C.route_equal(self._p, other._p) != 0

    def __hash__(self):
        return C.route_hash(self._p)

    def __len__(self):
        return C.route_length(self._p)

    def __iter__(self):
        head = C.route_get_coords(self._p)
        node = head
        while node != ffi.NULL:
            coord_ptr = ffi.cast("coord", node.data)
            yield c_coord(raw_ptr=coord_ptr)
            # x = C.coord_get_x(coord_ptr)
            # y = C.coord_get_y(coord_ptr)
            # yield c_coord(x, y)
            node = node.next

    def to_list(self):
        return list(iter(self))

    def append(self, other):
        C.route_append(self._p, other._p)

    def append_nodup(self, other):
        # void route_append_nodup(route dest, const route src);
        C.route_append_nodup(self.ptr(), other.ptr())

    def ptr(self):
        return self._p

    def __del__(self):
        # self.close()
        pass

    def close(self):
        if self._p:
            C.route_free(self._p)
            self._p = None        

    def __enter__(self):
        # with문이 시작될 때 호출
        return self  # 보통 self를 반환함

    def __exit__(self, exc_type, exc_val, exc_tb):
        # with문이 끝났을 때 호출됨
        # 여기서 자원 정리를 직접 수행
        self.close()

    def __repr__(self):
        return f"c_route(cost={self.cost:.3f}, success={self.success}, len={len(self)})"

    def __str__(self):
        return self.format_str()

    def format_str(self) -> str:
        coords = self.to_list()
        if not coords:
            return "경로 없음"
        return "최종 경로 : " + " -> ".join(f"({c.x}, {c.y})" for c in coords)
    
    def print(self) -> None:
        print(self.format_str())

    def look_at(self, index:int):
        # coord route_look_at(route p, int index);
        return c_coord(raw_ptr=C.route_look_at(self._p, index))

    # def get_direction_by_coord(self, dxdy:c_coord):
    #     # int route_get_direction_by_coord(const coord dxdy);
    #     return C.route_get_direction_by_coord(dxdy.ptr())

    # def get_direction_by_index(self, index:int):
    #     # int route_get_direction_by_index(route p, int index);
    #     return C.route_get_direction_by_index(self._p, index)

    def get_direction_by_coord(self, dxdy: c_coord) -> RouteDir:
        val = C.route_get_direction_by_coord(dxdy.ptr())
        return RouteDir(val)

    def get_direction_by_index(self, index: int) -> RouteDir:
        val = C.route_get_direction_by_index(self._p, index)
        return RouteDir(val)

    def has_changed(self, start:c_coord, goal:c_coord,
                    anle_threshold_deg:float):
        # gboolean route_has_changed(
        #     route p, const coord from,
        #     const coord to, gfloat angle_threshold_deg);
        return C.route_has_changed(self._p, start, goal, anle_threshold_deg)

    def has_changed_with_angle(self, start:c_coord, goal:c_coord,
                    angle_threshold_deg:float):
        # gboolean route_has_changed_with_angle(
        #     route p,
        #     const coord from,
        #     const coord to,
        #     gfloat angle_threshold_deg,
        #     gfloat* out_angle_deg);
        
        out_angle_deg_ptr = ffi.new("float *")        
        result = C.route_has_changed_with_angle(self._p, start, goal,
            angle_threshold_deg, out_angle_deg_ptr)
        return result, out_angle_deg_ptr[0]

    def update_average_vector(self, start:c_coord, goal:c_coord):
        # void route_update_average_vector(
        #     route p, const coord from, const coord to);
        C.route_update_average_vector(self._p, start, goal)

    def get_coord_at(self, index:int):
        # coord route_get_coord_at(route p, int index);
        return c_coord(raw_ptr=C.route_get_coord_at(self._p, index))

    def update_average_vector_by_index(self, index_start:int, index_goal:int):
        # void route_update_average_vector_by_index(
        #     route p, int index_from, int index_to);
        C.route_update_average_vector_by_index(self._p, 
                                              index_start, index_goal)

    def has_changed_by_index(self, index_start:int, index_goal:int,
                             angle_threshold_deg:float):
        # gboolean route_has_changed_by_index(
        #     route p, int index_from, int index_to, gfloat angle_threshold_deg);
        return C.route_has_changed_by_index(self._p, index_start, index_goal,
                                           angle_threshold_deg)
    
    def has_changed_with_angle_by_index(self, index_start:int, index_goal:int,
                                        angle_threshold_deg:float):
        # gboolean route_has_changed_with_angle_by_index(
        #     route p,
        #     int index_from,
        #     int index_to,
        #     gfloat angle_threshold_deg,
        #     gfloat* out_angle_deg);
        
        out_angle_deg_ptr = ffi.new("float *")        
        result = C.route_has_changed_with_angle_by_index(self._p,
            index_start, index_goal, angle_threshold_deg, out_angle_deg_ptr)
        
        return result, out_angle_deg_ptr[0]
    
    def calc_average_facing(self, history:int=1):
        # route_dir_t route_calc_average_facing(route p, int history);
        return C.route_calc_average_facing(self._p, history)
    
    def insert(self, index:int, coord:c_coord):
        # void route_insert(route p, int index, const coord c);
        C.route_insert(self.ptr(), index, coord.ptr())

    def remove_at(self, index:int):
        # void route_remove_at(route p, int index);
        C.route_remove_at(self.ptr(), index)

    def remove_value(self, coord:c_coord):
        # void route_remove_value(route p, const coord c);
        C.route_remove_value(self.ptr(), coord.ptr())

    def contains(self, coord:c_coord):
        # gboolean route_contains(const route p, const coord c);
        return C.route_contains(self.ptr(), coord.ptr())
    
    def find(self, coord:c_coord):
        # gint route_find(const route p, const coord c);
        return C.route_find(self.ptr(), coord.ptr())
    
    def slice(self, start:int, end:int):
        # void route_slice(route p, int start, int end);
        C.route_slice(self.ptr(), start, end)

def calc_direction(start:c_coord, goal:c_coord):
    # int calc_direction(const coord start, const coord goal);
    return C.calc_direction(start.ptr(), goal.ptr())

def direction_to_coord(direction: RouteDir):
    return c_coord(raw_ptr=C.direction_to_coord(direction.value))
