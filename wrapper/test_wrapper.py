from pathlib import Path
import sys

g_root_path = Path('C:/Users/critl/docs/byul_world_env/byul_world')
wrapper_path = g_root_path / Path("wrapper/modules")

sys.path.insert(0, str(wrapper_path.resolve()))

from coord import c_coord
from map import c_map, MAP_NEIGHBOR_8
from dstar_lite import c_dstar_lite
from dstar_lite_utils import c_dstar_lite_utils
from dstar_lite_pqueue import c_dstar_lite_pqueue

if __name__ == "__main__":
    map = c_map(10, 10, MAP_NEIGHBOR_8)
    finder = c_dstar_lite.from_map(map)
    finder.debug_mode_enabled = True

    # 1️⃣ 초기 경로
    print("\n▶ 최초 경로:")
    start = c_coord(0,0)
    goal = c_coord(9,9)
    finder.start = start
    finder.goal = goal
    # finder.real_loop_max_retry = 20

    result = finder.find()
    result.print()
    # c_dstar_lite_utils.print_ascii_only_map(finder)
    c_dstar_lite_utils.print_ascii_uv(finder, result)
    
    # del result
    result.close()

    # 2️⃣ 장애물 추가
    x = 3
    y = 3
    print(f"\n▶ ({x}, {y}에 장애물 추가:")
    finder.block_coord(x, y)
    finder.update_vertex_auto_range(c_coord(x, y))

    result = finder.find()
    result.print()
    c_dstar_lite_utils.print_ascii_uv(finder, result)
    result.close()

    x = 3
    y = 4
    print(f"\n▶ ({x}, {y}에 장애물 추가:")
    finder.block_coord(x, y)
    finder.update_vertex_auto_range(c_coord(x, y))

    result = finder.find()
    result.print()
    c_dstar_lite_utils.print_ascii_uv(finder, result)    
    result.close()

    x = 3
    y = 2
    print(f"\n▶ ({x}, {y}에 장애물 추가:")
    finder.block_coord(x, y)

    result = finder.find()
    result.print()
    c_dstar_lite_utils.print_ascii_uv(finder, result)
    result.close()  

    x = 3
    y = 1
    print(f"\n▶ ({x}, {y}에 장애물 추가:")
    finder.block_coord(x, y)

    result = finder.find()
    result.print()
    c_dstar_lite_utils.print_ascii_uv(finder, result)
    result.close()

    x = 3
    y = 0
    print(f"\n▶ ({x}, {y}에 장애물 추가:")
    finder.block_coord(x, y)
    finder.update_vertex_auto_range(c_coord(x, y))

    result = finder.find()
    result.print()
    c_dstar_lite_utils.print_ascii_uv(finder, result)
    result.close()

    # 4️⃣ 장애물 제거
    x = 3
    y = 3
    print(f"\n▶ ({x}, {y}에 장애물 제거:")
    finder.unblock_coord(x, y)
    finder.update_vertex_auto_range(c_coord(x, y))

    result = finder.find()
    result.print()
    c_dstar_lite_utils.print_ascii_uv(finder, result)    
    result.close()

    # 2️⃣ 장애물 추가
    x = 3
    y = 3
    print(f"\n▶ ({x}, {y}에 장애물 추가:")
    finder.block_coord(x, y)
    finder.update_vertex_auto_range(c_coord(x, y))

    with finder.find() as result:
        result.print()
        c_dstar_lite_utils.print_ascii_uv(finder, result)

    x = 3
    y = 5
    print(f"\n▶ ({x}, {y}에 장애물 추가:")
    finder.block_coord(x, y)
    finder.update_vertex_auto_range(c_coord(x, y))

    with finder.find() as result:
        result.print()
        c_dstar_lite_utils.print_ascii_uv(finder, result)
        
    x = 3
    y = 6
    print(f"\n▶ ({x}, {y}에 장애물 추가:")
    finder.block_coord(x, y)
    finder.update_vertex_auto_range(c_coord(x, y))

    with finder.find() as result:
        result.print()
        c_dstar_lite_utils.print_ascii_uv(finder, result)        
        
    x = 3
    y = 7
    print(f"\n▶ ({x}, {y}에 장애물 추가:")
    finder.block_coord(x, y)
    finder.update_vertex_auto_range(c_coord(x, y))

    with finder.find() as result:
        result.print()
        c_dstar_lite_utils.print_ascii_uv(finder, result)        
        

    start_x = 2
    start_y = 2
    goal_x = 13
    goal_y = 13
    print(f"\n▶ 시작({start_x}, {start_y}로 변경:")
    print(f"\n▶ 목표({goal_x}, {goal_y}로 변경:")

    s = c_coord(start_x, start_y)
    g = c_coord(goal_x, goal_y)

    finder.width = goal_x+3
    finder.height = goal_y+3

    finder.max_range = 18

    print(f"\n▶ 가로 :{goal_x}, 세로 {goal_y}로 변경:")
    finder.update_vertex_auto_range(g)
    finder.update_vertex_auto_range(s)

    with finder.find() as result:
        result.print()
        c_dstar_lite_utils.print_ascii_uv(finder, result)

    print('c_dstar_lite 테스트 종료된다.')
