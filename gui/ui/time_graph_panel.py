from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QFileDialog, QMessageBox, QSpinBox, QLabel
)
from ui.time_graph_widget import TimeGraphWidget  # 경로 조정 필요

from grid.grid_canvas import GridCanvas

class TimeGraphPanel(QWidget):
    """
    루프 시간 그래프 패널:
    - pyqtgraph 기반 실시간 그래프
    - 그래프 리셋 / 저장 / 불러오기 버튼 포함
    - 저장 범위 선택 가능
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.graph_widget = TimeGraphWidget()

        # 버튼들
        self.reset_button = QPushButton("리셋")
        self.save_button = QPushButton("저장")
        self.load_button = QPushButton("불러오기")

        # 범위 선택용 spinbox
        self.start_spin = QSpinBox()
        self.end_spin = QSpinBox()
        self.start_spin.setPrefix("Start: ")
        self.end_spin.setPrefix("End: ")
        self.start_spin.setMinimum(0)
        self.end_spin.setMinimum(0)

        # 이벤트 연결
        self.reset_button.clicked.connect(self.graph_widget.reset)
        self.save_button.clicked.connect(self._on_save)
        self.load_button.clicked.connect(self._on_load)

        # 버튼 및 범위 레이아웃
        range_layout = QHBoxLayout()
        range_layout.addWidget(self.start_spin)
        range_layout.addWidget(self.end_spin)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)

        # 전체 레이아웃
        layout = QVBoxLayout()
        layout.addWidget(self.graph_widget)
        layout.addLayout(range_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.start_spin.focusInEvent = self._make_focus_event(self.start_spin)
        self.end_spin.focusInEvent = self._make_focus_event(self.end_spin)


    def _on_save(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "그래프 저장", "move_center_log.csv", 
            "CSV Files (*.csv);;JSON Files (*.json)"
        )
        if file_path:
            try:
                start = self.start_spin.value()
                end = self.end_spin.value()
                if file_path.endswith(".csv"):
                    self.graph_widget.save_to_csv_from_index(file_path, start, end)
                else:
                    self.graph_widget.save_to_json_from_index(file_path, start, end)
            except Exception as e:
                QMessageBox.critical(self, "저장 실패", str(e))

    def _make_focus_event(self, spinbox):
        def _on_focus(event):
            max_index = len(self.graph_widget.samples)
            spinbox.setMaximum(max_index)
            QSpinBox.focusInEvent(spinbox, event)
        return _on_focus

    def _on_load(self):
        file_path, _ = QFileDialog.getOpenFileName(...)
        if file_path:
            try:
                if file_path.endswith(".csv"):
                    self.graph_widget.load_from_csv(file_path)
                else:
                    self.graph_widget.load_from_json(file_path)

                # 🔁 변경된 구조에서는 step → 인덱스 수
                total = len(self.graph_widget.samples)
                self.end_spin.setValue(total)
                self.start_spin.setMaximum(total)
                self.end_spin.setMaximum(total)

            except Exception as e:
                QMessageBox.critical(self, "불러오기 실패", str(e))

    def bind_canvas(self, grid_canvas:GridCanvas):
        self.graph_widget.bind_canvas(grid_canvas)
