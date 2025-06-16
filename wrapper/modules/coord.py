


from ffi_core import ffi, C
from pathlib import Path
import os
from typing import Any

ffi.cdef("""

             typedef struct s_coord* coord;
    typedef struct s_coord { int x ; int y ; } coord_t;
     
    coord    coord_new_full(int x, int y);
     coord    coord_new();
     void     coord_free(coord c);
     unsigned int coord_hash(const coord c);
     int coord_equal(const coord c1, const coord c2);
     coord coord_copy(const coord c);
     flud flud_new_coord(const coord s);
     flud flud_wrap_coord(const coord s);
     int flud_fetch_coord(const flud d, coord *out);
     const coord flud_get_coord(const flud d);
     int flud_set_coord(flud d, const coord s);
     int flud_is_coord(const flud d);
     int     coord_get_x(const coord c);
     void     coord_set_x(coord c, int x);
     int     coord_get_y(const coord c);
     void     coord_set_y(coord c, int y);
     unsigned long long  coord_pack(const coord c);
     coord    coord_unpack(unsigned long long packed);
     void     coord_set(coord c, int x, int y);
     void     coord_fetch(coord c, int* out_x, int* out_y);
     int coord_compare(const coord a, const coord b);
""")

def coord_pack(c: Any) -> Any:
    return C.coord_pack(c)

def coord_unpack(packed: Any) -> Any:
    return C.coord_unpack(packed)

class c_coord:
    def __init__(self, x=0, y=0, raw_ptr=None):
        if raw_ptr:
            self._c = raw_ptr
        # if raw_ptr:
        #     # raw_ptr의 값을 읽어서 새 coord를 만든다 (복사, not 공유)
        #     copied_x = C.coord_get_x(raw_ptr)
        #     copied_y = C.coord_get_y(raw_ptr)
        #     self._c = C.coord_new_full(copied_x, copied_y)
        elif x is not None and y is not None:
            self._c = C.coord_new_full(x, y)
        else:
            self._c = C.coord_new()

    @property
    def x(self):
        return C.coord_get_x(self._c)

    @x.setter
    def x(self, value):
        C.coord_set_x(self._c, value)

    @property
    def y(self):
        return C.coord_get_y(self._c)

    @y.setter
    def y(self, value):
        C.coord_set_y(self._c, value)

    def copy(self):
        return c_coord(raw_ptr=C.coord_copy(self._c))

    def __eq__(self, other):
        return C.coord_equal(self._c, other._c) != 0

    def __lt__(self, other):
            return C.coord_compare(self._c, other._c) < 0
    
    def __ge__(self, other):
            return C.coord_compare(self._c, other._c) >= 0

    def __hash__(self):
        return C.coord_hash(self._c)
    
    def __del__(self):
        # C.coord_free(self._c)
        pass

    def close(self):
        if self._c:
            C.coord_free(self._c)
            self._c = None        

    def __enter__(self):
        # with문이 시작될 때 호출
        return self  # 보통 self를 반환함

    def __exit__(self, exc_type, exc_val, exc_tb):
        # with문이 끝났을 때 호출됨
        # 여기서 자원 정리를 직접 수행
        self.close()    
    
    def __add__(self, other):
        return c_coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return c_coord(self.x - other.x, self.y - other.y)

    def __str__(self):
        return f"c_coord(x={self.x}, y={self.y})"
    
    def __repr__(self):
        return f"c_coord(x={self.x}, y={self.y})"    
    
    def to_tuple(self):
        return (self.x, self.y)
    
    def ptr(self):
        return self._c
    
    @staticmethod
    def from_tuple(t: tuple[int, int]):
        return c_coord(*t)
