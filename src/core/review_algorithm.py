"""
SM-2复习算法实现
基于SuperMemo SM-2算法，用于计算间隔重复的最佳复习时间
"""
from datetime import datetime, timedelta
from typing import Tuple
from loguru import logger


class SM2Algorithm:
    """SM-2间隔重复算法"""

    # 质量评分定义
    QUALITY_PERFECT = 5      # 完美回忆
    QUALITY_CORRECT = 4      # 正确但有些犹豫
    QUALITY_RECALLED = 3     # 正确但很困难
    QUALITY_WRONG = 2        # 错误但感觉熟悉
    QUALITY_FORGOT = 1       # 完全忘记
    QUALITY_BLACKOUT = 0     # 完全不记得

    # 初始值
    INITIAL_EASE_FACTOR = 2.5
    INITIAL_INTERVAL = 1
    MIN_EASE_FACTOR = 1.3

    @classmethod
    def calculate_next_review(
        cls,
        quality: int,
        ease_factor: float,
        interval: int,
        review_count: int
    ) -> Tuple[float, int, datetime]:
        """
        计算下次复习时间

        Args:
            quality: 质量评分 (0-5)
            ease_factor: 难度系数 (>=1.3)
            interval: 当前间隔天数
            review_count: 复习次数

        Returns:
            (新难度系数, 新间隔天数, 下次复习时间)
        """
        try:
            # 1. 更新难度系数
            new_ease_factor = cls._update_ease_factor(ease_factor, quality)

            # 2. 计算新间隔
            if quality < 3:
                # 回答错误，重新开始
                new_interval = 1
            else:
                # 回答正确，计算间隔
                if review_count == 0:
                    # 第一次复习
                    new_interval = 1
                elif review_count == 1:
                    # 第二次复习
                    new_interval = 6
                else:
                    # 后续复习
                    new_interval = int(interval * new_ease_factor)

            # 3. 计算下次复习时间
            next_review_date = datetime.now() + timedelta(days=new_interval)

            logger.debug(
                f"SM-2计算: quality={quality}, "
                f"ease_factor={ease_factor:.2f}->{new_ease_factor:.2f}, "
                f"interval={interval}->{new_interval}, "
                f"next_review={next_review_date.strftime('%Y-%m-%d')}"
            )

            return new_ease_factor, new_interval, next_review_date

        except Exception as e:
            logger.error(f"SM-2计算失败: {e}")
            # 返回默认值
            return cls.INITIAL_EASE_FACTOR, cls.INITIAL_INTERVAL, datetime.now() + timedelta(days=1)

    @classmethod
    def _update_ease_factor(cls, current_ef: float, quality: int) -> float:
        """
        更新难度系数

        EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))

        Args:
            current_ef: 当前难度系数
            quality: 质量评分 (0-5)

        Returns:
            新难度系数
        """
        if quality < 0 or quality > 5:
            logger.warning(f"无效的质量评分: {quality}，使用默认值3")
            quality = 3

        # SM-2公式
        new_ef = current_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

        # 确保不低于最小值
        new_ef = max(new_ef, cls.MIN_EASE_FACTOR)

        return new_ef

    @classmethod
    def calculate_proficiency(
        cls,
        review_count: int,
        correct_count: int,
        ease_factor: float
    ) -> int:
        """
        计算熟练度 (0-100)

        综合考虑：
        - 复习次数
        - 正确率
        - 难度系数

        Args:
            review_count: 总复习次数
            correct_count: 正确次数
            ease_factor: 难度系数

        Returns:
            熟练度分数 (0-100)
        """
        try:
            if review_count == 0:
                return 0

            # 1. 正确率贡献 (40%)
            accuracy_rate = correct_count / review_count
            accuracy_score = accuracy_rate * 40

            # 2. 复习次数贡献 (30%)
            # 使用对数曲线，避免次数过多时增长过快
            import math
            review_score = min(math.log(review_count + 1, 1.5) * 10, 30)

            # 3. 难度系数贡献 (30%)
            # 难度系数越高，说明掌握越好
            # EF范围: 1.3 - 2.5+，映射到 0-30
            ef_normalized = (ease_factor - cls.MIN_EASE_FACTOR) / (cls.INITIAL_EASE_FACTOR - cls.MIN_EASE_FACTOR)
            ef_score = min(ef_normalized * 30, 30)

            # 总分
            proficiency = int(accuracy_score + review_score + ef_score)
            proficiency = max(0, min(proficiency, 100))

            logger.debug(
                f"熟练度计算: review={review_count}, correct={correct_count}, "
                f"ef={ease_factor:.2f} -> proficiency={proficiency}"
            )

            return proficiency

        except Exception as e:
            logger.error(f"熟练度计算失败: {e}")
            return 0

    @classmethod
    def quality_from_user_input(cls, is_correct: bool, difficulty: str = "normal") -> int:
        """
        将用户输入转换为质量评分

        Args:
            is_correct: 是否回答正确
            difficulty: 难度感受 ("easy", "normal", "hard")

        Returns:
            质量评分 (0-5)
        """
        if is_correct:
            if difficulty == "easy":
                return cls.QUALITY_PERFECT  # 5
            elif difficulty == "normal":
                return cls.QUALITY_CORRECT  # 4
            else:  # hard
                return cls.QUALITY_RECALLED  # 3
        else:
            if difficulty == "hard":
                return cls.QUALITY_FORGOT  # 1
            else:
                return cls.QUALITY_WRONG  # 2

    @classmethod
    def get_initial_values(cls) -> Tuple[float, int, datetime]:
        """
        获取初始值

        Returns:
            (初始难度系数, 初始间隔, 初始下次复习时间)
        """
        return (
            cls.INITIAL_EASE_FACTOR,
            cls.INITIAL_INTERVAL,
            datetime.now() + timedelta(days=cls.INITIAL_INTERVAL)
        )


class ReviewScheduler:
    """复习计划调度器"""

    @staticmethod
    def is_due_for_review(next_review_date: datetime) -> bool:
        """
        判断是否到了复习时间

        Args:
            next_review_date: 下次复习时间

        Returns:
            是否应该复习
        """
        if next_review_date is None:
            return True

        return datetime.now() >= next_review_date

    @staticmethod
    def get_urgency_level(next_review_date: datetime) -> str:
        """
        获取紧急程度

        Args:
            next_review_date: 下次复习时间

        Returns:
            紧急程度: "overdue"(逾期), "today"(今天), "soon"(即将), "future"(未来)
        """
        if next_review_date is None:
            return "overdue"

        now = datetime.now()
        days_until = (next_review_date - now).days

        if days_until < 0:
            return "overdue"
        elif days_until == 0:
            return "today"
        elif days_until <= 3:
            return "soon"
        else:
            return "future"

    @staticmethod
    def calculate_retention_rate(
        last_review_date: datetime,
        ease_factor: float,
        interval: int
    ) -> float:
        """
        估算当前记忆保持率

        使用遗忘曲线估算：R(t) = e^(-t/S)
        其中 S = interval * ease_factor (记忆强度)

        Args:
            last_review_date: 上次复习时间
            ease_factor: 难度系数
            interval: 间隔天数

        Returns:
            保持率 (0.0-1.0)
        """
        try:
            import math

            if last_review_date is None:
                return 0.0

            # 计算已过去的天数
            days_elapsed = (datetime.now() - last_review_date).days

            # 计算记忆强度
            memory_strength = interval * ease_factor

            # 遗忘曲线
            if memory_strength > 0:
                retention = math.exp(-days_elapsed / memory_strength)
            else:
                retention = 0.0

            return max(0.0, min(1.0, retention))

        except Exception as e:
            logger.error(f"保持率计算失败: {e}")
            return 0.5
