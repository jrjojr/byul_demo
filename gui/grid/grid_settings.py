from PySide6.QtWidgets import QWidget, QFormLayout, QSpinBox, QLabel

class GridSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QFormLayout(self)

        # 중심 좌표
        self.field_center_x = QSpinBox()
        self.field_center_y = QSpinBox()
        # self.field_center_x.setReadOnly(True)
        # self.field_center_y.setReadOnly(True)

        # 셀 크기
        self.field_cell_size = QSpinBox()
        self.field_cell_size.setRange(10, 200)

        # 현재 그리드 크기 (읽기 전용)
        self.label_grid_size = QLabel()

        # 블록 크기 (읽기 전용)
        self.label_block_size = QLabel()

        # 폼 추가
        self.layout.addRow("Center X", self.field_center_x)
        self.layout.addRow("Center Y", self.field_center_y)
        self.layout.addRow("Cell Size", self.field_cell_size)
        self.layout.addRow("Grid Size", self.label_grid_size)
        self.layout.addRow("Block Size", self.label_block_size)

        # 연결은 외부에서
        # 글자 하나 처도 바뀐다
        self.field_cell_size.valueChanged.connect(self._on_cell_size_changed)

        # 엔터 치거나 포커스를 이동 시킬때
        # self.field_cell_size.editingFinished.connect(
        #     self._on_cell_size_changed)

        self._canvas = None

    def bind_canvas(self, canvas):
        self._canvas = canvas
    #     self.refresh()

    def refresh(self):
        if not self._canvas:
            return
        self.field_center_x.setValue(self._canvas.grig_map.center.x)
        self.field_center_y.setValue(self._canvas.grig_map.center.y)
        self.field_cell_size.setValue(self._canvas.cell_size)
        self.label_grid_size.setText(
f"{self._canvas.grig_map.grid_width} x {self._canvas.grig_map.grid_height}")
        
        self.label_block_size.setText(
            str(self._canvas.block_manager.block_size))

    def _on_cell_size_changed(self, val):
        if self._canvas:
            self._canvas.set_cell_size(val)
            self._canvas.grid_map.change_grid_from_window(
                self._canvas.width(), self._canvas.height(), val)
