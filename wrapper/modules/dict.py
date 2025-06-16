''' 사용법
cd = c_dict()
cd.insert(c_coord(1, 2).ptr(), ffi.NULL)
cd.insert(c_coord(3, 4).ptr(), ffi.NULL)

print(f"size: {cd.size()}")

key_list = cd.keys().to_list()
for k in key_list:
    c = c_coord(raw_ptr=k)
    print(f"coord: {c}")

g_ptr = C.map_get_blocked_coords(gmap.ptr())
cd = c_dict.from_ptr(g_ptr)

for key_ptr in cd.keys().to_list():
    c = c_coord(raw_ptr=key_ptr)
    print(f"blocked: {c}")

'''

from ffi_core import ffi, C

from list import c_list

ffi.cdef("""
typedef struct _GHashTable GHashTable;

GHashTable* g_hash_table_new_full(void*, void*, void*, void*);
void g_hash_table_insert(GHashTable*, void*, void*);
void* g_hash_table_lookup(GHashTable*, const void*);
int g_hash_table_contains(GHashTable*, const void*);
void g_hash_table_remove(GHashTable*, const void*);
void g_hash_table_destroy(GHashTable*);

GList* g_hash_table_get_keys(GHashTable*);
GList* g_hash_table_get_values(GHashTable*);
int g_hash_table_size(GHashTable*);
""")

class c_dict:
    def __init__(self, ptr=None):
        if ptr:
            self._ptr = ptr
            self._owned = False
        else:
            # NULL로 생성하면 기본 설정 (key/value free는 없음)
            self._ptr = C.g_hash_table_new_full(
                ffi.NULL, ffi.NULL, ffi.NULL, ffi.NULL)
            
            self._owned = True

    def insert(self, key, value):
        C.g_hash_table_insert(self._ptr, key, value)

    def get(self, key):
        return C.g_hash_table_lookup(self._ptr, key)

    def contains(self, key):
        return bool(C.g_hash_table_contains(self._ptr, key))

    def remove(self, key):
        C.g_hash_table_remove(self._ptr, key)

    def keys(self):
        return c_list._from_ptr(C.g_hash_table_get_keys(self._ptr))

    def values(self):
        return c_list._from_ptr(C.g_hash_table_get_values(self._ptr))

    def size(self):
        return int(C.g_hash_table_size(self._ptr))

    def ptr(self):
        return self._ptr

    def close(self):
        if self._owned and self._ptr != ffi.NULL:
            C.g_hash_table_destroy(self._ptr)
            self._ptr = ffi.NULL

    def __del__(self):
        self.close()
        pass

    @classmethod
    def from_ptr(cls, ptr):
        return cls(ptr)
