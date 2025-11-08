"""
统计图表窗口
"""
from datetime import datetime, timedelta
from typing import List, Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from loguru import logger

from src.data.repository import StatsRepository, EntryRepository


class ChartWidget(QWidget):
    """简单图表控件（柱状图/折线图）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data: List[tuple] = []  # [(label, value), ...]
        self.chart_type = "bar"  # bar / line
        self.title = ""
        self.setMinimumHeight(300)
        
    def set_data(self, data: List[tuple], title: str = "", chart_type: str = "bar"):
        """设置数据"""
        self.data = data
        self.title = title
        self.chart_type = chart_type
        self.update()
    
    def paintEvent(self, event):
        """绘制图表"""
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制背景
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        # 边距
        margin = 40
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin - 30  # 预留标题空间
        
        # 绘制标题
        if self.title:
            font = QFont("Microsoft YaHei", 12, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(0, 10, self.width(), 20, Qt.AlignmentFlag.AlignCenter, self.title)
        
        # 计算数值范围
        values = [v for _, v in self.data]
        if not values:
            return
        
        max_value = max(values) if values else 1
        min_value = min(values) if values else 0
        value_range = max_value - min_value if max_value != min_value else 1
        
        # 绘制坐标轴
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawLine(margin, margin + 30, margin, height + margin + 30)  # Y轴
        painter.drawLine(margin, height + margin + 30, width + margin, height + margin + 30)  # X轴
        
        # 数据点数量
        n = len(self.data)
        if n == 0:
            return
        
        bar_width = width // n * 0.6
        spacing = width / n
        
        # 绘制数据
        if self.chart_type == "bar":
            painter.setBrush(QColor(70, 130, 180, 180))
            for i, (label, value) in enumerate(self.data):
                bar_height = (value - min_value) / value_range * height if value_range > 0 else 0
                x = margin + i * spacing + spacing * 0.2
                y = margin + 30 + height - bar_height
                
                # 绘制柱子
                painter.drawRect(int(x), int(y), int(bar_width), int(bar_height))
                
                # 绘制标签
                font = QFont("Microsoft YaHei", 8)
                painter.setFont(font)
                painter.drawText(int(x), height + margin + 35, int(bar_width), 20, 
                               Qt.AlignmentFlag.AlignCenter, str(label))
                
                # 绘制数值
                painter.drawText(int(x), int(y) - 5, int(bar_width), 20, 
                               Qt.AlignmentFlag.AlignCenter, str(int(value)))
        
        elif self.chart_type == "line":
            painter.setPen(QPen(QColor(70, 130, 180), 3))
            points = []
            for i, (label, value) in enumerate(self.data):
                point_height = (value - min_value) / value_range * height if value_range > 0 else 0
                x = margin + i * spacing + spacing / 2
                y = margin + 30 + height - point_height
                points.append((int(x), int(y)))
                
                # 绘制点
                painter.setBrush(QColor(70, 130, 180))
                painter.drawEllipse(int(x) - 4, int(y) - 4, 8, 8)
                
                # 绘制标签
                font = QFont("Microsoft YaHei", 8)
                painter.setFont(font)
                painter.drawText(int(x) - 20, height + margin + 35, 40, 20, 
                               Qt.AlignmentFlag.AlignCenter, str(label))
            
            # 连接线
            for i in range(len(points) - 1):
                painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])


class StatisticsWindow(QWidget):
    """统计窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats_repo = StatsRepository()
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("学习统计")
        self.resize(900, 700)
        
        layout = QVBoxLayout(self)
        
        # 顶部控制栏
        control_layout = QHBoxLayout()
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["最近7天", "最近30天", "最近90天", "全部"])
        self.period_combo.currentTextChanged.connect(self._on_period_changed)
        control_layout.addWidget(QLabel("时间范围:"))
        control_layout.addWidget(self.period_combo)
        
        control_layout.addStretch()
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_data)
        control_layout.addWidget(refresh_btn)
        
        layout.addLayout(control_layout)
        
        # 概览卡片
        overview_group = QGroupBox("概览")
        overview_layout = QHBoxLayout(overview_group)
        
        self.total_words_label = QLabel("总词条: 0")
        self.today_new_label = QLabel("今日新增: 0")
        self.to_review_label = QLabel("待复习: 0")
        self.mastered_label = QLabel("已掌握: 0")
        
        overview_layout.addWidget(self.total_words_label)
        overview_layout.addWidget(self.today_new_label)
        overview_layout.addWidget(self.to_review_label)
        overview_layout.addWidget(self.mastered_label)
        overview_layout.addStretch()
        
        layout.addWidget(overview_group)
        
        # 图表区域
        chart_group = QGroupBox("趋势图表")
        chart_layout = QVBoxLayout(chart_group)
        
        # 每日新增词条图表
        self.daily_chart = ChartWidget()
        chart_layout.addWidget(self.daily_chart)
        
        # 复习正确率图表
        self.accuracy_chart = ChartWidget()
        chart_layout.addWidget(self.accuracy_chart)
        
        layout.addWidget(chart_group)
        
        # 详细数据表格
        table_group = QGroupBox("详细数据")
        table_layout = QVBoxLayout(table_group)
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(5)
        self.stats_table.setHorizontalHeaderLabels([
            "日期", "新增词条", "复习次数", "正确率", "学习时长(分钟)"
        ])
        table_layout.addWidget(self.stats_table)
        
        layout.addWidget(table_group)
        
        # 加载初始数据
        self.refresh_data()
    
    def _on_period_changed(self, period: str):
        """时间范围改变"""
        self.refresh_data()
    
    def _get_date_range(self) -> tuple:
        """获取日期范围"""
        period = self.period_combo.currentText()
        today = datetime.now().date()
        
        if period == "最近7天":
            start_date = today - timedelta(days=7)
        elif period == "最近30天":
            start_date = today - timedelta(days=30)
        elif period == "最近90天":
            start_date = today - timedelta(days=90)
        else:
            start_date = None
        
        return start_date, today
    
    def refresh_data(self):
        """刷新数据"""
        try:
            start_date, end_date = self._get_date_range()
            
            # 获取统计数据
            self._update_overview(start_date, end_date)
            self._update_charts(start_date, end_date)
            self._update_table(start_date, end_date)
            
            logger.info("统计数据已刷新")
            
        except Exception as e:
            logger.error(f"刷新统计数据失败: {e}")
    
    def _update_overview(self, start_date, end_date):
        """更新概览数据"""
        try:
            entry_repo = EntryRepository()
            
            # 总词条数
            total = entry_repo.get_total_count()
            self.total_words_label.setText(f"总词条: {total}")
            
            # 今日新增
            today_new = entry_repo.get_entries_by_date(datetime.now().date())
            self.today_new_label.setText(f"今日新增: {len(today_new)}")
            
            # 待复习（简化逻辑：创建超过1天未复习的）
            to_review = entry_repo.get_entries_to_review()
            self.to_review_label.setText(f"待复习: {len(to_review)}")
            
            # 已掌握（熟练度>=80）
            mastered = entry_repo.get_mastered_entries()
            self.mastered_label.setText(f"已掌握: {len(mastered)}")
            
        except Exception as e:
            logger.error(f"更新概览数据失败: {e}")
    
    def _update_charts(self, start_date, end_date):
        """更新图表"""
        try:
            # 获取每日统计
            stats = self.stats_repo.get_stats_by_date_range(start_date, end_date)
            
            if not stats:
                return
            
            # 每日新增词条
            daily_data = [(s.date.strftime("%m-%d"), s.new_words) for s in stats[-14:]]  # 最多显示14天
            self.daily_chart.set_data(daily_data, "每日新增词条", "bar")
            
            # 复习正确率
            accuracy_data = [
                (s.date.strftime("%m-%d"), 
                 s.review_correct / s.review_count * 100 if s.review_count > 0 else 0)
                for s in stats[-14:]
            ]
            self.accuracy_chart.set_data(accuracy_data, "复习正确率 (%)", "line")
            
        except Exception as e:
            logger.error(f"更新图表失败: {e}")
    
    def _update_table(self, start_date, end_date):
        """更新表格"""
        try:
            stats = self.stats_repo.get_stats_by_date_range(start_date, end_date)
            
            self.stats_table.setRowCount(len(stats))
            
            for i, stat in enumerate(stats):
                self.stats_table.setItem(i, 0, QTableWidgetItem(stat.date.strftime("%Y-%m-%d")))
                self.stats_table.setItem(i, 1, QTableWidgetItem(str(stat.new_words)))
                self.stats_table.setItem(i, 2, QTableWidgetItem(str(stat.review_count)))
                
                # 正确率
                accuracy = stat.review_correct / stat.review_count * 100 if stat.review_count > 0 else 0
                self.stats_table.setItem(i, 3, QTableWidgetItem(f"{accuracy:.1f}%"))
                
                self.stats_table.setItem(i, 4, QTableWidgetItem(str(stat.study_duration)))
            
            # 自动调整列宽
            self.stats_table.resizeColumnsToContents()
            
        except Exception as e:
            logger.error(f"更新表格失败: {e}")


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = StatisticsWindow()
    window.show()
    sys.exit(app.exec())

