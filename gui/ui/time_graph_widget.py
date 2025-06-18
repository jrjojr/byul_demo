import pyqtgraph as pg
from PySide6.QtCore import QTimer
from pyqtgraph import (
    AxisItem, PlotWidget, PlotDataItem, TextItem, ScatterPlotItem, SignalProxy
)
from typing import List, Dict
from utils.elapsed_msec_series import ElapsedSeries

import pandas as pd

from grid.grid_canvas import GridCanvas


class IndexLabelAxisItem(AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [str(int(v)) for v in values]


class TimeGraphWidget(pg.PlotWidget):
    def __init__(self, parent=None, update_interval_ms=250,
                 step_interval_sec=1.0, sec_range=10):
        axis = IndexLabelAxisItem(orientation='bottom')
        super().__init__(parent, axisItems={'bottom': axis})

        self.setBackground('w')
        self.plot_item = self.getPlotItem()
        self.plot_item.showGrid(x=True, y=True)
        self.plot_item.setLabel('left', 'Elapsed time (ms)')
        self.plot_item.setLabel('bottom', 'Step Index')
        self.plot_item.setTitle("여러 시리즈 처리 시간 그래프")

        self.step_interval_sec = step_interval_sec
        self.sec_range = sec_range

        self.series_list: List[ElapsedSeries] = []
        self.series_items: Dict[str, Dict] = {}
        self._canvas_bound = False  # 바인딩 중복 방지

        self.hover_text = TextItem("", anchor=(0, 1), color='black')
        self.hover_text.setZValue(10)
        self.plot_item.addItem(self.hover_text, ignoreBounds=True)

        self.proxy = SignalProxy(
            self.scene().sigMouseMoved,
            rateLimit=60,
            slot=self._on_mouse_move
        )

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(update_interval_ms)

        self.plot_item.enableAutoRange(axis='y', enable=True)
        self.legend = self.plot_item.addLegend(offset=(30, 10))

    def pause(self):
        self.timer.stop()

    def resume(self):
        self.timer.start()

    def add_series(self, series: ElapsedSeries):
        if not series.name:
            raise ValueError("Series must have a unique name.")
        if series.name in self.series_items:
            return  # 이미 추가됨

        index = len(self.series_items)
        color = pg.intColor(index)
        pen = pg.mkPen(color=color, width=2)

        items = {
            "avg": PlotDataItem(pen=pg.mkPen(color=color, width=2)),
            "dots_min": ScatterPlotItem(pen=None, brush=pg.mkBrush(color), size=10),
            "dots_max": ScatterPlotItem(pen=None, brush=pg.mkBrush(color), size=10),
            "v_lines": [],
            "pen": pen  # 🎯 v_line과 통일할 선 정보 저장
        }        

        self.plot_item.addItem(items["avg"])
        self.plot_item.addItem(items["dots_min"])
        self.plot_item.addItem(items["dots_max"])
        self.legend.addItem(items["avg"], series.name)

        self.series_list.append(series)
        self.series_items[series.name] = items

    def reset(self):
        for items in self.series_items.values():
            for line in items["v_lines"]:
                self.plot_item.removeItem(line)
            self.plot_item.removeItem(items["avg"])
            self.plot_item.removeItem(items["dots_min"])
            self.plot_item.removeItem(items["dots_max"])

        self.series_items.clear()
        self.series_list.clear()
        self.hover_text.setText("")

    def _add_vertical_line(self, series_name: str, step: int, min_v: float, max_v: float):
        pen = self.series_items[series_name]["pen"]
        line = PlotDataItem([step, step], [min_v, max_v], pen=pen)
        self.plot_item.addItem(line)
        return line

    def update_graph(self):
        for items in self.series_items.values():
            for line in items["v_lines"]:
                self.plot_item.removeItem(line)
            items["v_lines"].clear()

        overall_first = float("inf")
        overall_last = 0

        for series in self.series_list:
            df = series.get_combined_data()
            if df.empty:
                continue

            df["sec"] = ((df["timestamp"])).astype(int)

            last_sec = df["sec"].max()
            first_sec = max(0, last_sec - self.sec_range)
            df = df[df["sec"] >= first_sec]

            overall_first = min(overall_first, first_sec)
            overall_last = max(overall_last, last_sec)

            secs, avgs, min_points, max_points = [], [], [], []

            for sec, group in df.groupby("sec"):
                min_v = group["elapsed_ms"].min()
                max_v = group["elapsed_ms"].max()
                avg_v = group["elapsed_ms"].mean()

                line = self._add_vertical_line(
                    series.name, sec, min_v, max_v)
                
                self.series_items[series.name]["v_lines"].append(line)

                secs.append(sec)
                avgs.append(avg_v)
                min_points.append({'pos': (sec, min_v)})
                max_points.append({'pos': (sec, max_v)})                

            self.series_items[series.name]["avg"].setData(secs, avgs)
            self.series_items[series.name]["dots_min"].setData(spots=min_points)
            self.series_items[series.name]["dots_max"].setData(spots=max_points)

        if overall_first < overall_last:
            self.plot_item.setXRange(overall_first, overall_last, padding=0)


    def _on_mouse_move(self, evt):
        pos = evt[0]
        vb = self.plot_item.vb
        if not self.plot_item.sceneBoundingRect().contains(pos):
            self.hover_text.setText("")
            return

        mouse_point = vb.mapSceneToView(pos)
        x = int(round(mouse_point.x()))
        y = mouse_point.y()
        self.hover_text.setPos(mouse_point.x(), mouse_point.y())
        self.hover_text.setText(f"Step {x}\n{y:.3f} ms")

    def bind_canvas(self, grid_canvas:GridCanvas):
        """GridCanvas에서 draw_cells, move_center 이벤트를 바인딩하고 시리즈 등록"""
        if self._canvas_bound:
            return
        self._canvas_bound = True

        series_draw = ElapsedSeries("draw_cells")
        series_move = ElapsedSeries("move_center")
        series_to_cells = ElapsedSeries("to_cells")
        
        # update_buffer_cells_elapsed
        series_update_buffer_cells = ElapsedSeries("update_buffer_cells")

        grid_canvas.draw_cells_elapsed.connect(series_draw.add_elapsed)
        grid_canvas.grid_map.move_center_elapsed.connect(series_move.add_elapsed)
        grid_canvas.grid_map.to_cells_elapsed.connect(series_to_cells.add_elapsed)
        grid_canvas.grid_map.update_buffer_cells_elapsed.connect(series_update_buffer_cells.add_elapsed)

        self.add_series(series_draw)
        self.add_series(series_move)
        self.add_series(series_to_cells)
        self.add_series(series_update_buffer_cells)
