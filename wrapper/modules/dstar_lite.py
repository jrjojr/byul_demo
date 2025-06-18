from ffi_core import ffi, C

from pathlib import Path
import os
import platform

from typing import Any

from map import c_map
from route import c_route
from coord import c_coord
from dstar_lite_pqueue import c_dstar_lite_pqueue
from dstar_lite_key import c_dstar_lite_key

ffi.cdef("""
    typedef gfloat (*dsl_cost_func)(
        const map m, const coord start, const coord goal, gpointer userdata);

    typedef gfloat (*dsl_heuristic_func)(
        const coord start, const coord goal);

    typedef gboolean (*dsl_is_blocked_func)(
        const map m, gint x, gint y, gpointer userdata);

         
    typedef void (*move_func)(const coord c, gpointer userdata);
         
    typedef GList* (*changed_coords_func)(gpointer userdata);
         
    typedef struct s_dstar_lite* dstar_lite;
         

    gfloat dstar_lite_cost(
        const map m, const coord start, const coord goal, gpointer userdata);         

    gfloat dstar_lite_heuristic ( const coord start , const coord goal );
         
    dstar_lite dstar_lite_new ( map m );
         
    dstar_lite dstar_lite_new_full ( 
         map m , dsl_cost_func cost_fn , dsl_heuristic_func heuristic_fn , 
         int debug_mode_enabled);

    void dstar_lite_free ( dstar_lite dsl );
    coord dstar_lite_get_start ( const dstar_lite dsl );
    void dstar_lite_set_start ( dstar_lite dsl , const coord c );
    coord dstar_lite_get_goal ( const dstar_lite dsl );
    void dstar_lite_set_goal ( dstar_lite dsl , const coord c );
    GHashTable * dstar_lite_get_g_table ( const dstar_lite dsl );
    GHashTable * dstar_lite_get_rhs_table ( const dstar_lite dsl );
    dstar_lite_pqueue dstar_lite_get_frontier ( const dstar_lite dsl );
         
    void dstar_lite_set_frontier ( 
         dstar_lite dsl , dstar_lite_pqueue frontier );

    float dstar_lite_get_km ( const dstar_lite dsl );
    void dstar_lite_set_km ( dstar_lite dsl , float km );
         
    int dstar_lite_get_max_range ( const dstar_lite dsl );
    void dstar_lite_set_max_range ( dstar_lite dsl , int value );
         
    int dstar_lite_get_debug_mode_enabled ( const dstar_lite dsl );
    void dstar_lite_set_debug_mode_enabled ( dstar_lite dsl , int enabled );
         
    GHashTable * dstar_lite_get_update_count_table ( const dstar_lite dsl );
    void dstar_lite_add_update_count ( dstar_lite dsl , const coord c );
    void dstar_lite_clear_update_count ( dstar_lite dsl );
    int dstar_lite_get_update_count ( dstar_lite dsl , const coord c );
         
    void dstar_lite_set_cost_func(
        dstar_lite dsl, dsl_cost_func fn, gpointer userdata);         

    dsl_cost_func dstar_lite_get_cost_func ( const dstar_lite dsl );
         
    void dstar_lite_set_heuristic_func ( 
         dstar_lite dsl , dsl_heuristic_func func );

    dsl_heuristic_func dstar_lite_get_heuristic_func ( const dstar_lite dsl );
         
    const map dstar_lite_get_map ( const dstar_lite dsl );
         
    const route dstar_lite_get_proto_route(const dstar_lite dsl);
         
    const route dstar_lite_get_real_route(const dstar_lite dsl);
         
    void dstar_lite_reset ( dstar_lite dsl );

gint   dstar_lite_get_real_loop_max_retry(const dstar_lite dsl);
void   dstar_lite_set_real_loop_max_retry(
    dstar_lite dsl, gint value);
gint dstar_lite_real_loop_retry_count(dstar_lite dsl);

// 10x10의 맵에서 100은 되어야 잘 찾는거 같다.
gint dstar_lite_get_compute_max_retry(const dstar_lite dsl);
void dstar_lite_set_compute_max_retry(
    const dstar_lite dsl, gint v);

gint dstar_lite_proto_compute_retry_count(dstar_lite dsl);

gint dstar_lite_real_compute_retry_count(dstar_lite dsl);

// proto route 생성할때 reconstruct_route한다. 여기에 사용하는 루프
// 10x10에서 100은 오버고 10은 너무 작고 대충 40 정도면 되겠다.
gint dstar_lite_get_reconstruct_max_retry(const dstar_lite dsl);
void dstar_lite_set_reconstruct_max_retry(
    const dstar_lite dsl, gint v);
gint dstar_lite_reconstruct_retry_count(dstar_lite dsl);

                  
    gint dstar_lite_get_interval_msec(dstar_lite dsl);

    void dstar_lite_set_interval_msec(dstar_lite dsl, gint interval_msec);
                  
    // 루프 내 move_fn 설정/조회
    move_func dstar_lite_get_move_func(const dstar_lite dsl);

    void dstar_lite_set_move_func(dstar_lite dsl, move_func fn);

    gpointer dstar_lite_get_move_func_userdata(const dstar_lite dsl);

    void dstar_lite_set_move_func_userdata(
        dstar_lite dsl, gpointer userdata);

    // 루프 내 changed_coords_fn 설정/조회
    changed_coords_func dstar_lite_get_changed_coords_func(
        const dstar_lite dsl);

    void dstar_lite_set_changed_coords_func(
        dstar_lite dsl, changed_coords_func fn);

    gpointer dstar_lite_get_changed_coords_func_userdata(
        const dstar_lite dsl);

    void dstar_lite_set_changed_coords_func_userdata(
        dstar_lite dsl, gpointer userdata);

    void dstar_lite_init ( dstar_lite dsl );
         
    void dstar_lite_update_vertex ( const dstar_lite dsl , const coord u );
         
    void dstar_lite_update_vertex_range ( 
         const dstar_lite dsl , const coord s , int max_range );

    void dstar_lite_update_vertex_auto_range ( 
         const dstar_lite dsl , const coord s );

    void dstar_lite_compute_shortest_route ( dstar_lite dsl );
    route dstar_lite_reconstruct_route ( const dstar_lite dsl );
         
    route dstar_lite_find ( const dstar_lite dsl );
         
    void dstar_lite_find_proto(const dstar_lite dsl);

    void dstar_lite_find_loop(const dstar_lite dsl);
                  
    void dstar_lite_update_vertex_by_route ( dstar_lite dsl , route p );
         
    // 루프를 강제종료한다.
    void dstar_lite_force_quit(dstar_lite dsl);         
         
    gboolean dstar_lite_is_quit_forced(dstar_lite dsl);
         
    void dstar_lite_set_force_quit(dstar_lite dsl, gboolean v);         
         
    void move_to(const coord c, gpointer userdata);

    GList* get_changed_coords(gpointer userdata);
         

    gboolean dstar_lite_is_blocked(
        dstar_lite dsl, gint x, gint y, gpointer userdata);    
         
dsl_is_blocked_func dstar_lite_get_is_blocked_func(dstar_lite dsl);
                  
void dstar_lite_set_is_blocked_func(
    dstar_lite dsl, dsl_is_blocked_func fn, gpointer userdata);         
         
""")

# dstar_lite_cost = C.dstar_lite_cost 
DSTAR_LITE_COST = C.dstar_lite_cost
# dstar_lite_heuristic = C.dstar_lite_heuristic 
DSTAR_LITE_HEURISTIC = C.dstar_lite_heuristic 

MOVE_TO = C.move_to
CHANGE_COORDS = C.get_changed_coords

class c_dstar_lite:
    def __init__(self, raw_ptr=None):
        if raw_ptr:
            self._c = raw_ptr
        else:
            raise ValueError("기본 생성자는 지원되지 않습니다. "
                             "from_values 또는 from_map을 사용하세요.")

    @classmethod
    def from_map(cls, m:c_map):
        ptr = C.dstar_lite_new(m.ptr())
        return cls(raw_ptr=ptr)

    @classmethod
    def from_values(cls, map_m:c_map, start:c_coord, goal:c_coord, km:float, 
        max_range:int, real_loop_max_retry:int, 
        cost_fn:Any, heuristic_fn:Any, debug_mode_enabled:bool, userdata:Any):

        ptr = C.dstar_lite_new_full(map_m.ptr(), start.ptr(), goal.ptr(), km, 
            max_range, real_loop_max_retry, 
            cost_fn, heuristic_fn, debug_mode_enabled, userdata)
        
        return cls(raw_ptr=ptr)
    
    def ptr(self):
        return self._c

    def close(self):
        if self._c:
            C.dstar_lite_free(self._c)
            self._c = None

    def __del__(self):
        self.close()

    def __enter__(self):
        # with문이 시작될 때 호출
        return self  # 보통 self를 반환함

    def __exit__(self, exc_type, exc_val, exc_tb):
        # with문이 끝났을 때 호출됨
        # 여기서 자원 정리를 직접 수행
        self.close()        

    @property
    def start(self):
        return c_coord(raw_ptr=C.dstar_lite_get_start(self._c))

    @start.setter
    def start(self, value:c_coord):
        C.dstar_lite_set_start(self._c, value.ptr())

    @property
    def goal(self):
        return c_coord(raw_ptr=C.dstar_lite_get_goal(self._c))

    @goal.setter
    def goal(self, value:c_coord):
        C.dstar_lite_set_goal(self._c, value.ptr())

    @property
    def g_table(self):
        return C.dstar_lite_get_g_table(self._c)

    @property
    def rhs_table(self):
        return C.dstar_lite_get_rhs_table(self._c)

    @property
    def frontier(self):
        return c_dstar_lite_pqueue(raw_ptr=C.dstar_lite_get_frontier(self._c))

    @frontier.setter
    def frontier(self, value:c_dstar_lite_pqueue):
        C.dstar_lite_set_frontier(self._c, value.ptr())

    @property
    def km(self):
        return C.dstar_lite_get_km(self._c)

    @km.setter
    def km(self, value:float):
        C.dstar_lite_set_km(self._c, value)

    @property
    def max_range(self):
        return C.dstar_lite_get_max_range(self._c)

    @max_range.setter
    def max_range(self, value:int):
        C.dstar_lite_set_max_range(self._c, value)

    @property
    def debug_mode_enabled(self):
        return C.dstar_lite_get_debug_mode_enabled(self._c)

    @debug_mode_enabled.setter
    def debug_mode_enabled(self, value):
        C.dstar_lite_set_debug_mode_enabled(self._c, value)

    @property
    def update_count_table(self):
        return C.dstar_lite_get_update_count_table(self._c)

    @property
    def cost_func(self):
        return C.dstar_lite_get_cost_func(self._c)

    @cost_func.setter
    def cost_func(self, func, userdata):
        # void dstar_lite_set_cost_func(
        #     dstar_lite dsl, dsl_cost_func fn, gpointer userdata);
        C.dstar_lite_set_cost_func(self._c, func, userdata)

    @property
    def is_blocked_func(self):
        # void dstar_lite_get_is_blocked_func(
        #     dstar_lite dsl);
        return C.dstar_lite_get_is_blocked_func(self.ptr())
    
    @is_blocked_func.setter
    def is_blocked_func(self, func, userdata):
        # void dstar_lite_set_is_blocked_func(
        #     dstar_lite dsl, dsl_is_blocked_func fn, gpointer userdata);
        return C.dstar_lite_set_is_blocked_func(self.ptr(), func, userdata)
    
    @property
    def heuristic_func(self):
        return C.dstar_lite_get_heuristic_func(self._c)

    @heuristic_func.setter
    def heuristic_func(self, value):
        C.dstar_lite_set_heuristic_func(self._c, value)

    @property
    def map(self):
        return c_map(raw_ptr=C.dstar_lite_get_map(self._c))


    @property
    def real_loop_max_retry(self):
        # gint   dstar_lite_get_real_loop_max_retry(const dstar_lite dsl);
        return C.dstar_lite_get_real_loop_max_retry(self.ptr())

    @real_loop_max_retry.setter
    def real_loop_max_retry(self, value:int):
        # void   dstar_lite_set_real_loop_max_retry(
        #     dstar_lite dsl, gint value);
        C.dstar_lite_set_real_loop_max_retry(self.ptr(), value)

    @property
    def compute_max_retry(self):
        # // 10x10의 맵에서 100은 되어야 잘 찾는거 같다.
        # gint dstar_lite_get_compute_max_retry(const dstar_lite dsl);
        return C.dstar_lite_get_compute_max_retry(self.ptr())

    @compute_max_retry.setter
    def compute_max_retry(self, value:int):
        # void dstar_lite_set_compute_max_retry(
        #     const dstar_lite dsl, gint v);
        C.dstar_lite_set_compute_max_retry(self.ptr(), value)

    @property
    def reconstruct_max_retry(self):
        # // proto route 생성할때 reconstruct_route한다. 여기에 사용하는 루프
        # // 10x10에서 100은 오버고 10은 너무 작고 대충 40 정도면 되겠다.
        # gint dstar_lite_get_reconstruct_max_retry(const dstar_lite dsl);
        return C.dstar_lite_get_reconstruct_max_retry(self.ptr())

    @reconstruct_max_retry.setter
    def reconstruct_max_retry(self, value:int):
        # void dstar_lite_set_reconstruct_max_retry(
        #     const dstar_lite dsl, gint v);
        C.dstar_lite_set_reconstruct_max_retry(self.ptr(), value)

    @property
    def proto_compute_retry_count(self):
        # gint dstar_lite_proto_compute_retry_count(dstar_lite dsl);
        return C.dstar_lite_proto_compute_retry_count(self.ptr())

    @property
    def real_compute_retry_count(self):
        # gint dstar_lite_real_compute_retry_count(dstar_lite dsl);
        return C.dstar_lite_real_compute_retry_count(self.ptr())

    @property
    def real_loop_retry_count(self):
        # gint dstar_lite_real_loop_retry_count(dstar_lite dsl);
        return C.dstar_lite_real_loop_retry_count(self.ptr())

    @property
    def reconstruct_retry_count(self):
        # gint dstar_lite_reconstruct_retry_count(dstar_lite dsl);         
        return C.dstar_lite_reconstruct_retry_count(self.ptr())


    @property
    def interval_msec(self):
        # gint dstar_lite_get_interval_msec(dstar_lite dsl);
        return C.dstar_lite_get_interval_msec(self.ptr())

    @interval_msec.setter
    def interval_msec(self, msec:int):
        # void dstar_lite_set_interval_msec(dstar_lite dsl, gint interval_msec);    
        C.dstar_lite_set_interval_msec(self.ptr(), msec)

    @property
    def move_func(self):
        # move_func dstar_lite_get_move_func(const dstar_lite dsl);        
        return C.dstar_lite_get_move_func(self._c)

    @move_func.setter
    def move_func(self, func):
        # void dstar_lite_set_move_func(dstar_lite dsl, move_func fn);        
        C.dstar_lite_set_move_func(self._c, func)
   
    @property
    def move_func_userdata(self):
        # gpointer dstar_lite_get_move_func_userdata(const dstar_lite dsl);        
        return C.dstar_lite_get_move_func_userdata(self._c)
    
    @move_func_userdata.setter
    def move_func_userdata(self, userdata):
        # void dstar_lite_set_move_func_userdata(
        #     dstar_lite dsl, gpointer userdata);
        C.dstar_lite_set_move_func_userdata(self.ptr(), userdata)

    @property
    def changed_coords_func(self):
        # // 루프 내 changed_coords_fn 설정/조회
        # changed_coords_func dstar_lite_get_changed_coords_func(
        #     const dstar_lite dsl);        
        return C.dstar_lite_get_changed_coords_func(self._c)

    @changed_coords_func.setter
    def changed_coords_func(self, func):
        # void dstar_lite_set_changed_coords_func(
        #     dstar_lite dsl, changed_coords_func fn);
        C.dstar_lite_set_changed_coords_func(
            self._c, func)

    # @changed_coords_func.setter
    # def changed_coords_func(self, value):
    #     func, userdata = value
    #     C.dstar_lite_set_changed_coords_func(self._c, func, userdata)   

    @property
    def changed_coords_func_userdata(self):
        # gpointer dstar_lite_get_changed_coords_func_userdata(
        # const dstar_lite dsl);

        return C.dstar_lite_get_changed_coords_func_userdata(self._c)    

    @changed_coords_func_userdata.setter
    def changed_coords_func_userdata(self, userdata):
        # void dstar_lite_set_changed_coords_func_userdata(
        #     dstar_lite dsl, gpointer userdata);
        C.dstar_lite_set_changed_cooords_func_userdata(
            self.ptr(), userdata)

    def add_update_count(self, c):
        C.dstar_lite_add_update_count(self._c, c)

    def clear_update_count(self):
        C.dstar_lite_clear_update_count(self._c)

    def get_update_count(self, c):
        return C.dstar_lite_get_update_count(self._c, c)

    def reset(self):
        C.dstar_lite_reset(self._c)

    def calculate_key(self, s:c_coord):
        return c_dstar_lite_key(C.dstar_lite_calculate_key(self._c, s.ptr()))

    def init(self):
        C.dstar_lite_init(self._c)

    def update_vertex(self, u:c_coord):
        C.dstar_lite_update_vertex(self._c, u.ptr())

    def update_vertex_range(self, s:c_coord, max_range):
        C.dstar_lite_update_vertex_range(self._c, s.ptr(), max_range)

    def update_vertex_auto_range(self, s:c_coord):
        C.dstar_lite_update_vertex_auto_range(self._c, s.ptr())

    def compute_shortest_route(self):
        C.dstar_lite_compute_shortest_route(self._c)

    def reconstruct_route(self):
        return c_route(raw_ptr=C.dstar_lite_reconstruct_route(self._c))

    def find(self):
        return c_route(raw_ptr=C.dstar_lite_find(self._c))

    def find_proto(self):
        # void dstar_lite_find_proto(const dstar_lite dsl);
        C.dstar_lite_find_proto(self.ptr())

    def find_loop(self):
        # void dstar_lite_find_loop(const dstar_lite dsl);
        C.dstar_lite_find_loop(self.ptr())

    def update_vertex_by_route(self, p:c_route):
        C.dstar_lite_update_vertex_by_route(self._c, p.ptr())

    def block_coord(self, x, y):
        self.map.block(x, y)

    def unblock_coord(self, x, y):
        self.map.unblock(x, y)        

    def get_proto_route(self):
        # const route dstar_lite_get_proto_route(const dstar_lite dsl);
        return c_route(raw_ptr=C.dstar_lite_get_proto_route(self.ptr()))
    
    def get_real_route(self):
        # const route dstar_lite_get_real_route(const dstar_lite dsl);
        return c_route(raw_ptr=C.dstar_lite_get_real_route(self.ptr()))    

    def force_quit(self):    
        # // 루프를 강제종료한다.
        # void dstar_lite_force_quit(dstar_lite dsl);    
        C.dstar_lite_force_quit(self.ptr())

    def is_quit_forced(self):
        # gboolean dstar_lite_is_quit_forced(dstar_lite dsl);
        return C.dstar_lite_is_quit_forced(self.ptr())

    def set_force_quit(self, v:bool):
        # void dstar_lite_set_force_quit(dstar_lite dsl, gboolean v);         
        C.dstar_lite_set_force_quit(self.ptr(), v)
