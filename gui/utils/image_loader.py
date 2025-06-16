from PySide6.QtGui import QPixmap
from pathlib import Path

def load_image(path: Path):
    pixmap = QPixmap(str(path))

    # 셀 사이즈에 맞게 스케일 하기
    # pixmap = QPixmap(str(path)).scaled(cell_size, cell_size)

    if pixmap.isNull():
        raise ValueError(f"이미지 로딩 실패: {path}")
    return pixmap
