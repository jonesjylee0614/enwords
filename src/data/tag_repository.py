"""
标签仓储
"""
from typing import List, Optional
from sqlalchemy import func
from loguru import logger

from src.data.database import db_manager
from src.data.models import Tag


class TagRepository:
    """标签仓储"""
    
    def save(self, tag: Tag) -> Tag:
        """保存标签"""
        with db_manager.get_session() as session:
            # 检查是否已存在
            existing = session.query(Tag).filter(
                Tag.name == tag.name
            ).first()
            
            if existing:
                # 更新
                existing.color = tag.color
                existing.icon = tag.icon
                logger.debug(f"更新标签: {tag.name}")
                return existing
            else:
                # 新增
                session.add(tag)
                logger.debug(f"新增标签: {tag.name}")
                return tag
    
    def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """根据ID获取标签"""
        with db_manager.get_session() as session:
            return session.query(Tag).filter(Tag.id == tag_id).first()
    
    def get_by_name(self, name: str) -> Optional[Tag]:
        """根据名称获取标签"""
        with db_manager.get_session() as session:
            return session.query(Tag).filter(Tag.name == name).first()
    
    def get_all(self) -> List[Tag]:
        """获取所有标签"""
        with db_manager.get_session() as session:
            return session.query(Tag).order_by(Tag.name).all()
    
    def delete(self, tag_id: int):
        """删除标签"""
        with db_manager.get_session() as session:
            tag = session.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                session.delete(tag)
                logger.debug(f"删除标签: {tag.name}")
    
    def get_or_create(self, name: str, color: str = "#3B82F6") -> Tag:
        """获取或创建标签"""
        tag = self.get_by_name(name)
        if tag:
            return tag
        
        new_tag = Tag(name=name, color=color)
        return self.save(new_tag)

