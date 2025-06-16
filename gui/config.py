import sys
from pathlib import Path

# 🧠 최초 1회 기준 루트 설정
BYUL_WORLD_ENV_PATH = Path(__file__).parents[2]
BYUL_WORLD_PATH = BYUL_WORLD_ENV_PATH / 'byul_demo'
WRAPPER_PATH = BYUL_WORLD_PATH / Path('wrapper/modules')
GUI_PATH = BYUL_WORLD_PATH / 'gui'
IMAGES_PATH = BYUL_WORLD_ENV_PATH / 'images'

# sys.path에 디렉토리 추가 (중복 방지)
if str(BYUL_WORLD_ENV_PATH) not in sys.path:
    sys.path.insert(0, str(BYUL_WORLD_ENV_PATH))

# sys.path에 디렉토리 추가 (중복 방지)
if str(BYUL_WORLD_PATH) not in sys.path:
    sys.path.insert(0, str(BYUL_WORLD_PATH))

# sys.path에 디렉토리 추가 (중복 방지)
if str(WRAPPER_PATH) not in sys.path:
    sys.path.insert(0, str(WRAPPER_PATH))

if str(GUI_PATH) not in sys.path:
    sys.path.insert(0, str(GUI_PATH))

if __name__ == '__main__':
    print(f'BYUL_WORLD_ENV_PATH : {BYUL_WORLD_ENV_PATH}')
    print(f'BYUL_WORLD_PATH : {BYUL_WORLD_PATH}')
    print(f'WRAPPER_PATH : {WRAPPER_PATH}')
    print(f'GUI_PATH : {GUI_PATH}')
    print(f'IMAGES_PATH : {IMAGES_PATH}')

    print(f'sys.path : {sys.path}')