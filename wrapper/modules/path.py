from ffi_core import ffi, C
from pathlib import Path
import os
from typing import Any

from coord import c_coord
from ffi_core import ffi
from list import c_list
from dict import c_dict

from enum import IntEnum

class PathDir(IntEnum):
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
    typedef enum e_path_dir{
        PATH_DIR_UNKNOWN, 
        PATH_DIR_RIGHT,
        PATH_DIR_TOP_RIGHT,
        PATH_DIR_TOP,
        PATH_DIR_TOP_LEFT,
        PATH_DIR_LEFT,
        PATH_DIR_DOWN_LEFT,
        PATH_DIR_DOWN,
        PATH_DIR_DOWN_RIGHT,
        PATH_DIR_COUNT
    } path_dir_t;
         
    typedef struct s_path* path;
    typedef struct s_path { 
         GList * coords ; 
         float cost ; 
         int success ; 
         GList * visited_order ; 
         GHashTable * visited_count ;
        GHashTable * algo_specific_dict ;
         
        
   float avg_vec_x;
    float avg_vec_y;
    int   vec_count;             
        } path_t;
         
    path path_new(void);
     path path_new_full(float cost);
     void path_free(const path p);
     unsigned int path_hash(const path a);
     int path_equal(const path a, const path b);
     path path_copy(const path p);
     flud flud_new_path(const path s);
     flud flud_wrap_path(const path s);
     int flud_fetch_path(const flud d, path *out);
     const path flud_get_path(const flud d);
     int flud_set_path(flud d, const path s);
     int flud_is_path(const flud d);
     void path_set_cost(path p, float cost);
     float path_get_cost(const path p);
     void path_set_success(path p, int success);
     int path_get_success(const path p);
     void path_set_coords(const path p, const GList* coords);
     GList* path_get_coords(const path p);
     GList* path_get_visited_order(const path p);
     void path_set_visited_order(path p, const GList* visited_order);
     GHashTable* path_get_visited_count(const path p);
     void path_set_visited_count(path p, const GHashTable* visited_count);
     int path_add_coord(path p, const coord c);
     void path_clear_coords(path p);
     int path_add_visited(path p, const coord c);
     void path_clear_visited(path p);
     int path_length(const path p);
     
    void path_append(path dest, const path src);
    void path_append_nodup(path dest, const path src);
     
    void path_print(const path p);
         
/**
 * @brief 경로 상의 index → index+1 방향을 반환합니다.
 *        단, 마지막 index의 경우 index-1과 동일한 방향을 반환합니다 (관성 유지).
 *
 * @param p      path 객체
 * @param index  현재 인덱스 (0 ≤ index < length)
 * @return coord 구조체 (dx, dy). 유효하지 않으면 NULL.
 */
coord path_look_at(path p, int index);

/**
 * @brief 방향 벡터(dx, dy)를 8방향 enum으로 변환합니다.
 *
 * @param dxdy 방향 벡터 (x, y)
 * @return int PATH_DIR_*
 */
int path_get_direction_enum(const coord dxdy);

/**
 * @brief 경로 상의 index 방향을 8방향 enum으로 반환합니다.
 *        마지막 index의 경우 이전 방향을 반환합니다. (관성 유지)
 *
 * @param p      path 객체
 * @param index  경로 인덱스
 * @return int PATH_DIR_*
 */
int path_get_direction(path p, int index);

/**
 * @brief 이동 경로의 방향이 변경되었는지 판단합니다.
 *
 * - 이전 위치와 현재 위치로부터 벡터를 계산하고,
 * - 내부적으로 평균 방향 벡터와 비교하여
 *   지정된 각도 이상 차이 나면 변경으로 판단합니다.
 *
 * @param p       path 객체
 * @param from    이전 좌표
 * @param to      현재 좌표
 * @param angle_threshold_deg 허용 편차 각도 (도 단위, 기본 10도)
 * @return TRUE = 변경 감지됨 / FALSE = 유지 중
 */
gboolean path_has_changed(
    path p, const coord from,
    const coord to, gfloat angle_threshold_deg);

/**
 * @brief 경로가 변경되었는지 판단하고, 현재 방향과 평균 방향 간의 각도를 반환합니다.
 *
 * - 평균 벡터와 현재 벡터의 각도 차이를 비교해 변경 여부 판단
 * - 변경 여부는 임계값 각도보다 큰지 여부로 판단
 * - 각도는 출력 파라미터로 함께 반환됨
 *
 * @param p       path 객체
 * @param from    이전 위치
 * @param to      현재 위치
 * @param angle_threshold_deg 변경 기준 각도 (deg)
 * @param out_angle_deg 실제 각도 값 저장할 포인터 (nullable 아님)
 * @return TRUE = 변경 감지됨 / FALSE = 경로 유지 중
 */
gboolean path_has_changed_with_angle(
    path p,
    const coord from,
    const coord to,
    gfloat angle_threshold_deg,
    gfloat* out_angle_deg);


/**
 * @brief 현재 이동 벡터를 평균 벡터 누적에 반영합니다.
 *
 * @param p    path 객체
 * @param from 이전 좌표
 * @param to   현재 좌표
 */
void path_update_average_vector(
    path p, const coord from, const coord to);

/**
 * @brief 경로 객체에서 index 위치의 coord를 반환합니다.
 *
 * @param p path 객체
 * @param index  추출할 인덱스
 * @return coord (실패 시 NULL)
 */
coord path_get_coord_at(path p, int index);

/**
 * @brief 평균 벡터 누적을 index 기반으로 수행합니다.
 *
 * @param p 경로 객체
 * @param index_from 시작 인덱스
 * @param index_to 끝 인덱스
 */
void path_update_average_vector_by_index(
    path p, int index_from, int index_to);

/**
 * @brief 경로 변경 여부를 index 기반으로 판단합니다.
 *
 * @param p 경로 객체
 * @param index_from 시작 인덱스
 * @param index_to 끝 인덱스
 * @param angle_threshold_deg 허용 오차 각도 (도 단위)
 * @return TRUE = 변경 감지 / FALSE = 경로 유지
 */
gboolean path_has_changed_by_index(
    path p, int index_from, int index_to, gfloat angle_threshold_deg);

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
gboolean path_has_changed_with_angle_by_index(
    path p,
    int index_from,
    int index_to,
    gfloat angle_threshold_deg,
    gfloat* out_angle_deg);

int path_calc_average_facing(path p, int history);
         
int calc_direction(const coord start, const coord goal);
         
coord direction_to_coord(path_dir_t path_dir);         
                  
""")

def path_set_coords(p: Any, coords: Any) -> None:
    return C.path_set_coords(p, coords)


def path_get_coords(p: Any) -> Any:
    return C.path_get_coords(p)


def path_get_visited_order(p: Any) -> Any:
    return C.path_get_visited_order(p)


def path_set_visited_order(p: Any, visited_order: Any) -> None:
    return C.path_set_visited_order(p, visited_order)


def path_get_visited_count(p: Any) -> Any:
    return C.path_get_visited_count(p)

def path_set_visited_count(p: Any, visited_count: Any) -> None:
    return C.path_set_visited_count(p, visited_count)

class c_path:
    def __init__(self, cost: float = 0.0, raw_ptr=None):
        self._p = raw_ptr if raw_ptr else C.path_new_full(cost)

    @property
    def cost(self):
        return C.path_get_cost(self._p)

    @cost.setter
    def cost(self, value):
        C.path_set_cost(self._p, value)

    @property
    def success(self):
        return C.path_get_success(self._p) != 0

    @success.setter
    def success(self, value: bool):
        C.path_set_success(self._p, int(value))

    @property
    def total_retry_count(self):
        return C.path_get_total_retry_count(self._p)
    
    @total_retry_count.setter
    def total_retry_count(self, v:int):
        C.path_set_total_retry_count(self._p, v)

    def add_coord(self, coord):
        C.path_add_coord(self._p, coord.ptr())

    def add_visited(self, coord):
        C.path_add_visited(self._p, coord.ptr())

    def get_coords(self) -> list[c_coord]:
        head = C.path_get_coords(self._p)
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
        C.path_clear_coords(self._p)

    def clear_visited(self):
        C.path_clear_visited(self._p)

    def copy(self):
        return c_path(raw_ptr=C.path_copy(self._p))

    def __eq__(self, other):
        return C.path_equal(self._p, other._p) != 0

    def __hash__(self):
        return C.path_hash(self._p)

    def __len__(self):
        return C.path_length(self._p)

    def __iter__(self):
        head = C.path_get_coords(self._p)
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
        C.path_append(self._p, other._p)

    def append_nodup(self, other):
        # void path_append_nodup(path dest, const path src);
        C.path_append_nodup(self.ptr(), other.ptr())

    def ptr(self):
        return self._p

    def __del__(self):
        # self.close()
        pass

    def close(self):
        if self._p:
            C.path_free(self._p)
            self._p = None        

    def __enter__(self):
        # with문이 시작될 때 호출
        return self  # 보통 self를 반환함

    def __exit__(self, exc_type, exc_val, exc_tb):
        # with문이 끝났을 때 호출됨
        # 여기서 자원 정리를 직접 수행
        self.close()

    def __repr__(self):
        return f"c_path(cost={self.cost:.3f}, success={self.success}, len={len(self)})"

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
        # coord path_look_at(path p, int index);
        return c_coord(raw_ptr=C.path_look_at(self._p, index))

    # def get_direction_enum(self, dxdy:c_coord):
    #     # int path_get_direction_enum(const coord dxdy);
    #     return C.path_get_direction_enum(dxdy.ptr())

    # def get_direction(self, index:int):
    #     # int path_get_direction(path p, int index);
    #     return C.path_get_direction(self._p, index)

    def get_direction_enum(self, dxdy: c_coord) -> PathDir:
        val = C.path_get_direction_enum(dxdy.ptr())
        return PathDir(val)

    def get_direction(self, index: int) -> PathDir:
        val = C.path_get_direction(self._p, index)
        return PathDir(val)

    def has_changed(self, start:c_coord, goal:c_coord,
                    anle_threshold_deg:float):
        # gboolean path_has_changed(
        #     path p, const coord from,
        #     const coord to, gfloat angle_threshold_deg);
        return C.path_has_changed(self._p, start, goal, anle_threshold_deg)

    def has_changed_with_angle(self, start:c_coord, goal:c_coord,
                    angle_threshold_deg:float):
        # gboolean path_has_changed_with_angle(
        #     path p,
        #     const coord from,
        #     const coord to,
        #     gfloat angle_threshold_deg,
        #     gfloat* out_angle_deg);
        
        out_angle_deg_ptr = ffi.new("float *")        
        result = C.path_has_changed_with_angle(self._p, start, goal,
            angle_threshold_deg, out_angle_deg_ptr)
        return result, out_angle_deg_ptr[0]

    def update_average_vector(self, start:c_coord, goal:c_coord):
        # void path_update_average_vector(
        #     path p, const coord from, const coord to);
        C.path_update_average_vector(self._p, start, goal)

    def get_coord_at(self, index:int):
        # coord path_get_coord_at(path p, int index);
        return c_coord(raw_ptr=C.path_get_coord_at(self._p, index))

    def update_average_vector_by_index(self, index_start:int, index_goal:int):
        # void path_update_average_vector_by_index(
        #     path p, int index_from, int index_to);
        C.path_update_average_vector_by_index(self._p, 
                                              index_start, index_goal)

    def has_changed_by_index(self, index_start:int, index_goal:int,
                             angle_threshold_deg:float):
        # gboolean path_has_changed_by_index(
        #     path p, int index_from, int index_to, gfloat angle_threshold_deg);
        return C.path_has_changed_by_index(self._p, index_start, index_goal,
                                           angle_threshold_deg)
    
    def has_changed_with_angle_by_index(self, index_start:int, index_goal:int,
                                        angle_threshold_deg:float):
        # gboolean path_has_changed_with_angle_by_index(
        #     path p,
        #     int index_from,
        #     int index_to,
        #     gfloat angle_threshold_deg,
        #     gfloat* out_angle_deg);
        
        out_angle_deg_ptr = ffi.new("float *")        
        result = C.path_has_changed_with_angle_by_index(self._p,
            index_start, index_goal, angle_threshold_deg, out_angle_deg_ptr)
        
        return result, out_angle_deg_ptr[0]
    
    def calc_average_facing(self, history:int=1):
        # path_dir_t path_calc_average_facing(path p, int history);
        return C.path_calc_average_facing(self._p, history)

def calc_direction(start:c_coord, goal:c_coord):
    # int calc_direction(const coord start, const coord goal);
    return C.calc_direction(start.ptr(), goal.ptr())

def direction_to_coord(direction: PathDir):
    return c_coord(raw_ptr=C.direction_to_coord(direction.value))
