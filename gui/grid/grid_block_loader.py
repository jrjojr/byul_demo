from PySide6.QtCore import QThread, Signal

from grid.grid_cell import GridCell
from grid.dummy_block_generator import DummyBlock
from grid.grid_block import GridBlock

from coord import c_coord

import time

from pathlib import Path

import json
import re

from utils.log_to_panel import g_logger
    
class BlockLoaderThread(QThread):
    # succeeded = Signal(c_coord, dict)  # (bx, by), cells: dict[(x, y)] = GridCell
    succeeded = Signal(c_coord)
    failed = Signal(c_coord)          # (bx, by)
    loading_block_started = Signal(float)

    def __init__(self, folder, x0, y0, block_size,
                 save_to_json=True, parent=None):
        """
        - folder: 블럭 파일 저장 폴더
        - x0, y0: 중심 좌표 (이를 기준으로 블럭 위치 계산)
        - block_size: 블럭 한 변의 크기
        - save_to_json: 생성 시 JSON 저장 여부 (False면 메모리 기반 생성)
        """
        super().__init__(parent)
        self.folder = Path(folder)
        self.x0 = x0
        self.y0 = y0
        self.block_size = block_size
        self.save_to_json = save_to_json
        self.result_dict = dict()

    def run(self):
        success, key = self._load_or_generate_block()
        if success:
            self.succeeded.emit(key)
        else:
            self.failed.emit(key)

    def _load_or_generate_block(self) -> tuple[bool, c_coord]:
        bx = (self.x0 // self.block_size) * self.block_size
        by = (self.y0 // self.block_size) * self.block_size
        key = c_coord(bx, by)
        path = self.folder / f"block_{bx}_{by}.json"

        g_logger.log_debug_threadsafe(
            f'🔍 경로 확인: {path} / 존재 여부: {path.exists()}')

        if g_logger.debug_mode:
            t0 = time.time()
            self.loading_block_started.emit(t0)

        # 1. JSON 존재 시 로딩
        if path.exists():
            g_logger.log_debug_threadsafe(f'{path} exists. loading start')
            success = self._load_block_from_json(path, key)
            return (success, key)

        # 2. JSON 저장 설정이 켜진 경우
        if self.save_to_json:
            g_logger.log_debug_threadsafe(
                f'{path} not exists. save to json enabled. generating & saving...')
            success = self._generate_block_and_save_json(path, key)
            return (success, key)

        # 3. 메모리에서만 생성
        g_logger.log_debug_threadsafe(
            f'{path} not exists. save to json disabled. generating in memory...')
        success = self._generate_block_in_memory(key)
        return (success, key)            

    def _load_block_from_json(self, path: Path, key) -> bool:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                cell_dict = {
                    (c["x"], c["y"]): GridCell.from_dict(c)
                    for c in data["cells"]
                }
                self.result_dict = cell_dict
                # g_logger.log_debug_threadsafe(
                #     f'쓰레드에서 id(cell_dict): {id(cell_dict)}')
                # g_logger.log_debug_threadsafe(
                #     f'쓰레드에서 key({key[0]}, {key[1]}), 
                #       id(cell_dict) : {id(cell_dict)}')
                return True
        except Exception as e:
            print(f"[❌ 로딩 실패] {path.name}: {e}")
            return False
                
    def _generate_block_in_memory(self, key: c_coord) -> bool:
        try:
            bx = key.x
            by = key.y
            cell_dict = {
                (bx + dx, by + dy): GridCell(bx + dx, by + dy)
                for dy in range(self.block_size)
                for dx in range(self.block_size)
            }
            self.result_dict = cell_dict
            return True
        except Exception as e:
            print(f"[❌ 메모리 생성 실패] {key}: {e}")
            return False    

    def _generate_block_and_save_json(self, path: Path,
                                      key: c_coord) -> bool:
        try:
            bx = key.x
            by = key.y
            cells = DummyBlock.generate(bx, by, self.block_size)
            block = GridBlock(bx, by, self.block_size, cells)

            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(block.to_dict(), f, indent=4)

            self.result_dict = cells
            return True
        except Exception as e:
            print(f"[❌ 저장 실패] {key}: {e}")
            return False    
