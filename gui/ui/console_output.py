from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton
)
from PySide6.QtCore import Slot

class ConsoleOutputWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QHBoxLayout(self)

        # 왼쪽: 출력 영역 + Clear 버튼
        left_layout = QVBoxLayout()
        self.output_box = QPlainTextEdit()
        self.output_box.setReadOnly(True)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.output_box.clear)

        left_layout.addWidget(self.output_box)
        left_layout.addWidget(self.clear_button)

        # 오른쪽: 스크롤 제어 버튼들
        right_layout = QVBoxLayout()
        self.scroll_top_btn = QPushButton("⬆ 맨 위로")
        self.scroll_bottom_btn = QPushButton("⬇ 맨 아래로")

        self.scroll_top_btn.clicked.connect(self.scroll_to_top)
        self.scroll_bottom_btn.clicked.connect(self.scroll_to_bottom)

        right_layout.addWidget(self.scroll_top_btn)
        right_layout.addWidget(self.scroll_bottom_btn)
        right_layout.addStretch()

        # 전체 배치
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self._auto_scroll_enabled = True
        self.output_box.verticalScrollBar().valueChanged.connect(self._check_user_scroll)

    def _check_user_scroll(self, value):
        scrollbar = self.output_box.verticalScrollBar()
        at_bottom = value == scrollbar.maximum()
        self._auto_scroll_enabled = at_bottom

    @Slot(str)
    def log(self, message):
        self.output_box.appendPlainText(message)
        if self._auto_scroll_enabled:
            self.scroll_to_bottom()

    def scroll_to_top(self):
        self._auto_scroll_enabled = False
        scrollbar = self.output_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.minimum())

    def scroll_to_bottom(self):
        self._auto_scroll_enabled = True
        scrollbar = self.output_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
