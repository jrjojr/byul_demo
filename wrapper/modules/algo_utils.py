from ffi_core import ffi, C
from pathlib import Path
import os
from typing import Any

from map import c_map
from coord import c_coord
# from dstar_lite import dstar_lite_config

ffi.cdef("""
     void map_print_ascii(const map m);
         
    void map_print_ascii_with_path(const map m,
        const path p, const coord start, const coord goal);

    void map_print_ascii_with_visited_path(const map m,
        const path p, const coord start, const coord goal);

    void map_print_ascii_with_visited_count(const map m,
        const path p, const coord start, const coord goal);

""")

class c_map_debug:
    @staticmethod
    def print_ascii(map0):
        return C.map_print_ascii(map0.ptr())

    @staticmethod
    def print_with_path(map0, path0, start, goal):
        return C.map_print_ascii_with_path(map0.ptr(), path0.ptr(), 
                                           start.ptr(), goal.ptr())
    
    @staticmethod
    def print_ascii_with_visited_path(map0, path0, start, goal):
        return C.map_print_ascii_with_visited_path(map0.ptr(), path0.ptr(), 
                                                   start.ptr(), goal.ptr())    
    
    @staticmethod
    def print_ascii_with_visited_count(map0, path0, start, goal):
        return C.map_print_ascii_with_visited_count(map0.ptr(), path0.ptr(), 
                                                    start.ptr(), goal.ptr())        
