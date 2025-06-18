from typing import Dict
from PySide6.QtGui import QPixmap
from pathlib import Path

from route import RouteDir
from config import IMAGES_PATH

DEFAULT_NPC_IMAGE_PATH = IMAGES_PATH / "npc"
NPC_UN_PATH = 'byul_world_npc_un.png'
NPC_RI_PATH = 'byul_world_npc_ri.png'
NPC_TR_PATH = 'byul_world_npc_tr.png'
NPC_TO_PATH = 'byul_world_npc_to.png'
NPC_TL_PATH = 'byul_world_npc_tl.png'
NPC_LE_PATH = 'byul_world_npc_le.png'
NPC_DL_PATH = 'byul_world_npc_dl.png'
NPC_DO_PATH = 'byul_world_npc_do.png'
NPC_DR_PATH = 'byul_world_npc_dr.png'
SELECTED_NPC_PATH = 'byul_world_npc_sl.png'

DEFAULT_ROUTE_IMAGE_PATH = IMAGES_PATH / "route"
ROUTE_UN_PATH = 'byul_world_route_un.png'
ROUTE_RI_PATH = 'byul_world_route_ri.png'
ROUTE_TR_PATH = 'byul_world_route_tr.png'
ROUTE_TO_PATH = 'byul_world_route_to.png'
ROUTE_TL_PATH = 'byul_world_route_tl.png'
ROUTE_LE_PATH = 'byul_world_route_le.png'
ROUTE_DL_PATH = 'byul_world_route_dl.png'
ROUTE_DO_PATH = 'byul_world_route_do.png'
ROUTE_DR_PATH = 'byul_world_route_dr.png'

OBSTACLE_PATH = 'byul_world_obstacle.png'
OBSTACLE_FOR_NPC_PATH = 'byul_world_obstacle_for_npc.png'

START_PATH = 'byul_world_start.png'
GOAL_PATH = 'byul_world_goal.png'
EMPTY_PATH = 'byul_world_empty.png'

class ImageManager:
    _npc_image_cache: Dict[str, Dict[RouteDir, QPixmap]] = {}
    _route_image_cache: Dict[str, Dict[RouteDir, QPixmap]] = {}
    _obstacle_for_npc_image_cache: QPixmap = None
    _empty_image_cache:QPixmap = None
    _goal_image_cache:QPixmap = None
    _selected_npc_image_cache:QPixmap = None

    @classmethod
    def _normalize_path(cls, path: Path | None) -> Path:
        return path if path else DEFAULT_NPC_IMAGE_PATH

    @classmethod
    def _load(cls, rel_path: str, base_path: Path=None) -> QPixmap:
        return QPixmap(str(base_path / rel_path))

    @classmethod
    def get_npc_image_paths(cls, path: Path | None = None) -> \
        Dict[RouteDir, Path]:

        base = cls._normalize_path(path)
        return {
            RouteDir.UNKNOWN: base / NPC_UN_PATH,
            RouteDir.RIGHT: base / NPC_RI_PATH,
            RouteDir.TOP_RIGHT: base / NPC_TR_PATH,
            RouteDir.TOP: base / NPC_TO_PATH,
            RouteDir.TOP_LEFT: base / NPC_TL_PATH,
            RouteDir.LEFT: base / NPC_LE_PATH,
            RouteDir.DOWN_LEFT: base / NPC_DL_PATH,
            RouteDir.DOWN: base / NPC_DO_PATH,
            RouteDir.DOWN_RIGHT: base / NPC_DR_PATH,
        }

    @classmethod
    def get_npc_image_set(cls, path: Path | None = None) -> \
        Dict[RouteDir, QPixmap]:

        base = cls._normalize_path(path)
        key = str(base.resolve())

        if key in cls._npc_image_cache:
            return cls._npc_image_cache[key]

        images = {
            RouteDir.UNKNOWN: cls._load(NPC_UN_PATH, base),
            RouteDir.RIGHT: cls._load(NPC_RI_PATH, base),
            RouteDir.TOP_RIGHT: cls._load(NPC_TR_PATH, base),
            RouteDir.TOP: cls._load(NPC_TO_PATH, base),
            RouteDir.TOP_LEFT: cls._load(NPC_TL_PATH, base),
            RouteDir.LEFT: cls._load(NPC_LE_PATH, base),
            RouteDir.DOWN_LEFT: cls._load(NPC_DL_PATH, base),
            RouteDir.DOWN: cls._load(NPC_DO_PATH, base),
            RouteDir.DOWN_RIGHT: cls._load(NPC_DR_PATH, base),
        }

        cls._npc_image_cache[key] = images
        return images
    
    @classmethod
    def get_route_image_set(cls, path: Path | None = None) -> \
        Dict[RouteDir, QPixmap]:

        base = cls._normalize_path(path)
        key = str(base.resolve())

        if key in cls._route_image_cache:
            return cls._route_image_cache[key]

        route_images = {
            RouteDir.UNKNOWN: cls._load(NPC_UN_PATH, base),
            RouteDir.RIGHT: cls._load(NPC_RI_PATH, base),
            RouteDir.TOP_RIGHT: cls._load(NPC_TR_PATH, base),
            RouteDir.TOP: cls._load(NPC_TO_PATH, base),
            RouteDir.TOP_LEFT: cls._load(NPC_TL_PATH, base),
            RouteDir.LEFT: cls._load(NPC_LE_PATH, base),
            RouteDir.DOWN_LEFT: cls._load(NPC_DL_PATH, base),
            RouteDir.DOWN: cls._load(NPC_DO_PATH, base),
            RouteDir.DOWN_RIGHT: cls._load(NPC_DR_PATH, base),
        }

        cls._route_image_cache[key] = route_images
        return route_images  
    
    @classmethod
    def get_empty_image(cls, path: Path=None):
        if cls._empty_image_cache:
            return cls._empty_image_cache
        
        if path:
            image = cls._load(path)

        else:
            image = cls._load(EMPTY_PATH, IMAGES_PATH)
        cls._empty_image_cache = image
        return image
    
    @classmethod
    def get_obstacle_for_npc_image(cls, path:Path=None):
        if cls._obstacle_for_npc_image_cache:
            return cls._obstacle_for_npc_image_cache
        
        if path:
            image = cls._load(path)
        else:
            image = cls._load(OBSTACLE_FOR_NPC_PATH, IMAGES_PATH)

        cls._obstacle_for_npc_image_cache = image
        return image
    
    @classmethod
    def get_goal_image(cls, path:Path=None):
        if cls._goal_image_cache:
            cls._goal_image_cache

        if path:
            image = cls._load(path)
        else:
            image = cls._load(GOAL_PATH, IMAGES_PATH)
        cls._goal_image_cache = image
        return image

    @classmethod
    def get_selected_npc_image(cls, path:Path=None):
        if cls._selected_npc_image_cache:
            return cls._selected_npc_image_cache
        
        if path:
            image = cls._load(path)
        else:
            image = cls._load(SELECTED_NPC_PATH, DEFAULT_NPC_IMAGE_PATH)

        cls._selected_npc_image_cache = image
        return image


