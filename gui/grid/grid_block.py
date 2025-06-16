from grid.grid_cell import GridCell

from utils.log_to_panel import g_logger

class GridBlock:
    def __init__(self, x0: int, y0: int, block_size: int = 200, 
                 cells: dict = None):
        self.x0 = x0
        self.y0 = y0
        self.block_size = block_size
        self.cells = cells if cells is not None else {}

    def to_dict(self):
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

        cell_dict = {}
        for raw in raw_cells:
            cell = GridCell.from_dict(raw)
            cell_dict[(cell.x, cell.y)] = cell

        return cls(x0, y0, block_size, cell_dict)
