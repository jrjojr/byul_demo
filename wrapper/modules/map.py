from ffi_core import ffi, C
from pathlib import Path
import os
from typing import Any

from dict import c_dict

ffi.cdef("""
    typedef struct s_map* map;
    typedef struct s_tile* tile;
         
    typedef enum { MAP_NEIGHBOR_4 , MAP_NEIGHBOR_8 } map_neighbor_mode_t;
    // typedef struct { unsigned int8 type ; int8 height ; unsigned int8 flags ; unsigned int8 extra ; } tile_t;
    // typedef tile_t * tile;
    typedef struct s_map { int width ; int height ; int mode ; GHashTable * blocked_coords ; GHashTable * tiles ; tile default_tile ; } map_t;
    //  tile tile_new(void);
    // tile tile_new_full(unsigned int8 type, int8 height, unsigned int8 flags, unsigned int8 extra);
    //  void tile_free(tile t);
     map map_new(void);
     map map_new_full(int width, int height, int mode);
     void map_free(const map m);
     unsigned int map_hash(const map m);
     int map_equal(const map ma, const map mb);
     map map_copy(const map m);
     flud flud_new_map(const map m);
     flud flud_wrap_map(const map m);
     int flud_fetch_map(const flud d, map *out);
     const map flud_get_map(const flud d);
     int flud_set_map(flud d, const map m);
     int flud_is_map(const flud d);
     int map_get_width(const map m);
     void map_set_width(map m, int width);
     int map_get_height(const map m);
     void map_set_height(map m, int height);
     int map_get_neighbor_mode(const map m);
     void map_set_neighbor_mode(map m, int mode);
     const GHashTable* map_get_blocked_coords(const map m);
     int map_block_coord(map m, int x, int y);
     int map_unblock_coord(map m, int x, int y);
     int map_is_blocked(const map m, int x, int y);
     int map_is_inside(const map m, int x, int y);
     void map_clear(map m);
     // int map_set_tile(map m, coord c, const tile_t* tile);
     // unsigned int8 map_get_tile_type(const map m, int x, int y);
     // int8 map_get_tile_height(const map m, int x, int y);
     // unsigned int8 map_get_tile_flags(const map m, int x, int y);
     // unsigned int8 map_get_tile_extra(const map m, int x, int y);
""")

MAP_NEIGHBOR_4 = 0
MAP_NEIGHBOR_8 = 1

class c_map:
    def __init__(self, width=0, height=0, mode=1, raw_ptr=None):
        if raw_ptr:
            self._m = raw_ptr
        else:
            self._m = C.map_new_full(width, height, mode)

    @property
    def width(self):
        return C.map_get_width(self._m)

    @width.setter
    def width(self, value):
        C.map_set_width(self._m, value)

    @property
    def height(self):
        return C.map_get_height(self._m)

    @height.setter
    def height(self, value):
        C.map_set_height(self._m, value)

    @property
    def mode(self):
        return C.map_get_neighbor_mode(self._m)

    @mode.setter
    def mode(self, value):
        C.map_set_neighbor_mode(self._m, value)

    def is_inside(self, x: int, y: int) -> bool:
        return C.map_is_inside(self._m, x, y) != 0

    def is_blocked(self, x: int, y: int) -> bool:
        return C.map_is_blocked(self._m, x, y) != 0

    def block(self, x: int, y: int):
        return C.map_block_coord(self._m, x, y)

    def unblock(self, x: int, y: int):
        return C.map_unblock_coord(self._m, x, y)

    def clear(self):
        C.map_clear(self._m)

    def copy(self):
        return c_map(raw_ptr=C.map_copy(self._m))

    def __eq__(self, other):
        return C.map_equal(self._m, other._m) != 0

    def __hash__(self):
        return C.map_hash(self._m)

    def ptr(self):
        return self._m

    def __del__(self):
        # C.map_free(self._m)
        pass

    def close(self):
        if self._m:
            C.map_free(self._m)
            self._m = None        

    def __enter__(self):
        # with문이 시작될 때 호출
        return self  # 보통 self를 반환함

    def __exit__(self, exc_type, exc_val, exc_tb):
        # with문이 끝났을 때 호출됨
        # 여기서 자원 정리를 직접 수행
        self.close()    

    def __repr__(self):
        return f"c_map({self.width}x{self.height}, mode={self.mode})"

    def get_blocked_coords(self):
        ptr = C.map_get_blocked_coords(self.ptr())
        if ptr == ffi.NULL:
            return None
        return c_dict.from_ptr(ptr)
