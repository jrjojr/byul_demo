'''사용법
from path_consumer import PathConsumer

self.real_consumer = PathConsumer(self.real_coord_list, maxlen=200, chunk_size=8)

def on_real_path_found(self):
    try:
        p: c_path = self.real_queue.get_nowait()
    except Empty:
        return

    coord_list = p.to_list()
    p.close()
    self.real_consumer.consume(coord_list)

'''

from PySide6.QtCore import QObject, QTimer


class PathConsumer(QObject):
    def __init__(self, target_list: list, maxlen: int = 100, chunk_size: int = 10, parent=None):
        super().__init__(parent)
        self._target = target_list          # 경로 좌표를 저장할 외부 리스트
        self._maxlen = maxlen               # 리스트 최대 길이
        self._chunk_size = chunk_size       # 한 번에 처리할 좌표 수
        self._pending = []                  # 소비 대기 중인 좌표 리스트
        self._index = 0                     # 현재 처리 위치
        self._active = False                # 소비 루프 활성화 여부

    def consume(self, coord_list: list):
        if not coord_list:
            return

        if self._active:
            # 소비 도중 새 coord_list가 들어오면 덮어씀 (원하면 append로 바꿔도 됨)
            self._pending = coord_list
            self._index = 0
        else:
            self._pending = coord_list
            self._index = 0
            self._active = True
            self._consume_chunk()

    def _consume_chunk(self):
        if self._index >= len(self._pending):
            self._pending.clear()
            self._active = False
            return

        end = min(self._index + self._chunk_size, len(self._pending))
        new_coords = self._pending[self._index:end]
        self._index = end

        self._target.extend(new_coords)

        # 최대 길이 초과 시 앞에서 제거
        if len(self._target) > self._maxlen:
            excess = len(self._target) - self._maxlen
            del self._target[:excess]

        QTimer.singleShot(0, self._consume_chunk)

    def is_active(self):
        return self._active

    def cancel(self):
        self._pending.clear()
        self._active = False
        self._index = 0

    def set_maxlen(self, maxlen: int):
        self._maxlen = maxlen

    def set_chunk_size(self, chunk_size: int):
        self._chunk_size = chunk_size
