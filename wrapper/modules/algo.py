from ffi_core import ffi, C
from pathlib import Path
import os
from typing import Any

from coord import c_coord
from path import c_path
from map import c_map
# from algo_utils import c_map_debug

ffi.cdef("""
    typedef struct s_algo* algo;
    
    // typedef struct s_map* map;
         
    // typedef struct s_path* path;
    // typedef struct s_coord* coord;

    float default_cost(const map m, const coord start, const coord goal, void* userdata);
    float zero_cost(const map m, const coord start, const coord goal, void* userdata);
    float terrain_cost(const map m, const coord start, const coord goal, void* userdata);
    float diagonal_cost(const map m, const coord start, const coord goal, void* userdata);
    float height_cost(const map m, const coord start, const coord goal, void* userdata);
    float euclidean_heuristic(const coord start, const coord goal, void* userdata);
    float manhattan_heuristic(const coord start, const coord goal, void* userdata);
    float chebyshev_heuristic(const coord start, const coord goal, void* userdata);
    float default_heuristic(const coord start, const coord goal, void* userdata);                  

    typedef enum { PATH_ALGO_UNKNOWN = 0 , PATH_ALGO_BFS , PATH_ALGO_DFS , PATH_ALGO_DIJKSTRA , PATH_ALGO_ASTAR , PATH_ALGO_WEIGHTED_ASTAR , PATH_ALGO_GREEDY_BEST_FIRST , PATH_ALGO_IDA_STAR , PATH_ALGO_RTA_STAR , PATH_ALGO_SMA_STAR , PATH_ALGO_FAST_MARCHING , PATH_ALGO_FRINGE_SEARCH , PATH_ALGO_DSTAR_LITE , PATH_ALGO_DYNAMIC_ASTAR , PATH_ALGO_LPA_STAR , PATH_ALGO_HPA_STAR , PATH_ALGO_ANY_ANGLE_ASTAR , PATH_ALGO_ALT , PATH_ALGO_THETA_STAR , PATH_ALGO_LAZY_THETA_STAR , PATH_ALGO_JUMP_POINT_SEARCH , PATH_ALGO_JPS_PLUS , PATH_ALGO_BIDIRECTIONAL_ASTAR } path_algotype_t;
    typedef enum { FRONTIER_QUEUE , FRONTIER_PRIORQ } frontier_type_t;

    typedef struct s_algo { map m ; int algotype ; int frontier_type ; void* algo_find_fn ; void* cost_fn ; void* heuristic_fn ; void* userdata ; void* algo_specific ; coord start ; coord goal ; GHashTable * visited ; GHashTable * came_from ; GHashTable * cost_so_far ; void* frontier ; int visited_logging ; } algo_t;
    typedef struct s_coord_pq { coord c ; float priority ; } coord_pq_t;
    typedef coord_pq_t * coord_pq;
    
         // typedef float (*cost_func)( const map m, const coord start, const coord goal, void* userdata);
    // typedef float (*heuristic_func)( const coord start, const coord goal, void* userdata);
    // typedef path (*algo_find_func)( const algo al, const coord start, const coord goal);
         
    // float dstar_lite_cost(void* m, coord a, coord b, void* userdata);    
    // float default_heuristic(coord a, coord b, void* userdata);
         
     algo algo_new(void);
    algo algo_new_default( int width, int height, int algotype, int visited_logging );
    algo algo_new_full( int width, int height, int mode,  int algotype, void* cost_fn, void* heuristic_fn, void* userdata, void* algo_specific, int visited_logging );
     void algo_free(algo al);
     void algo_free_full(algo al, GDestroyNotify specific_free_func);
     path algo_find(const algo al, const coord start, const coord goal);
     path algo_refind(const algo al, const coord start, const coord goal);
     void algo_set_heuristic_func(algo al, void* func);
     void algo_set_userdata(algo al, void* userdata);
     void algo_set_algo_specific(algo al, void* specific);
     void* algo_get_heuristic_func(const algo al);
     void* algo_get_userdata(const algo al);
     void* algo_get_algo_specific(const algo al);
     const map algo_get_map(const algo al);
     void algo_reset(algo al);
     coord algo_pop_frontier(algo al);
     void     algo_prepend_frontier(algo al, const coord c);
     coord    algo_pop_frontier_head(algo al);
     void     algo_free_frontier(algo al);
     void algo_trim_frontier(algo al);
     int algo_frontier_size(const algo al);
     int algo_remove_frontier(algo al, void* coord_or_coord_pq);
     int algo_contains_came_from(const algo al, const coord key);
     coord    algo_lookup_came_from(const algo al, const coord key);
     void     algo_add_visited(algo al, const coord c);
    int algo_get_cost_so_far(const algo al, const coord c, float* out);
     void     free_coord_list(GList* list);
     int get_frontier_type(int algotype);
     // algo_find_func get_algo_find_func(int algotype);
    void algo_reconstruct_path(const algo al, path result, coord start, coord goal);
     coord_pq coord_pq_new();
     coord_pq coord_pq_new_full(const coord c, float prior);
     GList* append_coord_pq_to_list(GList* gl, coord_pq cp);
     void coord_pq_free(coord_pq cp);
    int coord_pq_compare( const void* coord_pq_a, const void* coord_pq_b);
        
""")

# heuristic_fn = C.default_heuristic

DEFAULT_COST = C.default_cost
TERRAIN_COST = C.terrain_cost
DIAGONAL_COST = C.diagonal_cost
HEIGHT_COST = C.height_cost
ZERO_COST = C.zero_cost

DEFAULT_HEURISTIC = C.default_heuristic
EUCLIDEAN_HEURISTIC = C.euclidean_heuristic
MANHATTAN_HEURISTIC = C.manhattan_heuristic
CHEBYSHEV_HEURISTIC = C.chebyshev_heuristic

def algo_set_heuristic_func(al: Any, func: Any) -> None:
    return C.algo_set_heuristic_func(al, func)


def algo_set_userdata(al: Any, userdata: None) -> None:
    return C.algo_set_userdata(al, userdata)


def algo_set_algo_specific(al: Any, specific: None) -> None:
    return C.algo_set_algo_specific(al, specific)


# def algo_get_heuristic_func(al: Any) -> Any:
#     return C.algo_get_heuristic_func(al)


def algo_get_userdata(al: Any) -> None:
    return C.algo_get_userdata(al)


def algo_get_algo_specific(al: Any) -> None:
    return C.algo_get_algo_specific(al)


def algo_pop_frontier(al: Any) -> Any:
    return C.algo_pop_frontier(al)


def algo_prepend_frontier(al: Any, c: Any) -> None:
    return C.algo_prepend_frontier(al, c)


def algo_pop_frontier_head(al: Any) -> Any:
    return C.algo_pop_frontier_head(al)


def algo_free_frontier(al: Any) -> None:
    return C.algo_free_frontier(al)


def algo_trim_frontier(al: Any) -> None:
    return C.algo_trim_frontier(al)


def algo_frontier_size(al: Any) -> int:
    return C.algo_frontier_size(al)


def algo_remove_frontier(al: Any, coord_or_coord_pq: None) -> int:
    return C.algo_remove_frontier(al, coord_or_coord_pq)


def free_coord_list(list: Any) -> None:
    return C.free_coord_list(list)


def get_frontier_type(algotype: Any) -> Any:
    return C.get_frontier_type(algotype)

def algo_reconstruct_path(al: Any, result: Any, start: Any, goal: Any) -> None:
    return C.algo_reconstruct_path(al, result, start, goal)


def coord_pq_new() -> Any:
    return C.coord_pq_new()


def coord_pq_new_full(c: Any, prior: float) -> Any:
    return C.coord_pq_new_full(c, prior)


def append_coord_pq_to_list(gl: Any, cp: Any) -> Any:
    return C.append_coord_pq_to_list(gl, cp)


def coord_pq_free(cp: Any) -> None:
    return C.coord_pq_free(cp)


def coord_pq_compare(coord_pq_a: None, coord_pq_b: None) -> int:
    return C.coord_pq_compare(coord_pq_a, coord_pq_b)

class c_algo:
    def __init__(self, width: int, height: int, mode: int, algotype: int,
                 cost_fn, heuristic_fn, userdata=None, algo_specific=None,
                 visited_logging=False):
        self._c = C.algo_new_full(width, height, mode, algotype,
                                  cost_fn, heuristic_fn,
                                  userdata, algo_specific,
                                  int(visited_logging))

    def __del__(self):
        # if self._c:
        #     C.algo_free(self._c)
        pass

    def close(self):
        if self._c:
            C.algo_free(self._c)
            self._c = None        

    def __enter__(self):
        # with문이 시작될 때 호출
        return self  # 보통 self를 반환함

    def __exit__(self, exc_type, exc_val, exc_tb):
        # with문이 끝났을 때 호출됨
        # 여기서 자원 정리를 직접 수행
        self.close()

    def ptr(self):
        return self._c

    def find(self, start: c_coord, goal: c_coord) -> c_path:
        p = C.algo_find(self._c, start.ptr(), goal.ptr())
        return c_path(raw_ptr=p)

    def reset(self):
        C.algo_reset(self._c)

    def get_map(self) -> c_map:
        m = C.algo_get_map(self._c)
        return c_map(raw_ptr=m)

    def frontier_size(self) -> int:
        return C.algo_frontier_size(self._c)

    def contains_came_from(self, coord: c_coord) -> bool:
        return bool(C.algo_contains_came_from(self._c, coord.ptr()))

    def lookup_came_from(self, coord: c_coord) -> c_coord:
        c = C.algo_lookup_came_from(self._c, coord.ptr())
        return c_coord(raw_ptr=c)

    def add_visited(self, coord: c_coord):
        C.algo_add_visited(self._c, coord.ptr())

    def get_cost_so_far(self, coord: c_coord) -> float:
        out = ffi.new("float*")
        success = C.algo_get_cost_so_far(self._c, coord.ptr(), out)
        return out[0] if success else float("inf")