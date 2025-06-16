from ffi_core import ffi, C
from pathlib import Path
import os
import platform

ffi.cdef("""
    typedef struct s_dstar_lite_key { float k1 ; float k2 ; } dstar_lite_key_t;
    typedef dstar_lite_key_t * dstar_lite_key;
    dstar_lite_key dstar_lite_key_new ( void );
    dstar_lite_key dstar_lite_key_new_full ( float k1 , float k2 );
    dstar_lite_key dstar_lite_key_copy ( dstar_lite_key key );
    void dstar_lite_key_free ( dstar_lite_key key );
    int dstar_lite_key_compare ( const dstar_lite_key dsk0 , const dstar_lite_key dsk1 );
    int dstar_lite_key_compare_raw ( const void* a , const void* b , void* userdata );
""")

class c_dstar_lite_key:
    def __init__(self, raw_ptr=None):
        if raw_ptr:
            self._c = raw_ptr
        else:
            self._c = C.dstar_lite_key_new()

    @classmethod
    def from_values(cls, k1, k2):
        ptr = C.dstar_lite_key_new_full(k1, k2)
        return cls(raw_ptr=ptr)

    def close(self):
        if self._c:
            C.dstar_lite_key_free(self._c)
            self._c = None

    def __del__(self):
        self.close()

    def copy(self):
        return c_dstar_lite_key(raw_ptr=C.dstar_lite_key_copy(self._c))

    def compare(self, other):
        return C.dstar_lite_key_compare(self._c, other._c)

    @staticmethod
    def compare_raw(a, b, userdata=None):
        return C.dstar_lite_key_compare_raw(a, b, userdata)

    def ptr(self):
        return self._c

    def __lt__(self, other):
        return self.compare(other) < 0

    def __eq__(self, other):
        return self.compare(other) == 0

    def __repr__(self):
        return f"c_dstar_lite_key(ptr={self._c})"
