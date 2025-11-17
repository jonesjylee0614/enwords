"""
复习服务
整合SM-2算法和数据仓储，提供复习业务逻辑
"""
from typing import List, Optional, Dict
from datetime import datetime
from loguru import logger

from src.data.models import Entry
from src.data.repository import EntryRepository, StatsRepository
from src.core.review_algorithm import SM2Algorithm, ReviewScheduler


class ReviewService:
    """复习服务"""

    def __init__(self):
        self.entry_repo = EntryRepository()
        self.stats_repo = StatsRepository()
        self.sm2 = SM2Algorithm()
        self.scheduler = ReviewScheduler()

    def get_due_reviews(self, limit: Optional[int] = None) -> List[Entry]:
        """
        获取待复习词条

        Args:
            limit: 限制数量（None则返回全部）

        Returns:
            待复习词条列表
        """
        try:
            if limit:
                return self.entry_repo.get_review_list(limit=limit)
            else:
                return self.entry_repo.get_entries_to_review()
        except Exception as e:
            logger.error(f"获取待复习词条失败: {e}")
            return []

    def get_reviews_by_urgency(self) -> Dict[str, List[Entry]]:
        """
        按紧急程度获取待复习词条

        Returns:
            字典，包含 overdue, today, soon 三个列表
        """
        try:
            return self.entry_repo.get_due_reviews_by_urgency()
        except Exception as e:
            logger.error(f"获取分类复习列表失败: {e}")
            return {'overdue': [], 'today': [], 'soon': []}

    def submit_review(
        self,
        entry_id: int,
        is_correct: bool,
        difficulty: str = "normal"
    ) -> bool:
        """
        提交复习结果

        Args:
            entry_id: 词条ID
            is_correct: 是否回答正确
            difficulty: 难度感受 ("easy", "normal", "hard")

        Returns:
            是否成功
        """
        try:
            # 1. 获取词条
            entry = self.entry_repo.get_by_id(entry_id)
            if not entry:
                logger.warning(f"词条不存在: {entry_id}")
                return False

            # 2. 转换为质量评分
            quality = self.sm2.quality_from_user_input(is_correct, difficulty)

            # 3. 获取当前值（如果是第一次复习，使用初始值）
            if entry.review_count == 0 or entry.ease_factor is None:
                ease_factor, interval, _ = self.sm2.get_initial_values()
            else:
                ease_factor = entry.ease_factor
                interval = entry.interval or 1

            review_count = entry.review_count or 0

            # 4. 计算下次复习时间
            new_ease_factor, new_interval, next_review = self.sm2.calculate_next_review(
                quality=quality,
                ease_factor=ease_factor,
                interval=interval,
                review_count=review_count
            )

            # 5. 计算新的熟练度
            new_correct_count = (entry.correct_count or 0) + (1 if is_correct else 0)
            new_review_count = review_count + 1
            new_proficiency = self.sm2.calculate_proficiency(
                review_count=new_review_count,
                correct_count=new_correct_count,
                ease_factor=new_ease_factor
            )

            # 6. 更新数据库
            success = self.entry_repo.update_review_data(
                entry_id=entry_id,
                ease_factor=new_ease_factor,
                interval=new_interval,
                next_review=next_review,
                proficiency=new_proficiency,
                is_correct=is_correct
            )

            if success:
                # 7. 更新统计
                self.stats_repo.update_today_stats(review_count=1)
                logger.info(
                    f"复习完成: {entry.source_text[:30]}... "
                    f"({'正确' if is_correct else '错误'}) "
                    f"-> proficiency={new_proficiency}, "
                    f"next_review={next_review.strftime('%Y-%m-%d')}"
                )

            return success

        except Exception as e:
            logger.error(f"提交复习结果失败: {e}")
            return False

    def get_review_statistics(self) -> Dict:
        """
        获取复习统计信息

        Returns:
            统计信息字典
        """
        try:
            return self.entry_repo.get_review_statistics()
        except Exception as e:
            logger.error(f"获取复习统计失败: {e}")
            return {}

    def estimate_study_time(self, entry_count: int) -> int:
        """
        估算学习时间（分钟）

        Args:
            entry_count: 词条数量

        Returns:
            预计所需时间（分钟）
        """
        # 假设每个词条平均需要30秒
        minutes = (entry_count * 30) // 60
        return max(1, minutes)

    def get_retention_rate(self, entry: Entry) -> float:
        """
        获取词条的记忆保持率

        Args:
            entry: 词条

        Returns:
            保持率 (0.0-1.0)
        """
        try:
            if not entry.last_review:
                return 0.0

            return self.scheduler.calculate_retention_rate(
                last_review_date=entry.last_review,
                ease_factor=entry.ease_factor or self.sm2.INITIAL_EASE_FACTOR,
                interval=entry.interval or self.sm2.INITIAL_INTERVAL
            )
        except Exception as e:
            logger.error(f"计算保持率失败: {e}")
            return 0.0

    def get_urgency_level(self, entry: Entry) -> str:
        """
        获取词条的紧急程度

        Args:
            entry: 词条

        Returns:
            紧急程度: "overdue"(逾期), "today"(今天), "soon"(即将), "future"(未来)
        """
        try:
            return self.scheduler.get_urgency_level(entry.next_review)
        except Exception as e:
            logger.error(f"获取紧急程度失败: {e}")
            return "future"

    def reset_review_progress(self, entry_id: int) -> bool:
        """
        重置复习进度（重新学习）

        Args:
            entry_id: 词条ID

        Returns:
            是否成功
        """
        try:
            ease_factor, interval, next_review = self.sm2.get_initial_values()

            success = self.entry_repo.update_review_data(
                entry_id=entry_id,
                ease_factor=ease_factor,
                interval=interval,
                next_review=next_review,
                proficiency=0,
                is_correct=False  # 不增加正确次数
            )

            if success:
                logger.info(f"重置复习进度: entry_id={entry_id}")

            return success

        except Exception as e:
            logger.error(f"重置复习进度失败: {e}")
            return False

    def batch_review(
        self,
        review_results: List[Dict]
    ) -> Dict[str, int]:
        """
        批量提交复习结果

        Args:
            review_results: 复习结果列表，每项包含 {entry_id, is_correct, difficulty}

        Returns:
            统计信息: {success_count, failed_count}
        """
        success_count = 0
        failed_count = 0

        for result in review_results:
            entry_id = result.get('entry_id')
            is_correct = result.get('is_correct', False)
            difficulty = result.get('difficulty', 'normal')

            if self.submit_review(entry_id, is_correct, difficulty):
                success_count += 1
            else:
                failed_count += 1

        logger.info(f"批量复习完成: 成功={success_count}, 失败={failed_count}")

        return {
            'success_count': success_count,
            'failed_count': failed_count
        }

    def get_mastered_entries(self, threshold: int = 80) -> List[Entry]:
        """
        获取已掌握的词条

        Args:
            threshold: 熟练度阈值

        Returns:
            已掌握词条列表
        """
        try:
            return self.entry_repo.get_mastered_entries(threshold)
        except Exception as e:
            logger.error(f"获取已掌握词条失败: {e}")
            return []

    def get_weak_entries(self, threshold: int = 40) -> List[Entry]:
        """
        获取薄弱词条（熟练度低）

        Args:
            threshold: 熟练度阈值

        Returns:
            薄弱词条列表
        """
        try:
            with self.entry_repo.db_manager.get_session() as session:
                from src.data.models import Entry
                from sqlalchemy import and_

                return session.query(Entry).filter(
                    and_(
                        Entry.proficiency < threshold,
                        Entry.is_deleted == False
                    )
                ).order_by(Entry.proficiency).all()
        except Exception as e:
            logger.error(f"获取薄弱词条失败: {e}")
            return []
