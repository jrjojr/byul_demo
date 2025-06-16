"""
MouseInputHandler
=================
PySide6 위젯에 마우스 입력 이벤트를 통합 관리하는 핸들러.
클릭, 더블클릭, 드래그 시작/이동/종료, 휠 이벤트까지 신호로 연결 가능.

📌 사용 예시:
    handler = MouseInputHandler(widget)
    handler.clicked.connect(on_click)
    handler.drag_moved.connect(on_drag_move)
    handler.mouse_moved.connect(on_hover)

✅ 지원 이벤트:
    - clicked (짧은 클릭)
    - double_clicked (더블 클릭)
    - drag_started / drag_moved / drag_ended (드래그 일련 이벤트)
    - mouse_moved (항상 발생, 이동 추적용)
    - wheel_scrolled (휠 스크롤)
"""

from PySide6.QtCore import QObject, Signal, QEvent, QTimer
from PySide6.QtGui import QMouseEvent, QWheelEvent, Qt
from PySide6.QtWidgets import QWidget

class MouseInputHandler(QObject):
    clicked = Signal(QMouseEvent)
    double_clicked = Signal(QMouseEvent)
    drag_started = Signal(QMouseEvent)
    drag_moved = Signal(QMouseEvent)
    drag_ended = Signal(QMouseEvent)
    mouse_moved = Signal(QMouseEvent)
    wheel_scrolled = Signal(QWheelEvent)

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.widget = widget
        self._pressed = False
        self._press_pos = None
        self._drag_started = False

        self._click_flag = False
        self._pending_click_event: QMouseEvent | None = None

        # self._click_timer = QTimer()
        # self._click_timer.setSingleShot(True)
        # self._click_timer.timeout.connect(self._emit_delayed_click)

        widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            return self._handle_mouse_press(event)
        elif event.type() == QEvent.MouseButtonRelease:
            return self._handle_mouse_release(event)
        elif event.type() == QEvent.MouseMove:
            return self._handle_mouse_move(event)
        elif event.type() == QEvent.MouseButtonDblClick:
            self._click_flag = False
            # self._click_timer.stop()
            self._pending_click_event = None
            self.double_clicked.emit(event)
            return True
        elif event.type() == QEvent.Wheel:
            self.wheel_scrolled.emit(event)
        return False

    def _handle_mouse_press(self, event: QMouseEvent):
        self._pressed = True
        self._drag_started = False
        self._press_pos = event.pos()
        self._click_flag = True
        return False

    def _handle_mouse_release(self, event: QMouseEvent):
        if not self._pressed:
            return False

        self._pressed = False

        if self._drag_started:
            self.drag_ended.emit(event)
            return False

        if self._click_flag and (
            event.pos() - self._press_pos).manhattanLength() < 5:

            self._pending_click_event = event
            # self._click_timer.start(100)
            # QTimer.singleShot(100, self._emit_delayed_click)
            self._emit_delayed_click()

        return False

    def _emit_delayed_click(self):
        if self._click_flag and self._pending_click_event:
            self.clicked.emit(self._pending_click_event)
        self._click_flag = False
        self._pending_click_event = None

    def _handle_mouse_move(self, event: QMouseEvent):
        self.mouse_moved.emit(event)

        if self._pressed and not self._drag_started:
            if (event.pos() - self._press_pos).manhattanLength() > 5:
                self._drag_started = True
                self.drag_started.emit(event)

        if self._drag_started:
            self.drag_moved.emit(event)
        return False
