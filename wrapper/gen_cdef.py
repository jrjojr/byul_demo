'''C 헤더 파일로부터 CFFI에서 사용 가능한 텍스트를 반환하거나 저장한다.
기본값은 텍스트 반환이다. 원할 경우 파일로 저장
구조체, typedef, 함수 선언 등을 파싱하고, `gint`, `BYUL_API` 등 CFFI에서 인식할 수 없는
타입이나 매크로는 적절히 변환합니다.

이 스크립트는 다음 두 가지 파서를 결합하여 완전한 선언 목록을 추출합니다:

1. extract_structs_and_typedefs(header_route)
   - libclang 기반으로 `struct`, `typedef` 선언을 추출합니다.
   - 장점: C의 구문을 정확히 분석하여 중복 없이 구조를 보존합니다.
   - 단점: 함수 선언 중 일부 복잡한 매크로나 콜백 주석이 포함된 선언은 추출하지 못함

2. FunctionDeclarationParser.extract_function_declarations(header_route)
   - 정규표현식 기반으로 `.h` 파일 내의 함수 선언을 직접 분석합니다.
   - 멀티라인 함수 선언도 지원하며, `BYUL_API`, `gint` 등의 매크로는 자동 치환됩니다.
   - 장점: 주석이 달린 선언, 매크로가 포함된 함수도 안전하게 인식
   - 단점: 구조체나 typedef는 분석하지 않음

두 파서를 결합하여 C 헤더에 존재하는 대부분의 선언을 CFFI용으로 완전하게 추출합니다.

사용법:
python gen_cdef.py -o ./ "C:/Users/critl/byul_world/include/internal/coord.h"

python gen_cdef.py `
-o C:/Users/critl/docs/byul_world_env/byul_world/wrapper/modules `
C:/Users/critl/byul_world/include/internal/coord.h `

출력:
coord.cdef.h 파일이 -o 디렉토리에 생성되며, 이는 다음과 같이 사용할 수 있습니다:

from cffi import FFI
ffi = FFI()
ffi.cdef(open("coord.cdef.h").read())
'''

import argparse
import re
import platform
from pathlib import Path
from clang.cindex import Index, CursorKind, Config, TokenKind

# 플랫폼에 따라 libclang 경로 설정
if platform.system() == "Windows":
    Config.set_library_file("C:/msys64/clang64/bin/libclang.dll")
elif platform.system() == "Linux":
    Config.set_library_file("/usr/lib/llvm-14/lib/libclang-14.so")

REPLACEMENTS = {
    "gint": "int",
    "guint": "unsigned int",
    "gint8": "signed char",
    "guint8": "unsigned char",
    "gint16": "short",
    "guint16": "unsigned short",
    "gint32": "int",
    "guint32": "unsigned int",
    "gint64": "long long",
    "guint64": "unsigned long long",
    "gfloat": "float",
    "gdouble": "double",
    "gboolean": "int",
    "gpointer": "void*",
    "gconstpointer": "const void*",
    "gchar": "char",
    "gunichar": "unsigned int",
    "gsize": "size_t",
    "gssize": "ssize_t",
    "BYUL_API": "",
    "DSL_API": "",
    "G_GNUC_CONST": "",
    "G_GNUC_WARN_UNUSED_RESULT": "",
    "unsigned int64": "unsigned long long",
    "int64": "long long",
    "dresult_t": "int",
    "map_neighbor_mode_t": "int",
}

CUSTOM_POINTER_STRUCTS = {'flud', 'algo', 'route', 'map', 'coord'}

EXTERNAL_FORWARD_DECLS = {
    "GHashTable": "typedef struct _GHashTable GHashTable;",
    "GQueue": "typedef struct _GQueue GQueue;",
    "GList": "typedef struct _GList GList;",
    "GTree": "typedef struct _GTree GTree;",
    "GHashTableIter": "typedef struct _GHashTableIter GHashTableIter;",
    "GDestroyNotify": "typedef void (*GDestroyNotify)(void*);",
}

FUNC_POINTER_NAMES = {"algo_find_func", "cost_func", "heuristic_func",
                      "dsl_cost_func", "dsl_heuristic_func"}

def patch_func_ptr_fields(decls: list[str]) -> list[str]:
    patched = []
    for line in decls:
        if line.startswith("typedef struct s_") and "{" in line and "}" in line:
            for name in FUNC_POINTER_NAMES:
                line = re.sub(rf"\\b{name}\\b\\s+(\\w+)", r"void* \\1", line)
        patched.append(line)
    return patched

class CdefExtractor:
    def __init__(self, header_path: Path):
        self.header_path = header_path

    def extract_structs_and_typedefs(self) -> list[str]:
        index = Index.create()
        tu = index.parse(str(self.header_path), args=['-x', 'c', '-std=c99'])
        decls, seen_structs = [], set()

        for name in CUSTOM_POINTER_STRUCTS:
            decls.append(f"typedef struct s_{name}* {name};")

        def visit(node):
            if node.location.file and Path(node.location.file.name) != self.header_path:
                return

            if node.kind == CursorKind.STRUCT_DECL:
                name = node.spelling or "anon"
                if name in seen_structs:
                    return
                seen_structs.add(name)

            if node.kind in {CursorKind.STRUCT_DECL, CursorKind.TYPEDEF_DECL}:
                tokens = list(node.get_tokens())
                clean = [tok.spelling for tok in tokens if tok.kind != TokenKind.COMMENT]
                if clean:
                    line = ' '.join(clean)
                    line = self.apply_replacements(line)
                    if not line.endswith(';'):
                        line += ';'
                    decls.append(line)
            for child in node.get_children():
                visit(child)

        visit(tu.cursor)

        cleaned = decls[:]
        for d1 in decls:
            if not d1.startswith("struct"):
                continue
            body = d1.strip().rstrip(';')
            for d2 in decls:
                if d1 == d2 or not d2.startswith("typedef"):
                    continue
                if body in d2 and d1 in cleaned:
                    cleaned.remove(d1)
                    break

        return cleaned

    def extract_functions(self) -> list[str]:
        index = Index.create()
        tu = index.parse(str(self.header_path), args=['-x', 'c', '-std=c99', '-DBYUL_API=', '-DDSL_API='])

        functions = []

        def visit(node):
            if node.location.file and Path(node.location.file.name) != self.header_path:
                return

            if node.kind == CursorKind.FUNCTION_DECL:
                tokens = list(node.get_tokens())
                clean = [tok.spelling for tok in tokens if tok.kind != TokenKind.COMMENT]
                if clean:
                    line = ' '.join(clean)
                    line = self.apply_replacements(line)
                    if not line.endswith(';'):
                        line += ';'
                    functions.append(line)

            for child in node.get_children():
                visit(child)

        visit(tu.cursor)
        return functions

    def apply_replacements(self, line: str) -> str:
        for key, val in REPLACEMENTS.items():
            line = line.replace(key, val)
        return line

    def is_func_pointer(self, fn_decl: str) -> bool:
        return '(*' in fn_decl and ')' in fn_decl and '(' in fn_decl

    def generate_cdef_text(self) -> str:
        type_decls = self.extract_structs_and_typedefs()
        func_decls = self.extract_functions()

        lines = ["// 이 파일은 gen_cdef.py에 의해 자동 생성됨"]
        lines.extend(EXTERNAL_FORWARD_DECLS.values())
        lines.append("")

        seen = set()
        filtered_decls = []
        for decl in type_decls:
            skip = False
            for name in CUSTOM_POINTER_STRUCTS:
                if f"typedef struct s_{name}*" in decl and name in seen:
                    skip = True
                if f"typedef {name}_t * {name};" in decl and name in seen:
                    skip = True
                if name in decl:
                    seen.add(name)
            if not skip:
                filtered_decls.append(decl)

        patched_decls = patch_func_ptr_fields(filtered_decls)
        lines.extend(patched_decls)

        for func in func_decls:
            lines.append(func)

        return '\n'.join(lines)

    def generate_py(self) -> str:
        cdef_text = self.generate_cdef_text()
        indent = "    "
        lines = []

        lines += [
            "from cffi import FFI",
            "from pathlib import Path",
            "import os",
            "import platform",
            "",
            "ffi = FFI()",
            "",
            "ffi.cdef(\"\"\""
        ]

        for line in cdef_text.splitlines()[1:]:
            lines.append(f"{indent}{line}")
        lines.append("\"\"\")")
        lines.append("")

        lines.append("if platform.system() == 'Windows':")
        lines.append("    glib_dir = Path('C:/msys64/clang64/bin')")
        lines.append("    os.add_dll_directory(str(glib_dir))")
        lines.append("    dll_path = Path.home() / 'byul_world' / 'bin' / 'libroutefinder.dll'")
        lines.append("else:")
        lines.append("    dll_path = Path.home() / 'byul_world' / 'bin' / 'libroutefinder.so'")
        lines.append("C = ffi.dlopen(str(dll_path))")
        lines.append("")

        # 구조체 포인터 래퍼 클래스 자동 생성
        for name in CUSTOM_POINTER_STRUCTS:
            class_name = f"c_{name}"
            lines.append(f"class {class_name}:")
            lines.append(f"{indent}def __init__(self, raw_ptr=None):")
            lines.append(f"{indent*2}self._c = raw_ptr if raw_ptr else C.{name}_new()")
            lines.append(f"{indent}def ptr(self): return self._c")
            lines.append(f"{indent}def close(self):\n{indent*2}if self._c: C.{name}_free(self._c); self._c = None")
            lines.append(f"{indent}def __del__(self): self.close()")
            lines.append("")

        functions = self.extract_functions()
        for fn in functions:
            if fn and self.is_func_pointer(fn):
                lines.append(f"def {fn}(*args):")
                lines.append(f"{indent}return C.{fn}(*args)")
                lines.append("")

        return "\n".join(lines)

    def save_to_cdef_file(self, outdir: Path):
        output_path = outdir / (self.header_path.stem + ".cdef.h")
        cdef_text = self.generate_cdef_text()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cdef_text)
        print(f'✅ 생성 완료: {output_path} (CDEF 헤더)')

    def save_to_py(self, outdir: Path):
        outdir.mkdir(parents=True, exist_ok=True)
        output_path = outdir / (self.header_path.stem + ".py")
        code = self.generate_py()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"✅ 저장 완료: {output_path} (Python 래퍼 파일)")

...

# ✅ 자동 클래스 생성기 함수

def generate_class_code(struct_name: str, func_decls: list[str]) -> str:
    """
    struct_name: 예) 'coord'
    func_decls: 함수 선언 리스트 (ex: ['coord coord_new();', 'void coord_set_x(coord c, int x);'])
    """
    import re

    cls_name = f"c_{struct_name}"
    indent = "    "
    methods = []
    getters, setters, other_methods = [], [], []
    has_copy = False
    has_equal = False
    has_compare = False
    has_hash = False

    for decl in func_decls:
        if not decl.startswith(struct_name):
            continue

        # 파싱
        decl = decl.rstrip(';').strip()
        m = re.match(r'(.+?)\s+(\w+)\s*\((.*)\)', decl)
        if not m:
            continue
        ret_type, fn_name, args = m.groups()
        arg_list = [a.strip() for a in args.split(',') if a.strip()]
        first_arg_type = arg_list[0] if arg_list else ""

        # 기본 생성자
        if fn_name == f"{struct_name}_new":
            methods.append(f"def __init__(self, raw_ptr=None):")
            methods.append(f"{indent}if raw_ptr: self._c = raw_ptr")
            methods.append(f"{indent}else: self._c = C.{fn_name}()")
            continue

        # full 생성자
        if fn_name == f"{struct_name}_new_full":
            param_names = [f"arg{i}" for i in range(1, len(arg_list))]
            args_str = ", ".join(param_names)
            call_args = ", ".join(param_names)
            methods.append(f"@classmethod")
            methods.append(f"def from_values(cls, {args_str}):")
            methods.append(f"{indent}ptr = C.{fn_name}({call_args})")
            methods.append(f"{indent}return cls(raw_ptr=ptr)")
            continue

        if fn_name == f"{struct_name}_free":
            methods.append("def close(self):")
            methods.append(f"{indent}if self._c: C.{fn_name}(self._c); self._c = None")
            methods.append("def __del__(self):")
            methods.append(f"{indent}self.close()")
            continue

        if fn_name == f"{struct_name}_copy":
            has_copy = True
            methods.append("def copy(self):")
            methods.append(f"{indent}return {cls_name}(raw_ptr=C.{fn_name}(self._c))")
            continue

        if fn_name == f"{struct_name}_equal":
            has_equal = True
            methods.append("def __eq__(self, other):")
            methods.append(f"{indent}return C.{fn_name}(self._c, other._c) != 0")
            continue

        if fn_name == f"{struct_name}_compare":
            has_compare = True
            methods.append("def __lt__(self, other):")
            methods.append(f"{indent}return C.{fn_name}(self._c, other._c) < 0")
            methods.append("def __ge__(self, other):")
            methods.append(f"{indent}return C.{fn_name}(self._c, other._c) >= 0")
            continue

        if fn_name == f"{struct_name}_hash":
            has_hash = True
            methods.append("def __hash__(self):")
            methods.append(f"{indent}return C.{fn_name}(self._c)")
            continue

        # getter / setter
        if fn_name.startswith(f"{struct_name}_get_"):
            field = fn_name[len(f"{struct_name}_get_") :]
            prop = f"@property\ndef {field}(self):\n{indent}return C.{fn_name}(self._c)"
            getters.append(prop)
            continue

        if fn_name.startswith(f"{struct_name}_set_"):
            field = fn_name[len(f"{struct_name}_set_") :]
            setter = f"@{field}.setter\ndef {field}(self, value):\n{indent}C.{fn_name}(self._c, value)"
            setters.append(setter)
            continue

        # 기타 함수들
        params = ", ".join(f"arg{i}" for i in range(1, len(arg_list)))
        call_params = ", ".join(["self._c"] + [f"arg{i}" for i in range(1, len(arg_list))])
        other_methods.append(f"def {fn_name[len(struct_name)+1:]}(self, {params}):")
        other_methods.append(f"{indent}return C.{fn_name}({call_params})")

    lines = [f"class {cls_name}:"]
    if not methods:
        lines.append(f"{indent}pass")
    else:
        lines += [indent + line for line in methods]
        lines.append("")
        lines += [indent + line for line in getters]
        lines.append("")
        lines += [indent + line for line in setters]
        lines.append("")
        lines += [indent + line for line in other_methods]

    return "\n".join(lines)

import re
from typing import Optional

def parse_c_function_signature(decl: str) -> Optional[tuple[str, str, list[str]]]:
    """
    C 함수 선언을 분석하여 (반환 타입, 함수명, 매개변수 리스트)로 분해합니다.

    예:
    'BYUL_API coord coord_new_full(int x, int y);'
    → ('coord', 'coord_new_full', ['int x', 'int y'])

    'void map_set_data(map m, int value);'
    → ('void', 'map_set_data', ['map m', 'int value'])
    """
    decl = decl.strip().rstrip(';')

    # BYUL_API 같은 접두사는 제거
    decl = decl.replace('BYUL_API', '').strip()

    m = re.match(r'(.+?)\s+(\w+)\s*\((.*?)\)', decl)
    if not m:
        return None

    ret_type, func_name, args = m.groups()
    arg_list = [arg.strip() for arg in args.split(',')] if args.strip() else []
    return ret_type.strip(), func_name.strip(), arg_list

import re

def parse_struct_members_from_decl(decl: str) -> tuple[str, list[str]]:
    """
    구조체 선언 문자열에서 이름과 멤버 리스트를 추출합니다.

    예:
    'struct s_coord { int x; int y; };'
    → ('coord', ['int x', 'int y'])

    반환값: (구조체 이름, 멤버 선언 리스트)
    """
    decl = decl.strip().rstrip(';')

    # 구조체 이름 추출
    m = re.match(r'struct\s+s_(\w+)\s*{(.*)}', decl)
    if not m:
        raise ValueError(f"올바른 struct 선언이 아닙니다: {decl}")

    struct_name, body = m.groups()
    # 멤버들 분리 (한 줄에 ; 기준으로 분리)
    members = [line.strip() for line in body.split(';') if line.strip()]
    return struct_name, members


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CFFI용 .py 텍스트 출력기")
    parser.add_argument("input", help="입력 헤더 파일 경로")
    parser.add_argument("-o", "--outdir", default=".", 
                        help="출력 디렉토리 (기본: 현재 디렉토리)")

    args = parser.parse_args()

    header_path = Path(args.input)
    if not header_path.exists():
        print(f"에러: 파일 '{header_path}'을 찾을 수 없습니다.")
        exit(1)

    # print(extractor.extract_functions())
    # funcs = extractor.extract_functions()
    # for f in funcs:
    #     splited_f = parse_c_function_signature(f)
    #     print(splited_f)

    # structs = extractor.extract_structs_and_typedefs()
    # for s in structs:
        # splited_s = parse_struct_members_from_decl(s)
        # print(splited_s)
        # print(s)

    # class_code = generate_class_code('dstar_lite', funcs)
    # print (class_code)
    
    extractor = CdefExtractor(header_path)
    # extractor.save_to_py(Path(args.outdir))

    structs = extractor.extract_structs_and_typedefs()
    for s in structs:
        print(s)

    funcs = extractor.extract_functions()
    for f in funcs:
        print(f)
