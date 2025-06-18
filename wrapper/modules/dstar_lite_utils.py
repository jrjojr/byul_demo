from ffi_core import ffi, C
from pathlib import Path
import os
import platform

from dstar_lite import c_dstar_lite
from route import c_route
from map import c_map
from coord import c_coord
from dstar_lite_pqueue import c_dstar_lite_pqueue

ffi.cdef("""
    void print_all_g_table_internal ( const map m , GHashTable * g_table );
    void print_all_rhs_table_internal ( const map m , GHashTable * rhs_table );
    void print_all_dsl_internal_full ( const map m , const coord start , const coord goal , float km , GHashTable * g_table , GHashTable * rhs_table , dstar_lite_pqueue frontier , int max_range , int real_loop_max_retry , int debug_mode_enabled , GHashTable * update_count_table );
    void print_all_dsl_internal ( const map m , const coord start , const coord goal , float km , GHashTable * g_table , GHashTable * rhs_table , dstar_lite_pqueue frontier );
    void print_all_dsl ( const dstar_lite dsl );
    void dsl_print_ascii_only_map ( const dstar_lite dsl );
    void dsl_print_ascii ( const dstar_lite dsl , const route p );
    void dsl_print_ascii_uv ( const dstar_lite dsl , const route p );
""")

class c_dstar_lite_utils:
    @staticmethod
    def print_all_g_table_internal(m:c_map, g_table):
        C.print_all_g_table_internal(m.ptr(), g_table)

    @staticmethod
    def print_all_rhs_table_internal(m:c_map, rhs_table):
        C.print_all_rhs_table_internal(m.ptr(), rhs_table)

    @staticmethod
    def print_all_dsl_internal_full(m:c_map, start:c_coord, goal:c_coord, 
                                    km, g_table, rhs_table,
                                    frontier:c_dstar_lite_pqueue, 
                                    max_range, real_loop_max_retry,
                                    debug_mode_enabled, update_count_table):
        C.print_all_dsl_internal_full(
            m.ptr(), start.ptr(), goal.ptr(), km, g_table, rhs_table,
            frontier, max_range, real_loop_max_retry, debug_mode_enabled,
            update_count_table
        )

    @staticmethod
    def print_all_dsl_internal(m:c_map, start:c_coord, goal:c_coord, km, 
                               g_table, rhs_table, frontier):
        
        C.print_all_dsl_internal(m.ptr(), start.ptr(), goal.ptr(), 
                                 km, g_table, rhs_table, frontier)

    @staticmethod
    def print_all_dsl(dsl:c_dstar_lite):
        C.print_all_dsl(dsl.ptr())

    @staticmethod
    def print_ascii_only_map(dsl:c_dstar_lite):
        C.dsl_print_ascii_only_map(dsl.ptr())

    @staticmethod
    def print_ascii(dsl:c_dstar_lite, p:c_route):
        C.dsl_print_ascii(dsl.ptr(), p.ptr())

    @staticmethod
    def print_ascii_uv(dsl:c_dstar_lite, p:c_route):
        C.dsl_print_ascii_uv(dsl.ptr(), p.ptr())
