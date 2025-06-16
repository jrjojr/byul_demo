from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox
)

class GotoDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("중심 좌표 이동")

        layout = QVBoxLayout()
        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        layout.addWidget(QLabel("X 좌표:"))
        layout.addWidget(self.x_input)
        layout.addWidget(QLabel("Y 좌표:"))
        layout.addWidget(self.y_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_coords(self):
        return int(self.x_input.text()), int(self.y_input.text())
