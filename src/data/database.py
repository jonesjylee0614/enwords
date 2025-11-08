"""
MySQL 数据库管理
"""
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.pool import QueuePool
from loguru import logger

from src.utils.config_loader import config


class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass


class DatabaseManager:
    """数据库管理器"""
    
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化数据库连接"""
        if self._engine is None:
            self._initialize_engine()
    
    def _initialize_engine(self):
        """初始化数据库引擎"""
        from urllib.parse import quote_plus
        
        db_config = config.database
        
        # URL编码用户名和密码（防止特殊字符引起问题）
        encoded_user = quote_plus(db_config.user)
        encoded_password = quote_plus(db_config.password)
        
        # 构建连接URL
        connection_url = (
            f"mysql+pymysql://{encoded_user}:{encoded_password}"
            f"@{db_config.host}:{db_config.port}/{db_config.database}"
            f"?charset={db_config.charset}"
        )
        
        # 创建引擎
        self._engine = create_engine(
            connection_url,
            poolclass=QueuePool,
            pool_size=db_config.pool_size,
            max_overflow=db_config.max_overflow,
            pool_recycle=db_config.pool_recycle,
            pool_pre_ping=True,  # 连接前检测
            echo=False,  # 不输出SQL语句
        )
        
        # 监听连接事件
        @event.listens_for(self._engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """连接建立时的回调"""
            logger.debug("数据库连接建立")
        
        @event.listens_for(self._engine, "close")
        def receive_close(dbapi_conn, connection_record):
            """连接关闭时的回调"""
            logger.debug("数据库连接关闭")
        
        # 创建会话工厂
        self._session_factory = sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )
        
        logger.info(f"数据库引擎初始化完成: {db_config.host}:{db_config.port}/{db_config.database}")
    
    @property
    def engine(self):
        """获取数据库引擎"""
        return self._engine
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        获取数据库会话（上下文管理器）
        
        使用示例:
            with db_manager.get_session() as session:
                result = session.query(Entry).all()
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库事务回滚: {e}")
            raise
        finally:
            session.close()
    
    def create_all_tables(self):
        """创建所有表"""
        try:
            Base.metadata.create_all(self._engine)
            logger.info("数据库表创建完成")
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise
    
    def drop_all_tables(self):
        """删除所有表（谨慎使用）"""
        try:
            Base.metadata.drop_all(self._engine)
            logger.warning("数据库表已删除")
        except Exception as e:
            logger.error(f"删除数据库表失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self._engine:
            self._engine.dispose()
            logger.info("数据库连接已关闭")


# 全局数据库管理器实例
db_manager = DatabaseManager()

