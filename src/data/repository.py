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
        """获取文本查询次数"""
        with db_manager.get_session() as session:
            count = session.query(Entry).filter(
                Entry.source_text == text,
                Entry.is_deleted == False
            ).count()
            return count
    
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
            else:
                # 添加新缓存
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

