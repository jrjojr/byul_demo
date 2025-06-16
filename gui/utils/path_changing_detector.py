import math
from collections import deque
from utils.log_to_panel import g_logger

class PathChangingDetector:
    """
    이동 경로 변경 감지기 (2D/3D 겸용, 방향 히스토리 기반).
    일정 각도 이상 벗어날 경우 경로가 변경된 것으로 판단한다.

    사용 예:
    from path_change_detector import PathChangingDetector

    self.path_detector = PathChangingDetector()

    if self.path_detector.has_changed(
        (self.center_x, self.center_y), (new_x, new_y)
    ):
        self.block_manager.load_blocks_forward_for_rect_async(...)
    """

    def __init__(self, history_size=5):
        self.history = deque(maxlen=history_size)

    def _normalize_vector(self, from_pos, to_pos):
        vx = to_pos[0] - from_pos[0]
        vy = to_pos[1] - from_pos[1]
        vz = (to_pos[2] - from_pos[2]) if len(to_pos) == 3 else 0.0

        mag = math.sqrt(vx**2 + vy**2 + vz**2)
        if mag < 1e-5:
            return None  # 정지 또는 미세 이동은 무시

        return (vx / mag, vy / mag, vz / mag)

    def _get_average_vector(self):
        if not self.history:
            return None
        sx, sy, sz = 0.0, 0.0, 0.0
        for vx, vy, vz in self.history:
            sx += vx
            sy += vy
            sz += vz
        count = len(self.history)
        return (sx / count, sy / count, sz / count)

    def has_changed(self, from_pos, to_pos, angle_threshold_deg=10):
        """
        경로가 변경되었는지 판단한다.
        - 평균 방향 벡터와 현재 방향 벡터의 각도 차이를 비교함.
        - 내부에 방향 벡터 히스토리를 유지함.

        :param from_pos: 이전 좌표 (x, y) or (x, y, z)
        :param to_pos: 현재 좌표 (x, y) or (x, y, z)
        :param angle_threshold_deg: 판단 기준 각도 (기본값: 10도)
        :return: True = 경로 변경 감지됨 / False = 유지 중
        """
        curr_vec = self._normalize_vector(from_pos, to_pos)
        if curr_vec is None:
            return False  # 정지 상태

        self.history.append(curr_vec)

        avg_vec = self._get_average_vector()
        if avg_vec is None:
            return False  # 첫 입력은 비교하지 않음

        # 평균 벡터와 현재 벡터의 각도 비교
        dot = sum(a * b for a, b in zip(avg_vec, curr_vec))
        angle_rad = math.acos(max(-1.0, min(1.0, dot)))
        angle_deg = math.degrees(angle_rad)

        changed = angle_deg > angle_threshold_deg
        if changed:
            g_logger.log_debug(
f"경로 변경 감지: 평균 벡터에서 {angle_deg:.1f}° 벗어남")

        return changed
