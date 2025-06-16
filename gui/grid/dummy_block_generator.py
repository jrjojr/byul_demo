import random
import json
import string
from pathlib import Path
from typing import Dict, Tuple

from grid.grid_cell import GridCell, CellStatus, CellFlag, TerrainType
from grid.grid_block import GridBlock

class DummyBlock:
    @staticmethod
    def generate(
        x0: int, y0: int,
        block_size: int = 200,
        obstacle_chance: float = 0.1,
        npc_chance: float = 0.05
    ) -> Dict[Tuple[int, int], GridCell]:
        """
        랜덤 장애물 및 NPC 포함 단일 블럭 셀 딕셔너리를 생성한다.
        """
        result = {}
        for dy in range(block_size):
            for dx in range(block_size):
                x = x0 + dx
                y = y0 + dy

                cell = GridCell(x, y)

                # 기본 속성
                cell.light_level = round(random.uniform(0.3, 1.0), 2)
                cell.zone_id = random.choice(string.ascii_uppercase)
                cell.terrain = random.choice(list(TerrainType))

                # 부가 플래그 설정
                # if random.random() < 0.3:
                #     cell.flags |= random.choice([CellFlag.START, CellFlag.GOAL, CellFlag.PATH])

                # 장애물 / NPC / EMPTY 설정
                # r = random.random()
                # if r < obstacle_chance:
                #     cell.obstacle = True
                #     cell.status = CellStatus.EMPTY
                # elif r < obstacle_chance + npc_chance:
                #     npc_id = f"npc_{random.randint(1000, 9999)}"
                #     cell.add_npc(npc_id)
                #     cell.status = CellStatus.NPC
                # else:
                #     cell.status = CellStatus.EMPTY
                cell.status = CellStatus.EMPTY

                # 아이템 20% 확률
                if random.random() < 0.2:
                    cell.items.append("item_" + random.choice(["apple", "gem", "scroll"]))

                # 효과/이벤트 확률
                if random.random() < 0.1:
                    cell.effect_id = "heal_zone"
                if random.random() < 0.05:
                    cell.event_id = "trigger_lever"

                # 시간 초기값
                cell.timestamp = 0.0

                result[(x, y)] = cell
        return result

    @staticmethod
    def to_json(
        folder: str,
        x0: int, y0: int,
        block_size: int = 200,
        obstacle_chance: float = 0.1,
        npc_chance: float = 0.05
    ) -> None:
        """
        단일 블럭을 생성하여 JSON 파일로 저장한다.
        """
        Path(folder).mkdir(parents=True, exist_ok=True)

        cells = DummyBlock.generate(
            x0, y0, block_size, obstacle_chance, npc_chance)

        block = GridBlock(x0, y0, block_size, cells)

        filename = f"block_{x0}_{y0}.json"
        path = Path(folder) / filename

        with open(path, "w", encoding="utf-8") as f:
            json.dump(block.to_dict(), f, indent=4)
