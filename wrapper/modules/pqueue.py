from ffi_core import ffi, C

from pathlib import Path
import os
import platform

ffi.cdef("""
    struct s_pqueue { GTree * tree ; GCompareDataFunc compare ; void* userdata ; GDestroyNotify value_destroy ; };
    typedef struct s_pqueue pqueue_t;
    typedef pqueue_t * pqueue;
    struct s_pqueue_iter { GList * keys ; GList * current ; pqueue pq ; };
    typedef struct s_pqueue_iter pqueue_iter_t;
    typedef pqueue_iter_t * pqueue_iter;
    pqueue pqueue_new ( void );
    pqueue pqueue_new_full ( GCompareDataFunc cmp , void* userdata , GDestroyNotify key_destroy , GDestroyNotify value_destroy );
    void pqueue_free ( pqueue pq );
    int pqueue_find_min_key ( pqueue pq , void* * out_key );
    void pqueue_push ( pqueue pq , void* key , size_t key_size , void* value , size_t value_size );
    void* pqueue_peek ( pqueue pq );
    void* pqueue_pop ( pqueue pq );
    int pqueue_is_empty ( pqueue pq );
    int pqueue_remove ( pqueue pq , void* key , void* value );
    int pqueue_remove_custom ( pqueue pq , void* key , const void* target_value , GCompareFunc cmp );
    void pqueue_update ( pqueue pq , void* old_key , void* new_key , size_t key_size , void* value , size_t value_size );
    int pqueue_contains ( pqueue pq , const void* key );
    GQueue * pqueue_get_values ( pqueue pq , const void* key );
    GList * pqueue_get_all_keys ( pqueue pq );
    void pqueue_clear ( pqueue pq );
    void* pqueue_find_key_by_value ( pqueue pq , const void* value );
    pqueue_iter pqueue_iter_new ( pqueue pq );
    int pqueue_iter_next ( pqueue_iter iter , void* * out_key , void* * out_value );
    void pqueue_iter_free ( pqueue_iter iter );
    void* pqueue_top_key ( pqueue pq );
""")

class c_pqueue:
    def __init__(self):
        self._c = C.pqueue_new()

    @classmethod
    def from_full(cls, cmp, userdata, key_destroy, value_destroy):
        ptr = C.pqueue_new_full(cmp, userdata, key_destroy, value_destroy)
        return cls._from_ptr(ptr)

    @classmethod
    def _from_ptr(cls, ptr):
        obj = cls.__new__(cls)
        obj._c = ptr
        return obj

    def close(self):
        if self._c:
            C.pqueue_free(self._c)
            self._c = None

    def __del__(self):
        self.close()

    def find_min_key(self):
        key_ptr = ffi.new("void**")
        result = C.pqueue_find_min_key(self._c, key_ptr)
        return result, key_ptr[0]

    def push(self, key, key_size, value, value_size):
        C.pqueue_push(self._c, key, key_size, value, value_size)

    def peek(self):
        return C.pqueue_peek(self._c)

    def pop(self):
        return C.pqueue_pop(self._c)

    def is_empty(self):
        return C.pqueue_is_empty(self._c)

    def remove(self, key, value):
        return C.pqueue_remove(self._c, key, value)

    def remove_custom(self, key, target_value, cmp):
        return C.pqueue_remove_custom(self._c, key, target_value, cmp)

    def update(self, old_key, new_key, key_size, value, value_size):
        C.pqueue_update(self._c, old_key, new_key, key_size, value, value_size)

    def contains(self, key):
        return C.pqueue_contains(self._c, key)

    def get_values(self, key):
        return C.pqueue_get_values(self._c, key)

    def get_all_keys(self):
        return C.pqueue_get_all_keys(self._c)

    def clear(self):
        C.pqueue_clear(self._c)

    def find_key_by_value(self, value):
        return C.pqueue_find_key_by_value(self._c, value)

    def top_key(self):
        return C.pqueue_top_key(self._c)

class c_pqueue_iter:
    def __init__(self, pq: c_pqueue):
        self._c = C.pqueue_iter_new(pq._c)

    def next(self):
        out_key = ffi.new("void**")
        out_value = ffi.new("void**")
        result = C.pqueue_iter_next(self._c, out_key, out_value)
        return result, out_key[0], out_value[0]

    def close(self):
        if self._c:
            C.pqueue_iter_free(self._c)
            self._c = None

    def __del__(self):
        self.close()
