"""
数据仓储层（Repository Pattern）
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import desc, asc, or_, and_
from loguru import logger
import hashlib

from src.data.database import db_manager
from src.data.models import Entry, Tag, DailyStat, TranslationCache
from src.data.tag_repository import TagRepository


class EntryRepository:
    """词条仓储"""
    
    @staticmethod
    def _compute_hash(text: str) -> str:
        """计算文本的MD5哈希"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def save(self, entry: Entry) -> Entry:
        """保存词条"""
        with db_manager.get_session() as session:
            # 计算哈希值
            if not entry.source_text_hash:
                entry.source_text_hash = self._compute_hash(entry.source_text)
            
            # 检查是否已存在
            existing = session.query(Entry).filter(
                Entry.source_text_hash == entry.source_text_hash,
                Entry.source_lang == entry.source_lang,
                Entry.target_lang == entry.target_lang,
                Entry.is_deleted == False
            ).first()
            
            if existing:
                # 更新现有记录
                existing.translation = entry.translation
                existing.updated_at = datetime.now()
                logger.debug(f"更新词条: {entry.source_text[:30]}...")
                return existing
            else:
                # 添加新记录
                session.add(entry)
                logger.debug(f"新增词条: {entry.source_text[:30]}...")
                return entry
    
    def get_by_id(self, entry_id: int) -> Optional[Entry]:
        """根据ID获取词条"""
        with db_manager.get_session() as session:
            return session.query(Entry).filter(
                Entry.id == entry_id,
                Entry.is_deleted == False
            ).first()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Entry]:
        """获取所有词条"""
        with db_manager.get_session() as session:
            return session.query(Entry).filter(
                Entry.is_deleted == False
            ).order_by(
                desc(Entry.created_at)
            ).limit(limit).offset(offset).all()
    
    def search(self, keyword: str, limit: int = 50) -> List[Entry]:
        """搜索词条"""
        with db_manager.get_session() as session:
            return session.query(Entry).filter(
                and_(
                    or_(
                        Entry.source_text.like(f"%{keyword}%"),
                        Entry.translation.like(f"%{keyword}%")
                    ),
                    Entry.is_deleted == False
                )
            ).order_by(
                desc(Entry.created_at)
            ).limit(limit).all()
    
    def get_query_count(self, text: str) -> int:
        """
        获取文本查询次数

        Args:
            text: 文本内容

        Returns:
            查询次数（从缓存hit_count获取）
        """
        try:
            # 生成缓存键
            import hashlib
            # 使用与TranslationService相同的方式生成key
            # 默认假设是英文->中文翻译
            key_str = f"{text}:auto:zh"
            cache_key = hashlib.md5(key_str.encode()).hexdigest()

            # 查询缓存
            with db_manager.get_session() as session:
                cache = session.query(TranslationCache).filter(
                    TranslationCache.cache_key == cache_key
                ).first()

                if cache:
                    return cache.hit_count
                else:
                    # 如果缓存不存在，返回0
                    return 0

        except Exception as e:
            logger.error(f"获取查询次数失败: {e}")
            return 0
    
    def get_review_list(self, limit: int = 50) -> List[Entry]:
        """获取待复习列表"""
        with db_manager.get_session() as session:
            now = datetime.now()
            return session.query(Entry).filter(
                Entry.next_review <= now,
                Entry.is_deleted == False
            ).order_by(
                asc(Entry.next_review)
            ).limit(limit).all()
    
    def delete(self, entry_id: int):
        """删除词条（软删除）"""
        with db_manager.get_session() as session:
            entry = session.query(Entry).filter(Entry.id == entry_id).first()
            if entry:
                entry.is_deleted = True
                entry.updated_at = datetime.now()
                logger.debug(f"删除词条: {entry.source_text[:30]}...")
    
    def get_total_count(self) -> int:
        """获取总词条数"""
        with db_manager.get_session() as session:
            return session.query(Entry).filter(
                Entry.is_deleted == False
            ).count()
    
    def get_entries_by_date(self, date: datetime.date) -> List[Entry]:
        """获取指定日期的词条"""
        with db_manager.get_session() as session:
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())
            return session.query(Entry).filter(
                and_(
                    Entry.created_at >= start,
                    Entry.created_at <= end,
                    Entry.is_deleted == False
                )
            ).all()
    
    def get_entries_to_review(self) -> List[Entry]:
        """获取待复习词条"""
        with db_manager.get_session() as session:
            now = datetime.now()
            return session.query(Entry).filter(
                and_(
                    Entry.next_review <= now,
                    Entry.is_deleted == False
                )
            ).all()
    
    def get_mastered_entries(self, proficiency_threshold: int = 80) -> List[Entry]:
        """获取已掌握词条"""
        with db_manager.get_session() as session:
            return session.query(Entry).filter(
                and_(
                    Entry.proficiency >= proficiency_threshold,
                    Entry.is_deleted == False
                )
            ).all()

    def update_review_data(
        self,
        entry_id: int,
        ease_factor: float,
        interval: int,
        next_review: datetime,
        proficiency: int,
        is_correct: bool
    ) -> bool:
        """
        更新复习数据

        Args:
            entry_id: 词条ID
            ease_factor: 新的难度系数
            interval: 新的间隔天数
            next_review: 下次复习时间
            proficiency: 新的熟练度
            is_correct: 本次是否正确

        Returns:
            是否成功
        """
        try:
            with db_manager.get_session() as session:
                entry = session.query(Entry).filter(Entry.id == entry_id).first()

                if not entry:
                    logger.warning(f"词条不存在: {entry_id}")
                    return False

                # 更新复习相关字段
                entry.ease_factor = ease_factor
                entry.interval = interval
                entry.next_review = next_review
                entry.proficiency = proficiency
                entry.last_review = datetime.now()
                entry.review_count = (entry.review_count or 0) + 1

                if is_correct:
                    entry.correct_count = (entry.correct_count or 0) + 1

                entry.updated_at = datetime.now()

                logger.debug(f"更新复习数据: {entry.source_text[:30]}... -> proficiency={proficiency}")
                return True

        except Exception as e:
            logger.error(f"更新复习数据失败: {e}")
            return False

    def get_due_reviews_by_urgency(self) -> dict:
        """
        按紧急程度获取待复习词条

        Returns:
            字典，包含 overdue, today, soon 三个列表
        """
        try:
            with db_manager.get_session() as session:
                now = datetime.now()
                today_end = datetime.combine(now.date(), datetime.max.time())
                soon_end = now + timedelta(days=3)

                # 逾期
                overdue = session.query(Entry).filter(
                    and_(
                        Entry.next_review < now,
                        Entry.is_deleted == False
                    )
                ).order_by(asc(Entry.next_review)).all()

                # 今天
                today = session.query(Entry).filter(
                    and_(
                        Entry.next_review >= now,
                        Entry.next_review <= today_end,
                        Entry.is_deleted == False
                    )
                ).order_by(asc(Entry.next_review)).all()

                # 即将到期（3天内）
                soon = session.query(Entry).filter(
                    and_(
                        Entry.next_review > today_end,
                        Entry.next_review <= soon_end,
                        Entry.is_deleted == False
                    )
                ).order_by(asc(Entry.next_review)).all()

                return {
                    'overdue': overdue,
                    'today': today,
                    'soon': soon
                }

        except Exception as e:
            logger.error(f"获取待复习词条失败: {e}")
            return {'overdue': [], 'today': [], 'soon': []}

    def get_review_statistics(self) -> dict:
        """
        获取复习统计信息

        Returns:
            统计信息字典
        """
        try:
            with db_manager.get_session() as session:
                now = datetime.now()

                # 总词条数
                total_count = session.query(Entry).filter(
                    Entry.is_deleted == False
                ).count()

                # 待复习数
                due_count = session.query(Entry).filter(
                    and_(
                        Entry.next_review <= now,
                        Entry.is_deleted == False
                    )
                ).count()

                # 已掌握数（熟练度>=80）
                mastered_count = session.query(Entry).filter(
                    and_(
                        Entry.proficiency >= 80,
                        Entry.is_deleted == False
                    )
                ).count()

                # 学习中（熟练度40-79）
                learning_count = session.query(Entry).filter(
                    and_(
                        Entry.proficiency >= 40,
                        Entry.proficiency < 80,
                        Entry.is_deleted == False
                    )
                ).count()

                # 新词（熟练度<40）
                new_count = session.query(Entry).filter(
                    and_(
                        Entry.proficiency < 40,
                        Entry.is_deleted == False
                    )
                ).count()

                # 今日已复习
                today_start = datetime.combine(now.date(), datetime.min.time())
                reviewed_today = session.query(Entry).filter(
                    and_(
                        Entry.last_review >= today_start,
                        Entry.is_deleted == False
                    )
                ).count()

                return {
                    'total_count': total_count,
                    'due_count': due_count,
                    'mastered_count': mastered_count,
                    'learning_count': learning_count,
                    'new_count': new_count,
                    'reviewed_today': reviewed_today
                }

        except Exception as e:
            logger.error(f"获取复习统计失败: {e}")
            return {}


class CacheRepository:
    """缓存仓储"""
    
    def get(self, cache_key: str) -> Optional[TranslationCache]:
        """获取缓存"""
        with db_manager.get_session() as session:
            cache = session.query(TranslationCache).filter(
                TranslationCache.cache_key == cache_key
            ).first()
            
            if cache:
                # 检查是否过期
                if cache.expires_at and cache.expires_at < datetime.now():
                    session.delete(cache)
                    return None
                
                # 增加命中次数
                cache.hit_count += 1
                return cache
            
            return None
    
    def set(self, cache: TranslationCache):
        """设置缓存"""
        with db_manager.get_session() as session:
            existing = session.query(TranslationCache).filter(
                TranslationCache.cache_key == cache.cache_key
            ).first()

            if existing:
                # 更新现有缓存
                existing.translation = cache.translation
                existing.created_at = datetime.now()
                existing.expires_at = cache.expires_at
                # 增加命中次数（因为这次查询触发了缓存更新）
                existing.hit_count += 1
            else:
                # 添加新缓存，首次查询计为1次
                if cache.hit_count == 0:
                    cache.hit_count = 1
                session.add(cache)
    
    def clean_expired(self):
        """清理过期缓存"""
        with db_manager.get_session() as session:
            now = datetime.now()
            deleted = session.query(TranslationCache).filter(
                TranslationCache.expires_at < now
            ).delete()
            logger.info(f"清理过期缓存: {deleted} 条")


class StatsRepository:
    """统计仓储"""
    
    def update_today_stats(self, **kwargs):
        """更新今日统计"""
        with db_manager.get_session() as session:
            today = datetime.now().date()
            stats = session.query(DailyStat).filter(
                DailyStat.date == today
            ).first()
            
            if not stats:
                stats = DailyStat(date=today)
                session.add(stats)
            
            # 更新统计数据
            for key, value in kwargs.items():
                if hasattr(stats, key):
                    current = getattr(stats, key) or 0
                    setattr(stats, key, current + value)
    
    def get_stats(self, days: int = 30) -> List[DailyStat]:
        """获取统计数据"""
        with db_manager.get_session() as session:
            start_date = datetime.now().date() - timedelta(days=days)
            return session.query(DailyStat).filter(
                DailyStat.date >= start_date
            ).order_by(asc(DailyStat.date)).all()
    
    def get_stats_by_date_range(self, start_date: Optional[datetime.date], 
                                  end_date: datetime.date) -> List[DailyStat]:
        """获取日期范围内的统计数据"""
        with db_manager.get_session() as session:
            query = session.query(DailyStat)
            
            if start_date:
                query = query.filter(DailyStat.date >= start_date)
            
            query = query.filter(DailyStat.date <= end_date)
            
            return query.order_by(asc(DailyStat.date)).all()

