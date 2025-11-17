"""
备份服务
支持数据库备份、恢复、定时备份等功能
"""
import subprocess
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from loguru import logger

from src.utils.config_loader import config


class BackupService:
    """备份服务"""

    def __init__(self):
        # 备份目录
        self.backup_dir = Path("data/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # 数据库配置
        self.db_config = config.database

    def create_backup(self, backup_name: Optional[str] = None) -> Optional[Path]:
        """
        创建数据库备份

        Args:
            backup_name: 备份名称（可选，默认使用时间戳）

        Returns:
            备份文件路径，失败返回None
        """
        try:
            # 生成备份文件名
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"translearn_backup_{timestamp}.sql"

            backup_path = self.backup_dir / backup_name

            # 构建mysqldump命令
            cmd = [
                "mysqldump",
                "-h", self.db_config.host,
                "-P", str(self.db_config.port),
                "-u", self.db_config.user,
                f"-p{self.db_config.password}",
                "--single-transaction",  # 保证数据一致性
                "--routines",  # 包含存储过程
                "--triggers",  # 包含触发器
                "--events",  # 包含事件
                self.db_config.database
            ]

            # 执行备份
            with open(backup_path, 'w', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=300  # 5分钟超时
                )

            if result.returncode == 0:
                # 备份成功
                size_mb = backup_path.stat().st_size / (1024 * 1024)
                logger.info(f"备份成功: {backup_path} ({size_mb:.2f} MB)")

                # 清理旧备份
                self._cleanup_old_backups()

                return backup_path
            else:
                # 备份失败
                error = result.stderr
                logger.error(f"备份失败: {error}")
                # 删除失败的备份文件
                if backup_path.exists():
                    backup_path.unlink()
                return None

        except FileNotFoundError:
            logger.error("mysqldump 未找到，请确保 MySQL 客户端已安装")
            return None
        except subprocess.TimeoutExpired:
            logger.error("备份超时（超过5分钟）")
            return None
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return None

    def restore_backup(self, backup_path: Path) -> bool:
        """
        从备份恢复数据库

        Args:
            backup_path: 备份文件路径

        Returns:
            是否成功
        """
        try:
            if not backup_path.exists():
                logger.error(f"备份文件不存在: {backup_path}")
                return False

            # 确认操作
            logger.warning(f"即将从备份恢复数据库，当前数据将被覆盖: {backup_path}")

            # 构建mysql命令
            cmd = [
                "mysql",
                "-h", self.db_config.host,
                "-P", str(self.db_config.port),
                "-u", self.db_config.user,
                f"-p{self.db_config.password}",
                self.db_config.database
            ]

            # 执行恢复
            with open(backup_path, 'r', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=300  # 5分钟超时
                )

            if result.returncode == 0:
                logger.info(f"恢复成功: {backup_path}")
                return True
            else:
                error = result.stderr
                logger.error(f"恢复失败: {error}")
                return False

        except FileNotFoundError:
            logger.error("mysql 未找到，请确保 MySQL 客户端已安装")
            return False
        except subprocess.TimeoutExpired:
            logger.error("恢复超时（超过5分钟）")
            return False
        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            return False

    def list_backups(self) -> List[dict]:
        """
        列出所有备份

        Returns:
            备份列表，每项包含名称、路径、大小、时间
        """
        backups = []

        try:
            for backup_file in sorted(self.backup_dir.glob("*.sql"), reverse=True):
                stat = backup_file.stat()
                backups.append({
                    'name': backup_file.name,
                    'path': backup_file,
                    'size': stat.st_size,
                    'size_mb': stat.st_size / (1024 * 1024),
                    'created_at': datetime.fromtimestamp(stat.st_mtime)
                })

        except Exception as e:
            logger.error(f"列出备份失败: {e}")

        return backups

    def delete_backup(self, backup_name: str) -> bool:
        """
        删除指定备份

        Args:
            backup_name: 备份文件名

        Returns:
            是否成功
        """
        try:
            backup_path = self.backup_dir / backup_name

            if not backup_path.exists():
                logger.warning(f"备份文件不存在: {backup_name}")
                return False

            backup_path.unlink()
            logger.info(f"删除备份: {backup_name}")
            return True

        except Exception as e:
            logger.error(f"删除备份失败: {e}")
            return False

    def _cleanup_old_backups(self, keep_count: int = 10):
        """
        清理旧备份，只保留最近N个

        Args:
            keep_count: 保留数量
        """
        try:
            backups = self.list_backups()

            if len(backups) <= keep_count:
                return

            # 删除多余的备份
            for backup in backups[keep_count:]:
                self.delete_backup(backup['name'])
                logger.info(f"清理旧备份: {backup['name']}")

        except Exception as e:
            logger.error(f"清理旧备份失败: {e}")

    def should_auto_backup(self) -> bool:
        """
        判断是否应该自动备份

        Returns:
            是否应该备份
        """
        try:
            if not config.data.backup_enabled:
                return False

            backups = self.list_backups()

            if not backups:
                # 没有备份，应该立即备份
                return True

            # 检查最后备份时间
            last_backup = backups[0]
            last_backup_time = last_backup['created_at']
            interval_days = config.data.backup_interval_days

            next_backup_time = last_backup_time + timedelta(days=interval_days)

            return datetime.now() >= next_backup_time

        except Exception as e:
            logger.error(f"检查自动备份条件失败: {e}")
            return False

    def auto_backup(self):
        """执行自动备份（如果需要）"""
        try:
            if self.should_auto_backup():
                logger.info("执行自动备份...")
                backup_path = self.create_backup()

                if backup_path:
                    logger.info(f"自动备份完成: {backup_path}")
                else:
                    logger.error("自动备份失败")

        except Exception as e:
            logger.error(f"自动备份失败: {e}")

    def export_all_data(self, output_dir: Path) -> bool:
        """
        导出所有数据（包括数据库备份和配置文件）

        Args:
            output_dir: 输出目录

        Returns:
            是否成功
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 1. 数据库备份
            db_backup_name = f"database_{timestamp}.sql"
            db_backup = self.create_backup(db_backup_name)

            if db_backup:
                # 复制到输出目录
                shutil.copy(db_backup, output_dir / db_backup_name)

            # 2. 复制配置文件
            config_file = Path("data/config.toml")
            if config_file.exists():
                shutil.copy(config_file, output_dir / "config.toml")

            # 3. 复制词典文件
            dict_dir = Path("data/dict")
            if dict_dir.exists():
                shutil.copytree(dict_dir, output_dir / "dict", dirs_exist_ok=True)

            logger.info(f"导出所有数据到: {output_dir}")
            return True

        except Exception as e:
            logger.error(f"导出数据失败: {e}")
            return False

    def import_all_data(self, import_dir: Path) -> bool:
        """
        导入所有数据

        Args:
            import_dir: 导入目录

        Returns:
            是否成功
        """
        try:
            import_dir = Path(import_dir)

            if not import_dir.exists():
                logger.error(f"导入目录不存在: {import_dir}")
                return False

            # 1. 恢复数据库
            db_backups = list(import_dir.glob("database_*.sql"))
            if db_backups:
                # 使用最新的备份
                latest_backup = sorted(db_backups, reverse=True)[0]
                if not self.restore_backup(latest_backup):
                    logger.error("数据库恢复失败")
                    return False

            # 2. 恢复配置文件（谨慎操作）
            config_file = import_dir / "config.toml"
            if config_file.exists():
                logger.warning("发现配置文件备份，请手动检查并决定是否恢复")

            # 3. 恢复词典文件
            dict_dir = import_dir / "dict"
            if dict_dir.exists():
                target_dict_dir = Path("data/dict")
                shutil.copytree(dict_dir, target_dict_dir, dirs_exist_ok=True)

            logger.info(f"导入数据成功: {import_dir}")
            return True

        except Exception as e:
            logger.error(f"导入数据失败: {e}")
            return False
