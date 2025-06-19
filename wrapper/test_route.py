from pathlib import Path
import sys

g_root_path = Path('C:/Users/critl/docs/byul_world_env/byul_world')
wrapper_path = g_root_path / Path("wrapper/modules")

sys.path.insert(0, str(wrapper_path.resolve()))


from route import c_route
from coord import c_coord

if __name__ == '__main__':
    print('route.py 테스트 시작')

    a = c_coord(1, 1)
    b = c_coord(2, 1)
    c = c_coord(3, 1)
    d = c_coord(4, 2)

    route = c_route()
    route.add_coord(a)
    route.add_coord(b)
    route.add_coord(c)
    route.add_coord(d)

    route.update_average_vector_by_index(0, 1)
    route.update_average_vector_by_index(1, 2)

    angle_threshold = 5.0
    changed = route.has_changed_by_index(2, 3, angle_threshold)
    changed2, angle = route.has_changed_with_angle_by_index(2, 3, angle_threshold)

    print(f"변경 여부: {changed}")
    print(f"변경 여부 + 각도: {changed2}, angle={angle:.3f}°")

    # assert changed is True
    # assert changed2 is True
    assert changed
    assert changed2
    assert angle > angle_threshold

    print("테스트 완료: OK")


