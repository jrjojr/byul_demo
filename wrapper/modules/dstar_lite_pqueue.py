from ffi_core import ffi, C
from pathlib import Path
import os
import platform

from coord import c_coord
from dstar_lite_key import c_dstar_lite_key
from pqueue import c_pqueue

ffi.cdef("""
    typedef struct s_dstar_lite_pqueue { pqueue pq ; GHashTable * coord_to_key ; } * dstar_lite_pqueue;
         
    dstar_lite_pqueue dstar_lite_pqueue_new ( );
    void dstar_lite_pqueue_free ( dstar_lite_pqueue q );
    void dstar_lite_pqueue_push ( dstar_lite_pqueue q , const dstar_lite_key key , const coord c );
    coord dstar_lite_pqueue_peek ( dstar_lite_pqueue q );
    coord dstar_lite_pqueue_pop ( dstar_lite_pqueue q );
    int dstar_lite_pqueue_is_empty ( dstar_lite_pqueue q );
    int dstar_lite_pqueue_remove ( dstar_lite_pqueue q , const coord u );
    int dstar_lite_pqueue_remove_full ( dstar_lite_pqueue q , const dstar_lite_key key , const coord c );
    dstar_lite_key dstar_lite_pqueue_find_key_by_coord ( dstar_lite_pqueue q , const coord c );
    dstar_lite_key dstar_lite_pqueue_top_key ( dstar_lite_pqueue q );
    int dstar_lite_pqueue_contains ( dstar_lite_pqueue , const coord u );
""")

class c_dstar_lite_pqueue:
    def __init__(self, raw_ptr=None):
        if raw_ptr:
            self._c = raw_ptr
        else:
            self._c = C.dstar_lite_pqueue_new()

    def close(self):
        if self._c:
            C.dstar_lite_pqueue_free(self._c)
            self._c = None

    def __del__(self):
        self.close()

    def push(self, key, c):
        return C.dstar_lite_pqueue_push(self._c, key.ptr(), c.ptr())

    def peek(self):
        ptr = C.dstar_lite_pqueue_peek(self._c)
        return c_coord(raw_ptr=ptr) if ptr else None

    def pop(self):
        ptr = C.dstar_lite_pqueue_pop(self._c)
        return c_coord(raw_ptr=ptr) if ptr else None

    def is_empty(self) -> bool:
        return C.dstar_lite_pqueue_is_empty(self._c) != 0

    def remove(self, c):
        return C.dstar_lite_pqueue_remove(self._c, c.ptr()) != 0

    def remove_full(self, key, c):
        return C.dstar_lite_pqueue_remove_full(self._c, key.ptr(), c.ptr()) != 0

    def find_key_by_coord(self, c):
        ptr = C.dstar_lite_pqueue_find_key_by_coord(self._c, c.ptr())
        return c_dstar_lite_key(raw_ptr=ptr) if ptr else None

    def top_key(self):
        ptr = C.dstar_lite_pqueue_top_key(self._c)
        return c_dstar_lite_key(raw_ptr=ptr) if ptr else None

    def contains(self, c):
        return C.dstar_lite_pqueue_contains(self._c, c.ptr()) != 0

    def ptr(self):
        return self._c
