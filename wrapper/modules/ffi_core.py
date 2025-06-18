# ffi_core.py
from cffi import FFI
from pathlib import Path
import os
import platform
import sys

ffi = FFI()

ffi.cdef("""
typedef int gint;
typedef int guint;
typedef int gboolean;
typedef const void* gconstpointer;
typedef void* gpointer;
         
typedef float gfloat;

typedef struct _GQueue GQueue;

typedef struct _GHashTableIter GHashTableIter;
         
typedef struct _GTree GTree;         

typedef void (*GDestroyNotify)(void*);

typedef gint            (*GCompareDataFunc)     (gconstpointer  a,
                                                 gconstpointer  b,
						 gpointer       user_data);         
         
typedef gint            (*GCompareFunc)         (gconstpointer  a,
                                                 gconstpointer  b);         
         
typedef struct s_flud* flud;
""")

# === 플랫폼별 DLL/SO 파일 경로 자동 처리 ===
system = platform.system()
root = Path.home() / "byul_world"

if system == "Windows":
    lib_name = "libroutefinder.dll"
    lib_path = root / "bin" / lib_name
    os.add_dll_directory(str(lib_path.parent))  # 필수
    os.add_dll_directory(str(Path("C:/msys64/clang64/bin")))
elif system == "Linux":
    lib_name = "libroutefinder.so"
    lib_path = root / "lib" / lib_name
elif system == "Darwin":  # macOS
    lib_name = "libroutefinder.dylib"
    lib_path = root / "lib" / lib_name
else:
    raise RuntimeError(f"❌ 지원되지 않는 플랫폼: {system}")

# === 로딩 시도 및 오류 메시지 출력 ===
try:
    C = ffi.dlopen(str(lib_path))
except OSError as e:
    print(f"❌ 라이브러리 로딩 실패: {lib_path}")
    print(f"→ {e}")
    raise RuntimeError("플랫폼에 맞는 바이너리 경로 또는 파일명을 확인하세요.")
