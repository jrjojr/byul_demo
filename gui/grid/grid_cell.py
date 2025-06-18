from enum import Enum, Flag, auto
from typing import Optional, Any
from PySide6.QtGui import QColor

from route import RouteDir

import random
import string

class CellStatus(Enum):
    EMPTY = 0
    NPC = 1

class CellFlag(Flag):
    NONE = 0
    START = auto()
    GOAL = auto()
    ROUTE = auto()
    VISITED = auto()

class TerrainType(Enum):
    NORMAL = 0
    WATER = 1
    MOUNTAIN = 2
    FOREST = 3
    ROAD = 4

class GridCell:
    def __init__(self, x: int, y: int,
                 status: CellStatus = CellStatus.EMPTY,
                 terrain: TerrainType = TerrainType.NORMAL):
        self.x = x
        self.y = y

        self.status: CellStatus = status
        self.flags: CellFlag = CellFlag.NONE
        self.npc_ids: list[str] = []
        self.route_dir: RouteDir = RouteDir.UNKNOWN

        self.terrain: TerrainType = terrain
        self.light_level: float = 1.0
        self.zone_id: Optional[str] = None
        self.items: list[str] = []
        self.owner_npc_id: Optional[str] = None
        self.effect_id: Optional[str] = None
        self.event_id: Optional[str] = None
        self.timestamp: float = 0.0
        self.custom_data: dict[str, Any] = {}

    def add_npc(self, npc_id: str):
        if npc_id not in self.npc_ids:
            self.npc_ids.append(npc_id)
        self.status = CellStatus.NPC

    def remove_npc(self, npc_id: str):
        if npc_id in self.npc_ids:
            self.npc_ids.remove(npc_id)
        if len(self.npc_ids) <= 0:
            self.status = CellStatus.EMPTY

    def has_flag(self, flag: CellFlag) -> bool:
        return flag in self.flags

    def add_flag(self, flag: CellFlag):
        self.flags |= flag

    def remove_flag(self, flag: CellFlag):
        self.flags &= ~flag

    def clear_flags(self):
        self.flags = CellFlag.NONE

    def get_priority_flag(self) -> Optional[CellFlag]:
        for f in [CellFlag.START, CellFlag.GOAL, CellFlag.ROUTE, CellFlag.VISITED]:
            if f in self.flags:
                return f
        return None

    def get_color(self) -> QColor:
        if self.status == CellStatus.NPC:
            return QColor(255, 200, 0)

        flag = self.get_priority_flag()
        if flag == CellFlag.START:
            return QColor(0, 255, 0)
        elif flag == CellFlag.GOAL:
            return QColor(255, 0, 0)
        elif flag == CellFlag.ROUTE:
            return QColor(0, 0, 255)
        elif flag == CellFlag.VISITED:
            return QColor(180, 180, 180)

        return QColor(255, 255, 255)

    def get_cell_type_text(self) -> str:
        if self.status == CellStatus.NPC:
            return self.npc_ids[0] if self.npc_ids else "N"

        flag = self.get_priority_flag()
        if flag == CellFlag.START:
            return "S"
        elif flag == CellFlag.GOAL:
            return "G"
        elif flag == CellFlag.ROUTE:
            return "*"
        return ""

    def text(self):
        return f""""x": {self.x},
"y": {self.y},
t:{self.terrain.name},
"ids": {self.npc_ids}
"""

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "status": self.status.value,
            "flags": self.flags.value,
            "npc_ids": self.npc_ids,
            "route_dir": self.route_dir.value,
            "terrain": self.terrain.value,
            "light_level": self.light_level,
            "zone_id": self.zone_id,
            "items": self.items,
            "owner_npc_id": self.owner_npc_id,
            "effect_id": self.effect_id,
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "custom_data": self.custom_data
        }

    def get_route_image(self):
        if self.has_flag(CellFlag.ROUTE):
            route_dir = self.route_dir

            if route_dir == RouteDir.RIGHT:
                icon_path = DEFAULT_ROUTE_RI_PATH
                pass
            elif route_dir == RouteDir.TOP_RIGHT:
                icon_path = DEFAULT_ROUTE_TR_PATH
                pass
            elif route_dir == RouteDir.TOP:
                icon_path = DEFAULT_ROUTE_TO_PATH
                pass
            elif route_dir == RouteDir.TOP_LEFT:
                icon_path = DEFAULT_ROUTE_TL_PATH
                pass
            elif route_dir == RouteDir.LEFT:
                icon_path = DEFAULT_ROUTE_LE_PATH
                pass
            elif route_dir == RouteDir.DOWN_LEFT:
                icon_path = DEFAULT_ROUTE_DL_PATH
                pass
            elif route_dir == RouteDir.DOWN:
                icon_path = DEFAULT_ROUTE_DO_PATH
                pass
            elif route_dir == RouteDir.DOWN_RIGHT:
                icon_path = DEFAULT_ROUTE_DR_PATH
                pass
            else:
                # 알려진 방향이 아니다. 기본값
                # icon_path = None
                icon_path = DEFAULT_ROUTE_UN_PATH
                pass 
        # return load_image(icon_path)
        return icon_path
    
    @classmethod
    def from_dict(cls, data: dict):
        cell = cls(
            x=data["x"],
            y=data["y"],
            status=CellStatus(data.get("status", 0)),
            terrain=TerrainType(data.get("terrain", 0))
        )
        cell.flags = CellFlag(data.get("flags", 0))
        cell.npc_ids = data.get("npc_ids", [])
        cell.route_dir = RouteDir(data.get("route_dir", 0))
        cell.light_level = data.get("light_level", 1.0)
        cell.zone_id = data.get("zone_id")
        cell.items = data.get("items", [])
        cell.owner_npc_id = data.get("owner_npc_id")
        cell.effect_id = data.get("effect_id")
        cell.event_id = data.get("event_id")
        cell.timestamp = data.get("timestamp", 0.0)
        cell.custom_data = data.get("custom_data", {})
        return cell

    @classmethod
    def random(cls,
        x: int, y: int,
        npc_chance: float = 0.05,
        terrain_ratio_normal: float = 0.5,
        terrain_ratio_road: float = 0.2,
        terrain_ratio_water: float = 0.1,
        terrain_ratio_forest: float = 0.1,
        terrain_ratio_mountain: float = 0.1,
        item_chance: float = 0.2,
        effect_chance: float = 0.1,
        event_chance: float = 0.05
    ) -> "GridCell":
        """
        지정된 위치 (x, y)에 랜덤 속성을 가진 GridCell 하나 생성.
        """
        cell = cls(x, y)
        cell.light_level = round(random.uniform(0.3, 1.0), 2)
        cell.zone_id = random.choice(string.ascii_uppercase)

        # Terrain 결정 (비율 기반)
        terrain_weights = {
            TerrainType.NORMAL: terrain_ratio_normal,
            TerrainType.ROAD: terrain_ratio_road,
            TerrainType.WATER: terrain_ratio_water,
            TerrainType.FOREST: terrain_ratio_forest,
            TerrainType.MOUNTAIN: terrain_ratio_mountain,
        }
        total_ratio = sum(terrain_weights.values())
        r = random.random()
        acc = 0.0
        for terrain, ratio in terrain_weights.items():
            acc += ratio / total_ratio
            if r <= acc:
                cell.terrain = terrain
                break

        # NPC 설정
        if random.random() < npc_chance:
            npc_id = f"npc_{random.randint(1000, 9999)}"
            cell.status = CellStatus.NPC
            cell.npc_ids.append(npc_id)
        else:
            cell.status = CellStatus.EMPTY

        # 아이템 / 효과 / 이벤트
        if random.random() < item_chance:
            cell.items.append("item_" + random.choice(["apple", "gem", "scroll"]))
        if random.random() < effect_chance:
            cell.effect_id = "heal_zone"
        if random.random() < event_chance:
            cell.event_id = "trigger_lever"

        cell.timestamp = 0.0
        return cell
