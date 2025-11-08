"""
数据模型定义（SQLAlchemy ORM）
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, 
    Boolean, Index, UniqueConstraint
)
from sqlalchemy.sql import func

from src.data.database import Base


class Entry(Base):
    """词条表"""
    __tablename__ = "entries"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 基本信息
    source_text = Column(Text, nullable=False, comment="原文")
    source_text_hash = Column(String(64), nullable=False, comment="原文MD5哈希(用于唯一索引)")
    translation = Column(Text, nullable=False, comment="翻译")
    source_lang = Column(String(10), default="en", comment="源语言")
    target_lang = Column(String(10), default="zh", comment="目标语言")
    entry_type = Column(String(20), default="sentence", comment="类型: word/phrase/sentence/paragraph")
    
    # 来源信息
    context = Column(Text, comment="上下文")
    source_app = Column(String(100), comment="来源应用")
    source_url = Column(String(500), comment="来源URL")
    
    # 学习数据
    familiarity = Column(Integer, default=0, comment="熟悉度 0-5")
    proficiency = Column(Integer, default=0, comment="熟练度 0-100")
    review_count = Column(Integer, default=0, comment="复习次数")
    correct_count = Column(Integer, default=0, comment="答对次数")
    last_review = Column(DateTime, comment="上次复习时间")
    next_review = Column(DateTime, comment="下次复习时间")
    ease_factor = Column(Float, default=2.5, comment="SM-2算法:难度系数")
    interval = Column(Integer, default=0, comment="SM-2算法:间隔天数")
    is_starred = Column(Boolean, default=False, comment="收藏标记")
    
    # 元数据
    tags = Column(Text, comment="标签JSON数组")
    notes = Column(Text, comment="用户笔记")
    translator_type = Column(String(50), comment="翻译器类型")
    translation_time = Column(Float, comment="翻译耗时(秒)")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    is_deleted = Column(Boolean, default=False, comment="软删除")
    
    # 索引和约束
    __table_args__ = (
        UniqueConstraint('source_text_hash', 'source_lang', 'target_lang', name='uq_entry'),
        Index('idx_created_at', 'created_at'),
        Index('idx_next_review', 'next_review'),
        Index('idx_familiarity', 'familiarity'),
        Index('idx_source_text_hash', 'source_text_hash'),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )
    
    def __repr__(self):
        return f"<Entry(id={self.id}, source_text={self.source_text[:30]}...)>"


class Tag(Base):
    """标签表"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment="标签名")
    color = Column(String(20), default="#3B82F6", comment="颜色")
    icon = Column(String(50), comment="图标")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    __table_args__ = (
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class DailyStat(Base):
    """每日统计表"""
    __tablename__ = "daily_stats"
    
    date = Column(DateTime, primary_key=True, comment="日期")
    new_words = Column(Integer, default=0, comment="新词数")
    review_count = Column(Integer, default=0, comment="复习次数")
    review_correct = Column(Integer, default=0, comment="复习正确数")
    study_duration = Column(Integer, default=0, comment="学习时长(分钟)")
    translation_count = Column(Integer, default=0, comment="翻译次数")
    ai_calls = Column(Integer, default=0, comment="AI调用次数")
    ai_tokens = Column(Integer, default=0, comment="AI消耗tokens")
    
    __table_args__ = (
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )
    
    def __repr__(self):
        return f"<DailyStat(date={self.date}, new_words={self.new_words})>"


class TranslationCache(Base):
    """翻译缓存表"""
    __tablename__ = "translation_cache"
    
    cache_key = Column(String(64), primary_key=True, comment="缓存键(MD5)")
    source_text = Column(Text, nullable=False, comment="原文")
    translation = Column(Text, nullable=False, comment="翻译")
    translator_type = Column(String(50), nullable=False, comment="翻译器类型")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    expires_at = Column(DateTime, comment="过期时间")
    hit_count = Column(Integer, default=0, comment="命中次数")
    
    __table_args__ = (
        Index('idx_expires_at', 'expires_at'),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )
    
    def __repr__(self):
        return f"<TranslationCache(cache_key={self.cache_key}, hit_count={self.hit_count})>"


class Setting(Base):
    """配置表"""
    __tablename__ = "settings"
    
    key = Column(String(100), primary_key=True, comment="配置键")
    value = Column(Text, nullable=False, comment="配置值")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )
    
    def __repr__(self):
        return f"<Setting(key={self.key})>"


class Blacklist(Base):
    """黑名单表"""
    __tablename__ = "blacklist"
    
    app_name = Column(String(100), primary_key=True, comment="应用名称")
    reason = Column(String(200), comment="原因")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    __table_args__ = (
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )
    
    def __repr__(self):
        return f"<Blacklist(app_name={self.app_name})>"

