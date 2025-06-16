import pandas as pd
import time

import os
import time
from pathlib import Path
import pandas as pd
from PySide6.QtCore import QThread, Signal, Slot, QObject, QTimer
from datetime import datetime

import os
import time
from pathlib import Path
import pandas as pd
from datetime import datetime
from PySide6.QtCore import QThread, Signal

from utils.log_to_panel import g_logger

class ElapsedSeries(QObject):
    def __init__(self, name: str,
                 autosaving: bool = False,
                 save_folder: str = "autosave",
                 file_format: str = "csv",
                 check_interval_sec: float = 2.0,
                 max_rows: int = 1000):
        super().__init__()

        self.name = name
        self.data = pd.DataFrame(
            columns=["timestamp", "label", "elapsed_ms"])
        self.start_time = None  # 최초 add_elapsed 시점

        self._pending_rows = []  # 누적 버퍼
        self.max_rows = max_rows

        self.autosaver = None
        if autosaving:
            self.autosaver = AutoSaveThread(
                series=self,
                folder=save_folder,
                file_format=file_format,
                check_interval_sec=check_interval_sec,
                max_rows=max_rows
            )
            self.autosaver.start()

            self.autosaver.successed.connect(self.log_successed)
            self.autosaver.failed.connect(self.log_failed)

    def __del__(self):
        # 객체 소멸 직전에 강제 저장
        if self.autosaver:
            try:
                self.autosaver.flush()
                self.autosaver.quit()
                self.autosaver.wait()
            except Exception:
                pass  # 예외 무시 (종료 시 안전성 우선)

    def log_successed(self, string:str):
        g_logger.log_debug(f'성공했다 저장하기 {string}')

    def log_failed(self, string:str):
        g_logger.log_debug(f'실패했다 왜 안되지 {string}')

    def stop_autosave(self):
        if self.autosaver:
            self.autosaver.stop()

    # @Slot(float)
    # def add_elapsed(self, elapsed_ms: float):
    #     now = float(time.time())
    #     if self.start_time is None:
    #         self.start_time = now
    #     self.data.loc[len(self.data)] = [now, self.name, elapsed_ms]

    @Slot(float)
    def add_elapsed(self, elapsed_ms: float):
        now = float(time.time())
        if self.start_time is None:
            self.start_time = now

        self._pending_rows.append([now, self.name, elapsed_ms])
        if len(self._pending_rows) >= self.max_rows:
            self.flush_pending_rows()


    def flush_pending_rows(self):
        if not self._pending_rows:
            return

        df_pending = pd.DataFrame(
            self._pending_rows,
            columns=["timestamp", "label", "elapsed_ms"]
        )
        if self.data.empty:
            self.data = df_pending
        else:
            self.data = pd.concat([self.data, df_pending], ignore_index=True)

        self._pending_rows.clear()


    def get_combined_data(self) -> pd.DataFrame:
        if not self._pending_rows:
            return self.data

        df_pending = pd.DataFrame(
            self._pending_rows,
            columns=["timestamp", "label", "elapsed_ms"]
        )

        if self.data.empty:
            return df_pending

        return pd.concat([self.data, df_pending], ignore_index=True)


    def clear(self):
        self.data = self.data.iloc[0:0]
        self.start_time = None

    def get_range_by_time(
            self, start_sec: float, end_sec: float) -> pd.DataFrame:
        """
        최초 저장시간(self.start_time) 기준 offset(sec)으로 범위 추출
        """
        if self.start_time is None:
            return pd.DataFrame(columns=self.data.columns)
        start_time = self.start_time + start_sec
        end_time = self.start_time + end_sec
        return self.data[(self.data["timestamp"] >= start_time) &
                         (self.data["timestamp"] <= end_time)]

    def get_range_by_index(
            self, start_index: int, end_index: int) -> pd.DataFrame:
        return self.data.iloc[start_index:end_index + 1]

    def get_avg_by_time(self, start_sec: float, end_sec: float) -> float:
        df = self.get_range_by_time(start_sec, end_sec)
        return df["elapsed_ms"].mean() if not df.empty else None

    def get_avg_by_index(self, start_index: int, end_index: int) -> float:
        df = self.get_range_by_index(start_index, end_index)
        return df["elapsed_ms"].mean() if not df.empty else None

    def save_to_csv(self, filepath: str):
        self.data.to_csv(filepath, index=False)

    def load_from_csv(self, filepath: str):
        self.data = pd.read_csv(filepath)
        self._recalculate_start_time()

    def save_to_json(self, filepath: str):
        self.data.to_json(filepath, orient="records", indent=4)

    def load_from_json(self, filepath: str):
        self.data = pd.read_json(filepath)
        self._recalculate_start_time()

    def _recalculate_start_time(self):
        if not self.data.empty:
            self.start_time = self.data["timestamp"].min()
        else:
            self.start_time = None

    def save_to_csv_range(self, filepath: str, 
                        start_sec: float = None, end_sec: float = None,
                        start_index: int = None, end_index: int = None):
        df = self._get_filtered_range(
            start_sec, end_sec, start_index, end_index)
        
        df.to_csv(filepath, index=False)

    def save_to_json_range(self, filepath: str, 
                        start_sec: float = None, end_sec: float = None,
                        start_index: int = None, end_index: int = None):
        df = self._get_filtered_range(
            start_sec, end_sec, start_index, end_index)
        
        df.to_json(filepath, orient="records", indent=4)

    def _get_filtered_range(self, start_sec=None, end_sec=None,
                        start_index=None, end_index=None) -> pd.DataFrame:
        df = self.data

        # 시간 기준 필터
        if start_sec is not None and end_sec is not None and \
            self.start_time is not None:

            start_t = self.start_time + start_sec
            end_t = self.start_time + end_sec
            df = df[
                (df["timestamp"] >= start_t) & (df["timestamp"] <= end_t)]

        # 인덱스 기준 필터 (iloc)
        if start_index is not None and end_index is not None:
            df = df.iloc[start_index:end_index + 1]

        return df

    # --- 시간 기준 저장 ---
    def save_to_csv_by_time(self, 
                        filepath: str, start_sec: float, end_sec: float):
        
        df = self.get_range_by_time(start_sec, end_sec)
        df.to_csv(filepath, index=False)

    def save_to_json_by_time(self, 
                        filepath: str, start_sec: float, end_sec: float):
    
        df = self.get_range_by_time(start_sec, end_sec)
        df.to_json(filepath, orient="records", indent=4)


    # --- 인덱스 기준 저장 ---
    def save_to_csv_by_index(self, 
                            filepath: str, start_index: int, end_index: int):
        
        df = self.get_range_by_index(start_index, end_index)
        df.to_csv(filepath, index=False)

    def save_to_json_by_index(self, 
            filepath: str, start_index: int, end_index: int):
        
        df = self.get_range_by_index(start_index, end_index)
        df.to_json(filepath, orient="records", indent=4)


class AutoSaveThread(QThread):
    successed = Signal(str, int)  # (filepath, row count)
    failed = Signal(str, str)     # (filepath, error message)

    def __init__(self, series, 
                 folder="autosave",
                 file_format="csv", 
                 check_interval_sec=2.0,
                 max_rows: int = 1000):
        super().__init__()

        assert file_format in ("csv", "json"), \
            "file_format must be 'csv' or 'json'"

        self.series = series
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)

        self.file_format = file_format
        self.check_interval_sec = check_interval_sec
        self.max_rows = max_rows

        self._running = True
        self._last_saved_index = -1  # 저장된 마지막 인덱스

    def stop(self):
        """종료 전 flush"""
        self._running = False
        self.flush()
        self.wait()

    def _format_filename(self, start_t: float, end_t: float, 
                         label: str = "") -> Path:
        
        label_part = label or "unknown"
        start_unix = int(start_t)
        end_unix = int(end_t)
        
        filename = \
f"autosave_{label_part}_{start_unix}_{end_unix}.{self.file_format}"
        
        subdir = self.folder / label_part
        subdir.mkdir(parents=True, exist_ok=True)
        
        return subdir / filename


    def _save_dataframe(self, df: pd.DataFrame, filepath: Path):
        try:
            if self.file_format == "csv":
                df.to_csv(filepath, index=False)
            else:
                df.to_json(filepath, orient="records", indent=4)

            self.successed.emit(str(filepath), len(df))
        except Exception as e:
            self.failed.emit(str(filepath), str(e))

    def _flush_range(self, start_index: int, end_index: int):
        df = self.series.data
        if df.empty or end_index < start_index:
            return

        df_new = df.iloc[start_index:end_index + 1]
        if df_new.empty:
            return

        label = str(df_new.iloc[-1].get("label", "unknown"))
        start_ts = df_new.iloc[0]["timestamp"]
        end_ts = df_new.iloc[-1]["timestamp"]

        filepath = self._format_filename(start_ts, end_ts, label)
        self._save_dataframe(df_new, filepath)

        # 마지막 저장 인덱스만 갱신
        self._last_saved_index = end_index

    def flush_if_exceeds_rows(self):
        df = self.series.data
        if df.empty:
            return

        start_index = self._last_saved_index + 1
        end_index = len(df) - 1
        if end_index < start_index:
            return

        row_count = end_index - start_index + 1
        if row_count >= self.max_rows:
            self._flush_range(start_index, end_index)

    def flush(self):
        """현재까지 누적된 데이터 모두 저장"""
        df = self.series.data
        if df.empty:
            return

        start_index = self._last_saved_index + 1
        end_index = len(df) - 1
        self._flush_range(start_index, end_index)

    # def run(self):
    #     while self._running:
    #         time.sleep(self.check_interval_sec)
    #         self.flush_if_exceeds_rows()

    def run(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.flush_if_exceeds_rows)
        self.timer.start(self.check_interval_sec * 1000)  # ms 단위

        self.exec_()  # Qt 이벤트 루프 시작 (이게 핵심!)