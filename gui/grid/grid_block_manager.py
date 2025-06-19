from pathlib import Path
import json

from collections import OrderedDict, deque

from utils.log_to_panel import g_logger

from coord import c_coord

from PySide6.QtCore import QObject, QRect, Signal, QTimer

from grid.grid_block import GridBlock
from grid.grid_cell import GridCell
from grid.dummy_block import DummyBlockThread
import time

from config import BYUL_WORLD_ENV_PATH

class GridBlockManager(QObject):
    loading_block_completed = Signal()
    to_cells_elapsed = Signal(float, int)

    def __init__(self, block_size=100, max_blocks = 18, max_parallel = 2, 
                 on_npc_spawn=None, on_npc_evict=None,
                 parent_path=BYUL_WORLD_ENV_PATH):
        super().__init__()

        self.block_size = block_size
        self.max_blocks = max_blocks
        self.max_parallel = max_parallel

        dir_name = f"grid_blocks_{block_size}_size"
        self.grid_block_path = parent_path / dir_name
        self.grid_block_path.mkdir(parents=True, exist_ok=True)

        self.block_cache: OrderedDict[c_coord, GridBlock] = OrderedDict()
        
        self._active_threads: dict[c_coord, DummyBlockThread] = {}

        self.loading_queue: deque[c_coord] = deque()
        # 중복 제거용 큐는 같은 키도 추가한다.
        # 집합으로 중복 값을 확인한다.
        self.loading_set: set[c_coord] = set()

        self._pending_timer = False

        self.on_npc_spawn = on_npc_spawn
        self.on_npc_evict = on_npc_evict

    def get_origin(self, x: int, y: int) -> c_coord:
        return c_coord(
            (x // self.block_size) * self.block_size,
            (y // self.block_size) * self.block_size
        )

    def request_load_block(self, x: int, y: int, save_to_json: bool = True):
        key = self.get_origin(x, y)

        if key in self.block_cache or key in self.loading_set:
            return

        g_logger.log_debug(f'블럭({key.x}, {key.y}) 로딩이 큐에 추가됨.')

        self.loading_queue.append(key)
        self.loading_set.add(key)

        if not self._pending_timer:
            self._pending_timer = True
            QTimer.singleShot(0, self._process_next_block)

    def _process_next_block(self):
        self._pending_timer = False

        while (self.loading_queue and
               len(self._active_threads) < self.max_parallel):

            key= self.loading_queue.popleft()
            thread = DummyBlockThread(key.x, key.y, self.block_size)

            thread.succeeded.connect(self._on_block_load_succeeded)
            thread.failed.connect(self._on_block_load_failed)

            self._active_threads[key] = thread
            thread.start()            

        # ❗️다음 예약이 필요한 경우
        if self.loading_queue and not self._pending_timer:
            self._pending_timer = True
            QTimer.singleShot(0, self._process_next_block)

        # ✅ 완료 여부 알림
        if not self.loading_queue and not self._active_threads:
            self.loading_block_completed.emit()

    def _on_block_load_succeeded(self, key: c_coord):
        t0 = time.perf_counter()

        if key in self.block_cache:
            g_logger.log_debug(
                f"[load_block] ⚠️ 이미 처리된 key (중복 signal?): {key}")
            self._finalize_thread(key)
            return

        thread = self._active_threads.get(key)
        if not thread:
            g_logger.log_debug(f"[load_block] ❓ 쓰레드 누락: {key}")
            return

        self.block_cache[key] = thread.result

        # 💡 블락 내 npc_id 정보 기반으로 NPC 생성 요청
        if self.on_npc_spawn:
            self.on_npc_spawn(key)

        self.__touch_block(key)
        self.__evict_if_needed()

        g_logger.log_debug(f"[load_block] ✅ 완료: {key}")
        self._finalize_thread(key)

        t1 = time.perf_counter()
        g_logger.log_debug(
            f"🎯 _on_block_load_succeeded 처리 시간: {(t1 - t0)*1000:.3f}ms")

    def _finalize_thread(self, key: c_coord):
        self.loading_set.discard(key)

        thread = self._active_threads.pop(key, None)
        if thread:
            thread.quit()
            thread.wait()

        if not self._pending_timer:
            self._pending_timer = True
            QTimer.singleShot(0, self._process_next_block)

    def _on_block_load_failed(self, key: c_coord):
        # 중복 처리 방어
        if key not in self._active_threads:
            g_logger.log_debug(
                f"[load_block] ⚠️ 실패 시그널 중복 또는 이미 finalize됨: {key}")
            return

        g_logger.log_debug(f"[load_block] ❌ 실패: {key}")
        self._finalize_thread(key)

    def __touch_block(self, key:c_coord):
        if key in self.block_cache:
            g_logger.log_debug(f'block_cache에 key : {key} 가 존재한다 제거 예약한다.')
            self.block_cache.move_to_end(key)

    def __evict_if_needed(self):
        while len(self.block_cache) > self.max_blocks:
            old_key, _ = self.block_cache.popitem(last=False)
            g_logger.log_debug(f"[evict_block] ⛔ 제거: {old_key}")

            if self.on_npc_evict:
                self.on_npc_evict(old_key) 

    def load_blocks_around(self, center_x, center_y, around_range=1):
        base = self.get_origin(center_x, center_y)
        base_bx = base.x
        base_by = base.y
        for dy in range(-around_range, around_range + 1):
            for dx in range(-around_range, around_range + 1):
                bx = base_bx + dx * self.block_size
                by = base_by + dy * self.block_size
                self.request_load_block(bx, by)

    def to_cells(self, start_x=0, start_y=0, width=0, height=0):
        if g_logger.debug_mode:
            start = time.time()
            
        cells = {}

        if width == 0 and height == 0:
            # 전체 블럭 대상으로 처리
            block_keys = list(self.block_cache.keys())
            use_all_cells = True
        else:
            # 특정 영역의 블럭만
            block_keys = self.get_blocks_in_rect(
                start_x, start_y, width, height)
            use_all_cells = False

        for key in block_keys:
            if key not in self.block_cache:
                self.request_load_block(key.x, key.y)
                continue

            block = self.block_cache[key]
            if use_all_cells:
                cells.update(block.cells)
            else:
                for (x, y), cell in block.cells.items():
                    if start_x <= x < start_x + width and \
                        start_y <= y < start_y + height:

                        cells[(x, y)] = cell

        if g_logger.debug_mode:
            # g_logger.log_debug(f"[to_cells] 완료: {len(cells)}개, "
            #             f"{(time.time() - start) * 1000:.3f}ms")
            elapsed = time.time() - start
            self.to_cells_elapsed.emit(elapsed, len(cells))

        return cells

    def clear_block_cache(self):
        self.block_cache.clear()

    def set_max_blocks(self, new_max):
        """
        블록 캐시의 최대 개수를 동적으로 조정하고, 초과분 제거
        """
        self.max_blocks = max(1, new_max)  # 최소 1 이상 보장

        while len(self.block_cache) > self.max_blocks:
            old_key, _ = self.block_cache.popitem(last=False)

    def is_inside_block(self, x, y, block_x, block_y):
        """좌표 (x, y)가 키가(block_x, block_y)인 블록의 영역 안에 있는지 확인"""
        return (
            block_x <= x < block_x + self.block_size and
            block_y <= y < block_y + self.block_size
        )

    def is_block_loaded_for(self, x, y):
        return self.get_origin(x, y) in self.block_cache

    def is_blocks_loaded_for_rect(self, rect: QRect):
        keys = self.get_blocks_in_rect(rect.left(), rect.top(),
                                       rect.width(), rect.height())
        for key in keys:
            if key not in self.block_cache:
                return False
        return True
    
    def is_blocks_loaded_forward(self, x, y, dx, dy, distance=1):
        """
        좌표 (x, y)를 기준으로 방향 (dx, dy)로 distance만큼 이동한 블럭들이
        선로딩되어 있는지 확인한다.
        하나라도 로딩되지 않았다면 False 반환.
        """
        if dx == 0 and dy == 0:
            return True

        bs = self.block_size
        is_loaded = self.is_block_loaded_for

        for i in range(1, distance + 1):
            cx = x + dx * i * bs
            cy = y + dy * i * bs

            if dx == 0:
                check_points = [
                    (cx - bs, cy),
                    (cx, cy),
                    (cx + bs, cy),
                ]
            elif dy == 0:
                check_points = [
                    (cx, cy - bs),
                    (cx, cy),
                    (cx, cy + bs),
                ]
            else:
                check_points = [
                    (cx, cy),
                    (cx - dx * bs, cy),
                    (cx, cy - dy * bs),
                    (cx - dx * bs, cy - dy * bs),
                ]

            for px, py in check_points:
                if not is_loaded(px, py):
                    return False

        return True

    def is_blocks_loaded_forward_for_rect(
        self, rect, dx, dy, distance=1, offset=0):

        if dx == 0 and dy == 0:
            return True

        bs = self.block_size

        # 💡 offset으로 rect 확장
        expanded = QRect(
            rect.left() - offset,
            rect.top() - offset,
            rect.width() + offset * 2,
            rect.height() + offset * 2
        )

        for y in range(expanded.top(), expanded.bottom() + 1, bs):
            for x in range(expanded.left(), expanded.right() + 1, bs):
                for i in range(1, distance + 1):
                    fx = x + dx * i * bs
                    fy = y + dy * i * bs

                    if dx == 0:
                        targets = [(fx - bs, fy), (fx, fy), (fx + bs, fy)]
                    elif dy == 0:
                        targets = [(fx, fy - bs), (fx, fy), (fx, fy + bs)]
                    else:
                        targets = [
                            (fx, fy),
                            (fx - dx * bs, fy),
                            (fx, fy - dy * bs),
                            (fx - dx * bs, fy - dy * bs),
                        ]

                    for tx, ty in targets:
                        if not self.is_block_loaded_for(tx, ty):
                            return False

        return True

    def load_blocks_around(self, center_x, center_y, around_range=1):
        g_logger.log_debug(
            f'load blocks({center_x}, {center_y}, {around_range}) 실행됨')

        self.request_load_block(center_x, center_y)

        # self._initial_block_keys = set()

        if around_range > 0:
            base = self.get_origin(center_x, center_y)

            for dy in range(-around_range, around_range + 1):
                for dx in range(-around_range, around_range + 1):
                    bx = base.x + dx * self.block_size
                    by = base.y + dy * self.block_size
                    key = (bx, by)
                    
                    # self._initial_block_keys.add(key)
                    
                    if key in self.block_cache:
                        self.block_cache.move_to_end(key)  # LRU 갱신
                    elif key not in self.loading_blocks:
                        self.request_load_block(bx, by)
    
    def load_blocks_around_for_rect(self, rect:QRect, 
                                    around_range=1, offset=0):
        """
        지정된 rect 주위의 4개 꼭짓점 블럭이 로딩되어 있는지 확인하고,
        비어 있는 경우 해당 위치 주변 블럭을 로딩한다.
        """
        center_x = rect.left() + (rect.width() // 2)
        center_y = rect.top() + (rect.height() // 2)

        # g_logger.log_debug(
        #     f'중심좌표({center_x},{center_y})이 '
        #     f'포함된 사각형({rect.left()}, {rect.top()}, '
        #     f'{rect.width()}, {rect.height()})의 블락과 주변블락을 로딩한다.'
        # )        
        self.request_load_block(center_x, center_y)

        if around_range > 0:
            min_x = rect.left() - offset
            min_y = rect.top() - offset
            max_x = rect.left() + rect.width() + 1 + offset
            max_y = rect.top() + rect.height() + 1 + offset

            corners = [
                (min_x, min_y, "좌상단"),
                (max_x, min_y, "우상단"),
                (min_x, max_y, "좌하단"),
                (max_x, max_y, "우하단")
            ]

            for x, y, label in corners:
                # if not self.is_block_loaded_for(x, y):
                # g_logger.log_debug(
                #     f'{label}({x}, {y})을 포함하는 블락을 로딩한다.'
                # )

                self.request_load_block(x, y)                

    def load_blocks_forward(self, x, y, dx, dy, distance=1):
        if dx == 0 and dy == 0:
            return  # 움직이지 않았음

        self.request_load_block(x+dx, y+dy)
        
        if distance > 0:
            # 기준 블록 좌표
            base = self.get_origin(x, y)
            base_bx = base.x
            base_by = base.y

            for i in range(1, distance + 1):
                bx = base_bx + dx * i * self.block_size
                by = base_by + dy * i * self.block_size

                if dx == 0:
                    # 위, 아래로만 움직였다
                    # x가 블락거리 -1, 0, 1 세개의 블락을 미리 로딩 준비한다.
                    self.request_load_block(bx - self.block_size, by)
                    
                    self.request_load_block(bx, by)
                    self.request_load_block(bx + self.block_size, by)                
                    pass
                elif dy == 0:
                    # 왼쪽, 오른쪽으로만 움직였다
                    # y가 블락거리 -1, 0, 1 세개의 블락을 미리 로딩 준비한다.
                    self.request_load_block(bx, by - self.block_size)
                    
                    self.request_load_block(bx, by)
                    self.request_load_block(bx, by + self.block_size)                
                    pass
                # elif dx < 0 and dy < 0:
                #     # 왼쪽 위의 3개의 블락을 로딩해야 한다
                #     pass
                # elif dx < 0 and dy > 0:
                #     # 왼쪽 아래의 3개의 블락을 로딩해야 한다
                #     pass
                # elif dx > 0 and dy < 0:
                #     # 오른쪽 위의 3개의 블락을 로딩해야 한다
                #     pass
                # elif dx > 0 and dy > 0:
                #     # 오른쪽 아래의 3개의 블락을 로딩해야 한다
                #     pass
                else:
                    # 4군데 귀퉁이
                    # 대각선 이동 → 해당 블럭과 3방향 블럭 포함
                    self.request_load_block(bx, by)
                    self.request_load_block(bx - dx * self.block_size, by)
                    
                    self.request_load_block(bx, by - dy * self.block_size)
                    
                    self.request_load_block(bx - dx * self.block_size, 
                                            by - dy * self.block_size)
            pass

    def load_blocks_forward_for_rect(self, rect: QRect, 
                                     dx: int, dy: int, distance=1):
        """
        지정된 rect 범위를 기준으로 (dx, dy) 방향으로 
        1부터 distance 거리까지의 forward 블럭들을 모두 비동기로 로딩한다.
        """
        if dx == 0 and dy == 0:
            return

        bs = self.block_size
        visited = set()

        base_keys = self.get_blocks_in_rect(
            rect.left(), rect.top(), rect.width(), rect.height())

        for key in base_keys:
            # i = distance
            # fx = bx + dx * i * bs
            # fy = by + dy * i * bs
            bx = key.x
            by = key.y

            for i in range(1, distance + 1): 
                fx = bx + dx * i * bs
                fy = by + dy * i * bs

                if dx == 0:
                    targets = [(fx - bs, fy), (fx, fy), (fx + bs, fy)]
                elif dy == 0:
                    targets = [(fx, fy - bs), (fx, fy), (fx, fy + bs)]
                else:
                    targets = [
                        (fx, fy),
                        (fx - dx * bs, fy),
                        (fx, fy - dy * bs),
                        (fx - dx * bs, fy - dy * bs),
                    ]

                for tx, ty in targets:
                    key = self.get_origin(tx, ty)
                    if key not in visited:
                        visited.add(key)
                        self.request_load_block(tx, ty)

    def get_blocks_in_rect(self, start_x, start_y, width, height):
        """
        주어진 범위를 포함하는 모든 블럭의 키(bx, by)를 집합으로 반환한다.
        """
        end_x = start_x + width - 1
        end_y = start_y + height - 1

        start = self.get_origin(start_x, start_y)
        bx_start = start.x
        by_start = start.y

        end = self.get_origin(end_x, end_y)
        bx_end = end.x
        by_end = end.y

        result_keys = set()

        for by in range(by_start, by_end + 1, self.block_size):
            for bx in range(bx_start, bx_end + 1, self.block_size):
                result_keys.add(c_coord(bx, by))

        return result_keys

    def get_blocks_to_target_rect(
        self, rect: QRect, dx: int, dy: int, target_step: int
    ) -> set[c_coord]:
        """
        주어진 rect를 기준으로 (dx, dy) 방향으로 
        target_step 떨어진 블럭 좌표들을 반환한다.
        반환되는 블럭들은 중심 기준 forward 방향 블럭들이다.
        """
        if dx == 0 and dy == 0:
            return set()

        bs = self.block_size
        targets = set()

        base_keys = self.get_blocks_in_rect(
            rect.left(), rect.top(), rect.width(), rect.height()
        )

        for key in base_keys:
            bx = key.x
            by = key.y
            fx = bx + dx * target_step * bs
            fy = by + dy * target_step * bs

            if dx == 0:
                cand = [(fx - bs, fy), (fx, fy), (fx + bs, fy)]
            elif dy == 0:
                cand = [(fx, fy - bs), (fx, fy), (fx, fy + bs)]
            else:
                cand = [
                    (fx, fy),
                    (fx - dx * bs, fy),
                    (fx, fy - dy * bs),
                    (fx - dx * bs, fy - dy * bs),
                ]

            for tx, ty in cand:
                targets.add(self.get_origin(tx, ty))

        return targets

    def get_loaded_blocks_in_rect(self, start_x, start_y, width, height):
        """
        주어진 범위에 걸친 블럭들 중, block_cache에 로드된 블럭 키만 집합으로 반환한다.
        """
        end_x = start_x + width - 1
        end_y = start_y + height - 1

        start = self.get_origin(start_x, start_y)
        bx_start = start.x
        by_start = start.y

        end = self.get_origin(end_x, end_y)
        bx_end = end.x
        by_end = end.y

        result_keys = set()

        for by in range(by_start, by_end + 1, self.block_size):
            for bx in range(bx_start, bx_end + 1, self.block_size):
                key = (bx, by)
                if key in self.block_cache:
                    result_keys.add(key)

        return result_keys

    def save_cells_to_blocks(self, cells):
        blocks = {}
        block_sizes = {}
        fixed_block_size = (self.block_size, self.block_size)
        for (x, y), cell in cells.items():
            key = self.get_origin(x, y)
            if key not in blocks:
                path = Path(self.grid_block_path) / f"block_{key.x}_{key.y}.json"

                if path.exists():
                    with open(path, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                    block_size_x = existing.get("width", self.block_size)
                    block_size_y = existing.get("height", self.block_size)

                    if (block_size_x, block_size_y) != fixed_block_size:
                        raise ValueError(
"Block size mismatch in {}: expected {}, got ({}, {})".format(
    path, fixed_block_size, block_size_x, block_size_y)
                    )
                    block_sizes[key] = fixed_block_size
                    cell_dict = {
                        (c["x"], c["y"]): GridCell.from_dict(c)
                        for c in existing["cells"]
                    }
                    blocks[key] = cell_dict

                else:
                    block_sizes[key] = fixed_block_size
                    blocks[key] = {}
                    
            blocks[key][(x, y)] = cell

        Path(self.grid_block_path).mkdir(parents=True, exist_ok=True)
        for key, cell_dict in blocks.items():
            bx = key.x
            by = key.y
            bw, bh = block_sizes[(bx, by)]
            block_data = GridBlock(bx, by, bw, bh, 
                [cell.to_dict() for cell in cell_dict.values()])
            
            path = Path(self.grid_block_path) / f"block_{bx}_{by}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(block_data.to_json(), f, indent=4)

