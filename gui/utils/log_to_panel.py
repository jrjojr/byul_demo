from PySide6.QtCore import (
    QObject, Signal, QTimer, Slot, QMetaObject, Qt, Q_ARG
    )

class LogToPanel(QObject):
    log_emitted = Signal(str)

    def __init__(self, debug_mode=True):
        super().__init__()
        self.debug_mode = debug_mode

    def log_debug(self, message):
        if not self.debug_mode:
            return
        QTimer.singleShot(0, lambda: self._emit_log(f'debug: {message}'))

    def log_debug_threadsafe(self, message):
        if not self.debug_mode:
            return
        QMetaObject.invokeMethod(
            self,
            "_emit_log",
            Qt.QueuedConnection,
            Q_ARG(str, f"debug: {message}")
        )

    def log_always(self, message):
        QTimer.singleShot(0, lambda: self._emit_log(message))

    def set_debug_mode(self, enabled: bool):
        self.debug_mode = enabled

    def is_debug_mode_enabled(self):
        return self.debug_mode

    @Slot(str)
    def _emit_log(self, message):
        self.log_emitted.emit(message)


import threading
from datetime import datetime

class ThreadSafeLogger:
    def __init__(self, debug_mode=True):
        self.debug_mode = debug_mode
        self._lock = threading.Lock()
        self._log_callback = None  # 외부 출력 시스템 연결용 (옵션)

    def log_debug(self, message):
        if self.debug_mode:
            self._log(f'debug: {message}')

    def log_debug_threadsafe(self, message):
        if self.debug_mode:
            self._log(f'debug: {message}')

    def log_always(self, message):
        self._log(message)

    def _log(self, message):
        with self._lock:
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_text = f"[{timestamp}] {message}"

            if self._log_callback:
                self._log_callback(log_text)
            else:
                print(log_text)

    def set_debug_mode(self, enabled: bool):
        self.debug_mode = enabled

    def is_debug_mode_enabled(self):
        return self.debug_mode

    def set_log_callback(self, callback):
        '''로그 출력을 외부 UI 등으로 전달하고 싶을 때'''
        self._log_callback = callback


# 글로벌 싱글 인스턴스
# g_logger = ThreadSafeLogger()


# 글로벌 싱글 인스턴스
g_logger = LogToPanel()