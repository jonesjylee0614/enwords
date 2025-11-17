"""
学习时长追踪器
"""
import time
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

from src.data.repository import StatsRepository


class ActivityTracker:
    """学习活动追踪器"""

    def __init__(self):
        self.stats_repo = StatsRepository()
        self.session_start_time: Optional[float] = None
        self.last_activity_time: Optional[float] = None
        self.total_active_seconds = 0
        self.inactivity_threshold = 300  # 5分钟无活动视为休息

    def start_session(self):
        """开始学习会话"""
        self.session_start_time = time.time()
        self.last_activity_time = time.time()
        self.total_active_seconds = 0
        logger.info("学习会话开始")

    def record_activity(self):
        """记录一次活动（翻译、查词等）"""
        current_time = time.time()

        if self.last_activity_time is None:
            # 首次活动
            self.start_session()
            return

        # 计算距离上次活动的时间
        time_since_last = current_time - self.last_activity_time

        if time_since_last <= self.inactivity_threshold:
            # 连续活动，累计时长
            self.total_active_seconds += time_since_last
        else:
            # 超过阈值，视为中断，只记录最后一次操作
            logger.debug(f"检测到{time_since_last:.0f}秒的不活动期")

        self.last_activity_time = current_time

    def end_session(self):
        """结束学习会话并保存统计"""
        if self.session_start_time is None:
            return

        # 计算总时长(分钟)
        duration_minutes = int(self.total_active_seconds / 60)

        if duration_minutes > 0:
            # 更新统计
            try:
                self.stats_repo.update_today_stats(
                    study_duration=duration_minutes
                )
                logger.info(f"学习会话结束，总时长: {duration_minutes}分钟")
            except Exception as e:
                logger.error(f"保存学习时长失败: {e}")

        # 重置
        self.session_start_time = None
        self.last_activity_time = None
        self.total_active_seconds = 0

    def get_current_duration(self) -> int:
        """获取当前会话时长(分钟)"""
        if self.session_start_time is None:
            return 0
        return int(self.total_active_seconds / 60)


# 全局单例
_activity_tracker = None


def get_activity_tracker() -> ActivityTracker:
    """获取活动追踪器单例"""
    global _activity_tracker
    if _activity_tracker is None:
        _activity_tracker = ActivityTracker()
    return _activity_tracker
