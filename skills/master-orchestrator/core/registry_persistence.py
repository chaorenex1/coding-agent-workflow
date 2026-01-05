#!/usr/bin/env python3
"""
RegistryPersistence - 注册表持久化

管理 ~/.memex/orchestrator/registry/ 目录，提供：
- 保存资源扫描结果
- 检测配置文件变更
- 快速加载缓存
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class RegistryPersistence:
    """
    注册表持久化 - 管理 ~/.memex/orchestrator/registry/ 目录

    功能：
    - 保存资源扫描结果
    - 检测配置文件变更（通过文件哈希）
    - 加速后续启动（避免重复扫描）
    - TTL过期机制

    使用示例：
        persistence = RegistryPersistence(registry_dir=Path("registry"))

        # 尝试加载缓存
        cached = persistence.load_cached_resources(scan_paths)
        if cached:
            return cached

        # 执行扫描
        resources = scan_all()

        # 保存缓存
        persistence.save_scan_result(resources, scan_paths, duration_ms)
    """

    def __init__(self, registry_dir: Path, ttl_seconds: int = 3600):
        """
        初始化注册表持久化

        Args:
            registry_dir: 注册表目录
            ttl_seconds: 缓存有效期（秒），默认1小时
        """
        self.registry_dir = Path(registry_dir).expanduser()
        self.ttl_seconds = ttl_seconds

        # 确保目录存在
        self.registry_dir.mkdir(parents=True, exist_ok=True)

        # 文件路径
        self.last_scan_file = self.registry_dir / "last_scan.json"
        self.snapshot_file = self.registry_dir / "resources_snapshot.json"

    def save_scan_result(
        self,
        resources: Dict[str, List[Any]],
        file_paths: List[str],
        scan_duration_ms: int
    ):
        """
        保存扫描结果

        Args:
            resources: 资源字典 {"skills": [...], "commands": [...]}
            file_paths: 扫描的文件路径列表
            scan_duration_ms: 扫描耗时（毫秒）
        """
        try:
            # 1. 计算文件哈希
            file_hashes = {}
            for path in file_paths:
                file_path = Path(path).expanduser()
                if file_path.exists():
                    file_hashes[str(file_path)] = self._compute_file_hash(file_path)

            # 2. 保存扫描元数据
            last_scan = {
                "timestamp": datetime.now().isoformat(),
                "skills_count": len(resources.get("skills", [])),
                "commands_count": len(resources.get("commands", [])),
                "agents_count": len(resources.get("agents", [])),
                "prompts_count": len(resources.get("prompts", [])),
                "scan_duration_ms": scan_duration_ms,
                "file_hashes": file_hashes,
                "ttl_seconds": self.ttl_seconds
            }

            with open(self.last_scan_file, 'w', encoding='utf-8') as f:
                json.dump(last_scan, f, indent=2, ensure_ascii=False)

            # 3. 保存资源快照（序列化资源对象）
            snapshot = {
                "created_at": datetime.now().isoformat(),
                "resources": self._serialize_resources(resources)
            }

            with open(self.snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)

            total_resources = sum(len(v) for v in resources.values())
            logger.info(
                f"注册表快照已保存: {len(file_paths)}个文件, "
                f"{total_resources}个资源"
            )

        except Exception as e:
            logger.warning(f"保存注册表快照失败: {e}")

    def load_cached_resources(
        self,
        current_file_paths: List[str]
    ) -> Optional[Dict[str, List[Any]]]:
        """
        加载缓存的资源（如果有效）

        Args:
            current_file_paths: 当前的扫描路径列表

        Returns:
            如果缓存有效，返回资源字典；否则返回 None
        """
        try:
            # 1. 检查快照文件是否存在
            if not self.last_scan_file.exists() or not self.snapshot_file.exists():
                logger.debug("注册表快照不存在")
                return None

            # 2. 加载上次扫描信息
            with open(self.last_scan_file, 'r', encoding='utf-8') as f:
                last_scan = json.load(f)

            # 3. 检查TTL
            last_scan_time = datetime.fromisoformat(last_scan["timestamp"])
            age_seconds = (datetime.now() - last_scan_time).total_seconds()

            if age_seconds > self.ttl_seconds:
                logger.debug(f"注册表快照已过期: {age_seconds:.0f}s > {self.ttl_seconds}s")
                return None

            # 4. 检查文件是否变更
            if self._files_changed(last_scan["file_hashes"], current_file_paths):
                logger.debug("检测到配置文件变更，快照失效")
                return None

            # 5. 加载快照
            with open(self.snapshot_file, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)

            total_resources = sum(len(v) for v in snapshot['resources'].values())
            logger.info(f"加载注册表快照: {total_resources}个资源")

            return snapshot["resources"]

        except Exception as e:
            logger.warning(f"加载注册表快照失败: {e}")
            return None

    def invalidate(self):
        """使缓存失效（删除快照文件）"""
        try:
            if self.last_scan_file.exists():
                self.last_scan_file.unlink()
            if self.snapshot_file.exists():
                self.snapshot_file.unlink()
            logger.info("注册表快照已清除")
        except Exception as e:
            logger.warning(f"清除注册表快照失败: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        获取注册表统计信息

        Returns:
            统计信息字典
        """
        try:
            if not self.last_scan_file.exists():
                return {"status": "no_cache"}

            with open(self.last_scan_file, 'r', encoding='utf-8') as f:
                last_scan = json.load(f)

            last_scan_time = datetime.fromisoformat(last_scan["timestamp"])
            age_seconds = (datetime.now() - last_scan_time).total_seconds()

            return {
                "status": "cached",
                "last_scan": last_scan["timestamp"],
                "age_seconds": int(age_seconds),
                "ttl_seconds": self.ttl_seconds,
                "is_valid": age_seconds <= self.ttl_seconds,
                "total_resources": sum([
                    last_scan.get("skills_count", 0),
                    last_scan.get("commands_count", 0),
                    last_scan.get("agents_count", 0),
                    last_scan.get("prompts_count", 0)
                ]),
                "scan_duration_ms": last_scan.get("scan_duration_ms", 0),
                "file_count": len(last_scan.get("file_hashes", {}))
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _compute_file_hash(self, file_path: Path) -> str:
        """
        计算文件MD5哈希

        Args:
            file_path: 文件路径

        Returns:
            MD5哈希字符串
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return f"md5:{hashlib.md5(content).hexdigest()}"
        except Exception as e:
            logger.warning(f"计算文件哈希失败 {file_path}: {e}")
            return "error"

    def _files_changed(
        self,
        cached_hashes: Dict[str, str],
        current_paths: List[str]
    ) -> bool:
        """
        检查文件是否变更

        Args:
            cached_hashes: 缓存的文件哈希
            current_paths: 当前的文件路径列表

        Returns:
            文件是否变更
        """
        # 转换为绝对路径集合
        current_path_set = {
            str(Path(p).expanduser().resolve())
            for p in current_paths
        }
        cached_path_set = {
            str(Path(p).expanduser().resolve())
            for p in cached_hashes.keys()
        }

        # 检查文件数量是否变化
        if current_path_set != cached_path_set:
            logger.debug(
                f"文件列表变更: 新增={current_path_set - cached_path_set}, "
                f"删除={cached_path_set - current_path_set}"
            )
            return True

        # 检查每个文件的哈希
        for path_str in current_path_set:
            file_path = Path(path_str)
            if not file_path.exists():
                continue

            # 获取缓存的哈希（需要处理路径格式差异）
            cached_hash = None
            for cached_path, hash_val in cached_hashes.items():
                if Path(cached_path).resolve() == file_path.resolve():
                    cached_hash = hash_val
                    break

            if cached_hash is None:
                logger.debug(f"新文件: {file_path}")
                return True  # 新文件

            current_hash = self._compute_file_hash(file_path)
            if current_hash != cached_hash:
                logger.debug(f"文件内容变更: {file_path}")
                return True  # 文件内容变更

        return False

    def _serialize_resources(self, resources: Dict[str, List[Any]]) -> Dict[str, List[Dict]]:
        """
        序列化资源对象为JSON可序列化的字典

        Args:
            resources: 资源字典

        Returns:
            序列化后的字典
        """
        from enum import Enum
        from pathlib import Path

        def make_serializable(obj):
            """将对象转换为JSON可序列化的形式"""
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, Enum):
                return obj.value  # 枚举转换为其值
            elif isinstance(obj, Path):
                return str(obj)  # Path转换为字符串
            elif hasattr(obj, '__dict__'):
                return make_serializable(vars(obj))
            else:
                return obj

        serialized = {}

        for resource_type, resource_list in resources.items():
            serialized[resource_type] = []

            for resource in resource_list:
                # 尝试多种序列化方法（优先级：专用方法 > 通用属性）
                try:
                    if isinstance(resource, dict):
                        # 已经是字典，确保内容可序列化
                        serialized[resource_type].append(make_serializable(resource))
                    elif hasattr(resource, 'to_dict'):
                        # 对象有 to_dict() 方法（优先使用）
                        serialized[resource_type].append(make_serializable(resource.to_dict()))
                    elif hasattr(resource, '_asdict'):
                        # namedtuple
                        serialized[resource_type].append(make_serializable(resource._asdict()))
                    elif hasattr(resource, '__dict__'):
                        # 对象有 __dict__（兜底方案）
                        serialized[resource_type].append(make_serializable(vars(resource)))
                    else:
                        # 其他情况，转为字符串
                        logger.warning(
                            f"无法序列化资源类型 {type(resource)}, "
                            f"将转为字符串表示"
                        )
                        serialized[resource_type].append({"_str": str(resource)})
                except Exception as e:
                    logger.warning(f"序列化资源失败 {type(resource)}: {e}")
                    serialized[resource_type].append({"_error": str(e), "_type": str(type(resource))})

        return serialized
