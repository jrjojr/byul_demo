from typing import Dict, Tuple
from grid.grid_cell import GridCell
from coord import c_coord

import json
from pathlib import Path
from PySide6.QtCore import QThread, Signal

from utils.log_to_panel import g_logger

import json
from pathlib import Path
from PySide6.QtCore import QThread, Signal

from coord import c_coord
from utils.log_to_panel import g_logger

from coord import c_coord

import time

class GridBlock:
    def __init__(self, x0: int, y0: int, block_size: int = 100,
                 cells: Dict[c_coord, GridCell] = None):
        self.x0 = x0
        self.y0 = y0
        self.block_size = block_size
        self.cells: Dict[c_coord, GridCell] = cells if cells is not None else {}

    def to_dict(self) -> dict:
        return {
            "x0": self.x0,
            "y0": self.y0,
            "block_size": self.block_size,
            "cells": [cell.to_dict() for cell in self.cells.values()]
        }

    @classmethod
    def from_dict(cls, data: dict):
        x0 = data["x0"]
        y0 = data["y0"]
        block_size = data["block_size"]
        raw_cells = data["cells"]

        cell_dict: Dict[c_coord, GridCell] = {}
        for raw in raw_cells:
            cell = GridCell.from_dict(raw)
            cell_dict[(cell.x, cell.y)] = cell

        return cls(x0, y0, block_size, cell_dict)

    def get_key(self) -> c_coord:
        return (self.x0, self.y0)

    def get_coord_key(self) -> c_coord:
        return c_coord(self.x0, self.y0)

    def __getitem__(self, pos: c_coord) -> GridCell:
        return self.cells[pos]

    def __setitem__(self, pos: c_coord, cell: GridCell):
        self.cells[pos] = cell

    def __contains__(self, pos: c_coord) -> bool:
        return pos in self.cells

    def __len__(self) -> int:
        return len(self.cells)

    def __iter__(self):
        return iter(self.cells.items())

class BlockThread(QThread):
    succeeded = Signal(c_coord)
    failed = Signal(c_coord)
    loading_block_started = Signal(float)

    def __init__(self, block: GridBlock):
        super().__init__()
        self.block = block
        self.result_dict = {}

    def run(self):
        key = self.block.get_coord_key()
        self.loading_block_started.emit(time.time())
        try:
            self.result_dict = self.block.cells
            self.succeeded.emit(key)
        except Exception as e:
            g_logger.log_debug_threadsafe(f"[\u274c 블럭 생성 실패] {key}: {e}")
            self.failed.emit(key)

class BlockSaverThread(QThread):
    succeeded = Signal(c_coord)
    failed = Signal(c_coord)

    def __init__(self, block: GridBlock, folder: str):
        super().__init__()
        self.block = block
        self.folder = Path(folder)

    def run(self):
        key = self.block.get_coord_key()
        try:
            self.folder.mkdir(parents=True, exist_ok=True)
            path = self.folder / f"block_{self.block.x0}_{self.block.y0}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.block.to_dict(), f, indent=4, ensure_ascii=False)
            self.succeeded.emit(key)
        except Exception as e:
            g_logger.log_debug_threadsafe(f"[\u274c 블럭 저장 실패] {key}: {e}")
            self.failed.emit(key)

class BlockLoaderThread(QThread):
    succeeded = Signal(GridBlock)
    failed = Signal(str)

    def __init__(self, path: Path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                block = GridBlock.from_dict(data)
                self.succeeded.emit(block)
        except Exception as e:
            g_logger.log_debug_threadsafe(f"[\u274c 블럭 로딩 실패] {self.path}: {e}")
            self.failed.emit(str(self.path))
