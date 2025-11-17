"""
黑名单仓储
"""
from typing import List, Optional
from datetime import datetime
from loguru import logger

from src.data.database import db_manager
from src.data.models import Blacklist


class BlacklistRepository:
    """黑名单仓储"""

    @staticmethod
    def get_all() -> List[Blacklist]:
        """
        获取所有黑名单

        Returns:
            黑名单列表
        """
        with db_manager.get_session() as session:
            return session.query(Blacklist).all()

    @staticmethod
    def add(app_name: str, reason: str = "") -> Blacklist:
        """
        添加黑名单

        Args:
            app_name: 应用名称
            reason: 原因

        Returns:
            黑名单对象
        """
        with db_manager.get_session() as session:
            # 检查是否已存在
            existing = session.query(Blacklist).filter(
                Blacklist.app_name == app_name
            ).first()

            if existing:
                logger.warning(f"黑名单已存在: {app_name}")
                return existing

            # 创建新黑名单
            blacklist = Blacklist(
                app_name=app_name,
                reason=reason
            )
            session.add(blacklist)
            logger.info(f"添加黑名单: {app_name}")

            return blacklist

    @staticmethod
    def remove(app_name: str) -> bool:
        """
        移除黑名单

        Args:
            app_name: 应用名称

        Returns:
            是否成功
        """
        with db_manager.get_session() as session:
            blacklist = session.query(Blacklist).filter(
                Blacklist.app_name == app_name
            ).first()

            if blacklist:
                session.delete(blacklist)
                logger.info(f"移除黑名单: {app_name}")
                return True
            else:
                logger.warning(f"黑名单不存在: {app_name}")
                return False

    @staticmethod
    def exists(app_name: str) -> bool:
        """
        检查黑名单是否存在

        Args:
            app_name: 应用名称

        Returns:
            是否存在
        """
        with db_manager.get_session() as session:
            return session.query(Blacklist).filter(
                Blacklist.app_name == app_name
            ).count() > 0

    @staticmethod
    def clear_all():
        """清空所有黑名单"""
        with db_manager.get_session() as session:
            deleted = session.query(Blacklist).delete()
            logger.info(f"清空黑名单: {deleted} 条")
