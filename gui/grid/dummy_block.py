import json
import time
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from grid.grid_block import GridBlock, BlockLoaderThread
from grid.grid_cell import GridCell

from coord import c_coord

from utils.log_to_panel import g_logger

class DummyBlock(GridBlock):
    def __init__(
        self,
        x0: int, y0: int,
        block_size: int = 100,
        npc_chance: float = 0.05,
        terrain_ratio_normal: float = 0.5,
        terrain_ratio_road: float = 0.2,
        terrain_ratio_water: float = 0.1,
        terrain_ratio_forest: float = 0.1,
        terrain_ratio_mountain: float = 0.1,
        item_chance: float = 0.2,
        effect_chance: float = 0.1,
        event_chance: float = 0.05,
        cells: dict = None
    ):
        self.npc_chance = npc_chance
        self.terrain_ratio_normal = terrain_ratio_normal
        self.terrain_ratio_road = terrain_ratio_road
        self.terrain_ratio_water = terrain_ratio_water
        self.terrain_ratio_forest = terrain_ratio_forest
        self.terrain_ratio_mountain = terrain_ratio_mountain
        self.item_chance = item_chance
        self.effect_chance = effect_chance
        self.event_chance = event_chance

        if cells is None:
            cells = self._generate_cells(x0, y0, block_size)

        super().__init__(x0, y0, block_size, cells)

    def _generate_cells(self, x0: int, y0: int, block_size: int) -> dict:
        result = {}
        for dy in range(block_size):
            for dx in range(block_size):
                x = x0 + dx
                y = y0 + dy
                result[(x, y)] = GridCell.random(
                    x=x, y=y,
                    npc_chance=self.npc_chance,
                    terrain_ratio_normal=self.terrain_ratio_normal,
                    terrain_ratio_road=self.terrain_ratio_road,
                    terrain_ratio_water=self.terrain_ratio_water,
                    terrain_ratio_forest=self.terrain_ratio_forest,
                    terrain_ratio_mountain=self.terrain_ratio_mountain,
                    item_chance=self.item_chance,
                    effect_chance=self.effect_chance,
                    event_chance=self.event_chance,
                )
        return result

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "npc_chance": self.npc_chance,
            "terrain_ratio_normal": self.terrain_ratio_normal,
            "terrain_ratio_road": self.terrain_ratio_road,
            "terrain_ratio_water": self.terrain_ratio_water,
            "terrain_ratio_forest": self.terrain_ratio_forest,
            "terrain_ratio_mountain": self.terrain_ratio_mountain,
            "item_chance": self.item_chance,
            "effect_chance": self.effect_chance,
            "event_chance": self.event_chance,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict):
        x0 = data["x0"]
        y0 = data["y0"]
        block_size = data.get("block_size", 100)
        raw_cells = data["cells"]

        cell_dict = {}
        for raw in raw_cells:
            cell = GridCell.from_dict(raw)
            cell_dict[(cell.x, cell.y)] = cell

        return cls(
            x0=x0,
            y0=y0,
            block_size=block_size,
            npc_chance=data.get("npc_chance", 0.05),
            terrain_ratio_normal=data.get("terrain_ratio_normal", 0.5),
            terrain_ratio_road=data.get("terrain_ratio_road", 0.2),
            terrain_ratio_water=data.get("terrain_ratio_water", 0.1),
            terrain_ratio_forest=data.get("terrain_ratio_forest", 0.1),
            terrain_ratio_mountain=data.get("terrain_ratio_mountain", 0.1),
            item_chance=data.get("item_chance", 0.2),
            effect_chance=data.get("effect_chance", 0.1),
            event_chance=data.get("event_chance", 0.05),
            cells=cell_dict
        )

    def to_json(self, folder: str):
        Path(folder).mkdir(parents=True, exist_ok=True)
        data = self.to_dict()
        path = Path(folder) / f"block_{self.x0}_{self.y0}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

class DummyBlockThread(QThread):
    succeeded = Signal(c_coord, DummyBlock)
    failed = Signal(c_coord)
    loading_block_started = Signal(float)    

    def __init__(self,
                 x0: int, y0: int,
                 block_size: int = 100,
                 npc_chance: float = 0.05,
                 terrain_ratio_normal: float = 0.5,
                 terrain_ratio_road: float = 0.2,
                 terrain_ratio_water: float = 0.1,
                 terrain_ratio_forest: float = 0.1,
                 terrain_ratio_mountain: float = 0.1,
                 item_chance: float = 0.2,
                 effect_chance: float = 0.1,
                 event_chance: float = 0.05):
        super().__init__()
        self.x0 = x0
        self.y0 = y0
        self.block_size = block_size
        self.npc_chance = npc_chance
        self.terrain_ratio_normal = terrain_ratio_normal
        self.terrain_ratio_road = terrain_ratio_road
        self.terrain_ratio_water = terrain_ratio_water
        self.terrain_ratio_forest = terrain_ratio_forest
        self.terrain_ratio_mountain = terrain_ratio_mountain
        self.item_chance = item_chance
        self.effect_chance = effect_chance
        self.event_chance = event_chance
        self.result: DummyBlock | None = None

    def run(self):
        try:
            block = DummyBlock(
                x0=self.x0, y0=self.y0,
                block_size=self.block_size,
                npc_chance=self.npc_chance,
                terrain_ratio_normal=self.terrain_ratio_normal,
                terrain_ratio_road=self.terrain_ratio_road,
                terrain_ratio_water=self.terrain_ratio_water,
                terrain_ratio_forest=self.terrain_ratio_forest,
                terrain_ratio_mountain=self.terrain_ratio_mountain,
                item_chance=self.item_chance,
                effect_chance=self.effect_chance,
                event_chance=self.event_chance
            )
            self.result = block
            self.succeeded.emit(block.get_coord_key(), block)
        except Exception as e:
            g_logger.log_debug_threadsafe(
                f"[\u274c DummyBlockThread 실패] ({self.x0},{self.y0}): {e}")
            self.failed.emit(c_coord(self.x0, self.y0))

class DummyBlockLoaderThread(BlockLoaderThread):
    def run(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                block = DummyBlock.from_dict(data)
                self.succeeded.emit(block)
        except Exception as e:
            g_logger.log_debug_threadsafe(
                f"[\u274c 더미 블럭 로딩 실패] {self.path}: {e}")
            self.failed.emit(str(self.path))
