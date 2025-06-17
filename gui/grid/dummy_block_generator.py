from typing import Dict, Tuple

from grid.grid_cell import GridCell

class DummyBlock:
    @staticmethod
    def generate(
        x0: int, y0: int,
        block_size: int = 200,

        npc_chance: float = 0.05,

        terrain_ratio_normal: float = 0.5,
        terrain_ratio_road: float = 0.2,
        terrain_ratio_water: float = 0.1,
        terrain_ratio_forest: float = 0.1,
        terrain_ratio_mountain: float = 0.1,

        item_chance: float = 0.2,
        effect_chance: float = 0.1,
        event_chance: float = 0.05
    ) -> Dict[Tuple[int, int], GridCell]:
        """
        GridCell.random()을 활용한 블럭 단위 생성 함수.
        """
        result = {}

        for dy in range(block_size):
            for dx in range(block_size):
                x = x0 + dx
                y = y0 + dy

                cell = GridCell.random(
                    x=x, y=y,
                    npc_chance=npc_chance,
                    terrain_ratio_normal=terrain_ratio_normal,
                    terrain_ratio_road=terrain_ratio_road,
                    terrain_ratio_water=terrain_ratio_water,
                    terrain_ratio_forest=terrain_ratio_forest,
                    terrain_ratio_mountain=terrain_ratio_mountain,
                    item_chance=item_chance,
                    effect_chance=effect_chance,
                    event_chance=event_chance
                )
                result[(x, y)] = cell

        return result

    @staticmethod
    def to_json(
        folder: str,
        x0: int, y0: int,
        block_size: int = 200,

        npc_chance: float = 0.05,

        terrain_ratio_normal: float = 0.5,
        terrain_ratio_road: float = 0.2,
        terrain_ratio_water: float = 0.1,
        terrain_ratio_forest: float = 0.1,
        terrain_ratio_mountain: float = 0.1,

        item_chance: float = 0.2,
        effect_chance: float = 0.1,
        event_chance: float = 0.05
    ) -> None:
        from pathlib import Path
        import json

        Path(folder).mkdir(parents=True, exist_ok=True)

        cells = DummyBlock.generate(
            x0=x0, y0=y0,
            block_size=block_size,
            npc_chance=npc_chance,
            terrain_ratio_normal=terrain_ratio_normal,
            terrain_ratio_road=terrain_ratio_road,
            terrain_ratio_water=terrain_ratio_water,
            terrain_ratio_forest=terrain_ratio_forest,
            terrain_ratio_mountain=terrain_ratio_mountain,
            item_chance=item_chance,
            effect_chance=effect_chance,
            event_chance=event_chance
        )

        cells_data = [cell.to_dict() for cell in cells.values()]
        data = {
            "x0": x0,
            "y0": y0,
            "block_size": block_size,
            "cells": cells_data
        }

        filename = f"block_{x0}_{y0}.json"
        path = Path(folder) / filename

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

