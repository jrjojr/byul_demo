'''
사용법

cl = c_list()
for c in [c_coord(1, 2), c_coord(3, 4)]:
    cl.append(c.ptr())

gl_ptr = cl.ptr()  # 이걸 GList*로 넘기면 됨

'''

from ffi_core import ffi, C

from pathlib import Path
import os
from typing import Any

ffi.cdef("""
typedef struct _GList GList;
         
typedef struct _GList {
    gpointer data;
    GList* next;
    GList* prev;
} GList;

GList* g_list_prepend(GList *list, gpointer data);
GList* g_list_append(GList *list, gpointer data);
GList* g_list_reverse(GList *list);
void g_list_free(GList *list);
int g_list_length(GList *list);
gpointer g_list_nth_data(GList *list, int n);
""")

class c_list:
    def __init__(self):
        self._ptr = ffi.NULL

    def append(self, data):
        self._ptr = C.g_list_append(self._ptr, data)

    def prepend(self, data):
        self._ptr = C.g_list_prepend(self._ptr, data)

    def reverse(self):
        self._ptr = C.g_list_reverse(self._ptr)

    def free(self):
        if self._ptr != ffi.NULL:
            C.g_list_free(self._ptr)
            self._ptr = ffi.NULL

    def length(self):
        return int(C.g_list_length(self._ptr))

    def nth_data(self, index):
        return C.g_list_nth_data(self._ptr, index)

    def to_list(self):
        """Python list로 변환 (주의: 내부 포인터를 복사하지 않음)"""
        result = []
        for i in range(self.length()):
            result.append(self.nth_data(i))
        return result

    def ptr(self):
        """내부 GList* 포인터 반환"""
        return self._ptr

    @classmethod
    def _from_ptr(cls, gl_ptr):
        obj = cls()
        obj._ptr = gl_ptr
        return obj