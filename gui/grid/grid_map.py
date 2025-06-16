import shutil
import re
import os
import json
import time
from pathlib import Path

from PySide6.QtCore import Signal, QRect

from grid.grid_cell import GridCell, CellStatus, CellFlag, TerrainType
from grid.grid_block_manager import GridBlockManager
from map import c_map

from coord import c_coord

from utils.log_to_panel import g_logger
from utils.path_changing_detector import PathChangingDetector

class GridMap(GridBlockManager):
    """
    GridMap은 GridBlockManager로부터 셀 정보를 받아 GridCanvas에 제공한다.
    논리적인 장애물, 시작/목표, 경로 표시도 담당한다.
    """
    buffer_changed = Signal(QRect)
    center_changed = Signal(int, int)
    
    move_center_started = Signal(float)
    move_center_ended = Signal(float)
    move_center_elapsed = Signal(float)
    loading_block_ended = Signal(float)

    update_buffer_cells_elapsed = Signal(float)

    def __init__(self, block_size=200):
        super().__init__(block_size)

        self.map = c_map()
        self.parent = None

        # 셀 캐시 버퍼 (GridCanvas에서 사용)
        self.buffer_cells = {}
        self.buffer_cells_width = 0
        self.buffer_cells_height = 0

        self.center_x =0
        self.center_y = 0
        ox, oy = self.get_origin(self.center_x, self.center_y)
        self.request_load_block(ox, oy)

        self.path_detector = PathChangingDetector()

    def _on_block_load_succeeded(self, key: tuple):
        super()._on_block_load_succeeded(key)
    
        if g_logger.debug_mode == True:
            t0 = time.time()
            self.loading_block_ended.emit(t0)

        self.update_buffer_cells()

    def clear_path_flags(self):
        for cell in self.buffer_cells.values():
            cell.remove_flag(CellFlag.PATH)

    def update_buffer_cells(self):
        if g_logger.debug_mode:
            start = time.time()
           
        cx, cy = self.get_center()
        x0 = cx - (self.buffer_cells_width // 2)
        y0 = cy - (self.buffer_cells_height // 2)
        width = self.buffer_cells_width
        height = self.buffer_cells_height

        rect = QRect(x0, y0, width, height)

        if not self.is_blocks_loaded_for_rect(rect):
            self.load_blocks_around_for_rect(rect)

        # 셀 버퍼 갱신
        self.buffer_cells: dict[tuple[int, int], GridCell] = self.to_cells(
            x0, y0, width, height)

        # # 장애물 정보 반영
        # for (x, y), c in self.buffer_cells.items():
        #     if c.terrain == TerrainType.MOUNTAIN:
        #         self.map.block(x, y)
                

        # 변경 신호
        self.buffer_changed.emit(rect)

        if g_logger.debug_mode:
            # g_logger.log_debug(f"[to_cells] 완료: {len(cells)}개, "
            #             f"{(time.time() - start) * 1000:.3f}ms")
            elapsed = time.time() - start
            self.update_buffer_cells_elapsed.emit(elapsed)        

    def get_buffer_cells_rect(self):
        cx, cy = self.get_center()
        x0 = cx - (self.buffer_cells_width // 2)
        y0 = cy - (self.buffer_cells_height // 2)

        rect = QRect(x0, y0,
                     self.buffer_cells_width, self.buffer_cells_height)
        return rect

    def load_from_dict(self, data: dict[tuple[int, int], GridCell]):
        self._cells = {c_coord.from_tuple(k): v for k, v in data.items()}

    def find_width(self, dir: str | Path = None):
        dir = Path(dir) if dir else self.grid_block_path
        if not dir.exists() or not dir.is_dir():
            parsed = self.parse_size_from_folder_name(dir)
            return parsed[0] if parsed else 0

        max_x = -1
        block_size = self.find_block_size(dir)
        for path in dir.iterdir():
            match = re.match(r"block_(\d+)_(\d+)\.json", path.name)
            if match:
                x = int(match.group(1))
                max_x = max(max_x, x)
        return max_x + block_size if max_x >= 0 else 0

    def find_height(self, dir: str | Path = None):
        dir = Path(dir) if dir else self.grid_block_path
        if not dir.exists() or not dir.is_dir():
            parsed = self.parse_size_from_folder_name(dir)
            return parsed[1] if parsed else 0

        max_y = -1
        block_size = self.find_block_size(dir)
        for path in dir.iterdir():
            match = re.match(r"block_(\d+)_(\d+)\.json", path.name)
            if match:
                y = int(match.group(2))
                max_y = max(max_y, y)
        return max_y + block_size if max_y >= 0 else 0

    def find_block_size(self, dir: str | Path = None):
        dir = Path(dir) if dir else self.grid_block_path
        if not dir.exists() or not dir.is_dir():
            parsed = self.parse_size_from_folder_name(dir)
            return parsed[2] if parsed else 0

        for path in dir.iterdir():
            if path.name.startswith("block_") and path.suffix == ".json":
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return data.get("block_size", 0)
                except Exception:
                    continue
        return 0

    def remove_dir(self, dir: str | Path):
        """GridMap 전용 폴더만 안전하게 제거한다."""
        dir = Path(dir)
        if not dir.exists() or not dir.is_dir():
            return

        # 안전 체크: 'grid_map_'으로 시작하는 디렉토리만 삭제 허용
        if not dir.name.startswith("grid_map_"):
            g_logger.log_debug(f"❌ 안전 문제로 폴더 삭제 취소: {dir}")
            return

        try:
            shutil.rmtree(dir)
            g_logger.log_debug(f"🗑 폴더 삭제 완료: {dir}")
        except PermissionError as e:
            g_logger.log_error(f"❌ 삭제 실패 (PermissionError): {dir} - {e}")

    def is_dir_for_grid_map(self, dir: str | Path):
        """디렉토리 구조가 GridMap 형식에 맞는지 판단한다."""
        dir = Path(dir)
        if not dir.exists() or not dir.is_dir():
            return False

        files = list(dir.iterdir())
        block_size = None
        coords = set()

        for path in files:
            match = re.match(r"block_(\d+)_(\d+)\.json", path.name)
            if not match:
                return False

            x, y = int(match.group(1)), int(match.group(2))
            coords.add((x, y))

            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "block_size" not in data:
                        return False
                    if block_size is None:
                        block_size = data["block_size"]
                    elif data["block_size"] != block_size:
                        return False
            except Exception:
                return False

        if not coords:
            return False

        expected_w = self.find_width(dir)
        expected_h = self.find_height(dir)
        if expected_w == 0 or expected_h == 0 or block_size == 0:
            return False

        expected_count = \
            (expected_w // block_size) * (expected_h // block_size)
        
        return len(coords) == expected_count

    def parse_size_from_folder_name(self, dir: Path) -> \
        tuple[int, int, int] | None:
        """
        폴더 이름에서 grid_map_가로x세로_블럭사이즈 형식의 정보를 파싱한다.
        예: grid_map_4000x4000_200 → (4000, 4000, 200)
        """
        name = dir.name if isinstance(dir, Path) else Path(dir).name
        match = re.match(r"grid_map_(\d+)x(\d+)_(\d+)", name)
        if match:
            width = int(match.group(1))
            height = int(match.group(2))
            block_size = int(match.group(3))
            return width, height, block_size
        return None

    def get(self, x, y) -> GridCell:
        """
        지정 좌표의 셀을 반환한다.
        - buffer_cells에 있으면 즉시 반환
        - 없으면 블럭 캐시를 확인하여 해당 셀을 가져오고,
        블럭이 없으면 로딩을 요청한다.
        - 셀이 존재하지 않으면 더미 빈 셀(GridCell) 반환
        """
        # 1. 셀 캐시 먼저 확인
        if (x, y) in self.buffer_cells:
            return self.buffer_cells[(x, y)]

        # 2. 블럭에서 직접 조회 시도
        key = self.get_origin(x, y)
        block = self.block_cache.get(key)
        if block:
            cell = block.cells.get((x, y))
            if cell:
                self.buffer_cells[(x, y)] = cell
                return cell

        # 3. 로딩 중이 아니라면 로딩 요청
        if key not in self.block_cache and key not in self.loading_set:
            self.request_load_block(x, y)

        # 4. 임시용 빈 셀 반환
        return GridCell(x, y)
    
    def get_cell_at_center(self):
        cx, cy = self.get_center()
        return self.get(cx, cy)

    def set_buffer_width_height(self, width:int, height:int):
        self.buffer_cells_width = width
        self.buffer_cells_height = height
        self.update_buffer_cells()

    def get_center(self):
        return self.center_x, self.center_y
    
    def set_center(self, gx, gy):
        # 좌표(gx, gy)를 센터로 이동한다.
        g_logger.log_always(
            f'좌표({gx}, {gy})를 센터로 설정한다.')
        
        self.center_x = gx
        self.center_y = gy

        self.update_buffer_cells()
        self.center_changed.emit(gx, gy)

    def move_center(self, dx: int, dy: int, distance=2):
        """
        중심 좌표를 (dx, dy)만큼 직접 이동하며,
        내부적으로 set_center를 호출하지 않고 로딩 및 시그널을 직접 처리한다.
        """
        # g_logger.log_debug('move_center가 호출되었다')
        
        if dx == 0 and dy == 0:
            return

        if g_logger.debug_mode:
            t0 = time.time()
            self.move_center_started.emit(t0)

        # 현재 중심 → 목표 중심
        cx, cy = self.get_center()
        new_x = cx + dx
        new_y = cy + dy

        g_logger.log_debug(
            f'센터 이동 : 현재=({cx}, {cy}) '
            f'→ 이동량=({dx}, {dy}) → 목표=({new_x}, {new_y})'
        )

        # 경로 변경 여부에 따른 이동 사유 결정
        if self.path_detector.has_changed((cx, cy), (new_x, new_y)):
            self._move_reason = "changed"
        else:
            self._move_reason = "continue"

        self._target_step = 1

        self.center_x = new_x
        self.center_y = new_y

        # min_x = new_x - (self.buffer_cells_width // 2)
        # min_y = new_y - (self.buffer_cells_height // 2)

        # rect = QRect(min_x, min_y,
        #             self.buffer_cells_width, self.buffer_cells_height)

        # # → forward 기반으로 교체
        # if not self.is_blocks_loaded_forward_for_rect(rect, dx, dy, 
        #                                               distance):
        #     # g_logger.log_debug(
        #     #     f'좌표({new_x},{new_y})이 포함된 '
        #     #     f'사각형({rect.left()}, {rect.top()}, '
        #     #     f'{rect.width()}, {rect.height()})의 ({dx}, {dy})방향으로 '
        #     #     f'{distance}만큼 블락을 로딩한다.'
        #     #     )
                        
        #     self.load_blocks_forward_for_rect(rect, dx, dy, distance)

        self.update_buffer_cells()
        self.center_changed.emit(new_x, new_y)

        if g_logger.debug_mode:
            t1 = time.time()
            self.move_center_ended.emit(t1)
            elapsed = (t1 - t0) * 1000
            self.move_center_elapsed.emit(elapsed)
            # g_logger.log_debug(f"[move_center] 처리 시간: {elapsed:.3f} ms")
