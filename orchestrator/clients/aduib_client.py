#!/usr/bin/env python3
"""
AduibClient - aduib-ai 托管服务 REST 客户端

提供可选的远程缓存和历史功能
使用 aiohttp 进行异步 HTTP 请求，但对外提供同步接口
"""

import os
import json
import hashlib
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import aiohttp
except ImportError:
    aiohttp = None


@dataclass
class CacheQuery:
    """缓存查询请求"""
    request_hash: str
    mode: str
    backend: str


@dataclass
class TaskData:
    """任务数据"""
    request: str
    request_hash: str
    mode: str
    backend: str
    success: bool
    output: str
    error: Optional[str] = None
    run_id: Optional[str] = None
    duration_seconds: Optional[float] = None
    created_at: Optional[str] = None


@dataclass
class CachedResult:
    """缓存的结果"""
    task_id: str
    output: str
    success: bool
    created_at: str
    hit_count: int


class AduibClient:
    """
    aduib-ai 托管服务 REST 客户端

    功能：
    - 查询结果缓存
    - 保存任务结果
    - 获取任务历史

    使用场景：
    - 本地执行 memex-cli，可选上传结果到 aduib-ai
    - 查询缓存以避免重复执行
    - Web UI 查看历史

    注意：使用 aiohttp 进行异步请求，但对外提供同步接口
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        初始化 aduib-ai 客户端

        Args:
            base_url: aduib-ai 服务地址，默认从环境变量 ADUIB_URL 读取
            api_key: API 密钥，默认从环境变量 ADUIB_API_KEY 读取
            timeout: 请求超时时间（秒）

        Raises:
            ImportError: 如果未安装 aiohttp 库
            ValueError: 如果未提供 API Key
        """
        if aiohttp is None:
            raise ImportError(
                "请安装 aiohttp 库以使用远程服务：pip install aiohttp"
            )

        self.base_url = base_url or os.getenv("ADUIB_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("ADUIB_API_KEY")
        self.timeout = timeout

        if not self.api_key:
            raise ValueError(
                "未提供 ADUIB_API_KEY。请设置环境变量或传入 api_key 参数。"
            )

        # 确保 base_url 不以斜杠结尾
        self.base_url = self.base_url.rstrip("/")

        # 请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _compute_request_hash(self, request: str, mode: str, backend: str) -> str:
        """
        计算请求的哈希值（用于缓存查询）

        Args:
            request: 用户请求
            mode: 执行模式
            backend: 后端类型

        Returns:
            SHA256 哈希值
        """
        content = f"{request}:{mode}:{backend}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def _query_cache_async(
        self,
        request: str,
        mode: str,
        backend: str
    ) -> Optional[CachedResult]:
        """
        异步查询缓存

        Args:
            request: 用户请求
            mode: 执行模式
            backend: 后端类型

        Returns:
            如果缓存命中，返回 CachedResult；否则返回 None
        """
        try:
            request_hash = self._compute_request_hash(request, mode, backend)

            url = f"{self.base_url}/api/cache/query"
            params = {
                "request_hash": request_hash,
                "mode": mode,
                "backend": backend,
            }

            timeout = aiohttp.ClientTimeout(total=self.timeout)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return CachedResult(**data)
                    elif response.status == 404:
                        # 缓存未命中
                        return None
                    else:
                        # 其他错误
                        text = await response.text()
                        print(f"[警告] 缓存查询失败: {response.status} - {text}")
                        return None

        except asyncio.TimeoutError:
            print(f"[警告] 缓存查询超时")
            return None
        except aiohttp.ClientError as e:
            print(f"[警告] 无法连接到 aduib-ai 服务: {e}")
            return None
        except Exception as e:
            print(f"[警告] 缓存查询异常: {e}")
            return None

    def query_cache(
        self,
        request: str,
        mode: str,
        backend: str
    ) -> Optional[CachedResult]:
        """
        查询缓存（同步接口）

        Args:
            request: 用户请求
            mode: 执行模式
            backend: 后端类型

        Returns:
            如果缓存命中，返回 CachedResult；否则返回 None
        """
        return asyncio.run(self._query_cache_async(request, mode, backend))

    async def _save_task_result_async(
        self,
        request: str,
        mode: str,
        backend: str,
        success: bool,
        output: str,
        error: Optional[str] = None,
        run_id: Optional[str] = None,
        duration_seconds: Optional[float] = None
    ) -> bool:
        """
        异步保存任务结果

        Args:
            request: 用户请求
            mode: 执行模式
            backend: 后端类型
            success: 是否成功
            output: 输出内容
            error: 错误信息（如有）
            run_id: memex-cli 运行 ID
            duration_seconds: 执行耗时

        Returns:
            是否保存成功
        """
        try:
            request_hash = self._compute_request_hash(request, mode, backend)

            task_data = TaskData(
                request=request,
                request_hash=request_hash,
                mode=mode,
                backend=backend,
                success=success,
                output=output,
                error=error,
                run_id=run_id,
                duration_seconds=duration_seconds,
                created_at=datetime.utcnow().isoformat()
            )

            url = f"{self.base_url}/api/tasks/save"
            timeout = aiohttp.ClientTimeout(total=self.timeout)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=asdict(task_data), headers=self.headers) as response:
                    if response.status == 201:
                        return True
                    else:
                        text = await response.text()
                        print(f"[警告] 结果保存失败: {response.status} - {text}")
                        return False

        except asyncio.TimeoutError:
            print(f"[警告] 结果保存超时")
            return False
        except aiohttp.ClientError as e:
            print(f"[警告] 无法连接到 aduib-ai 服务: {e}")
            return False
        except Exception as e:
            print(f"[警告] 结果保存异常: {e}")
            return False

    def save_task_result(
        self,
        request: str,
        mode: str,
        backend: str,
        success: bool,
        output: str,
        error: Optional[str] = None,
        run_id: Optional[str] = None,
        duration_seconds: Optional[float] = None
    ) -> bool:
        """
        保存任务结果（同步接口）

        Args:
            request: 用户请求
            mode: 执行模式
            backend: 后端类型
            success: 是否成功
            output: 输出内容
            error: 错误信息（如有）
            run_id: memex-cli 运行 ID
            duration_seconds: 执行耗时

        Returns:
            是否保存成功
        """
        return asyncio.run(self._save_task_result_async(
            request, mode, backend, success, output, error, run_id, duration_seconds
        ))

    async def _get_task_history_async(
        self,
        limit: int = 50,
        offset: int = 0,
        mode: Optional[str] = None,
        backend: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        异步获取任务历史

        Args:
            limit: 返回结果数量
            offset: 偏移量
            mode: 过滤执行模式（可选）
            backend: 过滤后端类型（可选）

        Returns:
            任务列表
        """
        try:
            url = f"{self.base_url}/api/tasks/history"
            params = {
                "limit": limit,
                "offset": offset,
            }

            if mode:
                params["mode"] = mode
            if backend:
                params["backend"] = backend

            timeout = aiohttp.ClientTimeout(total=self.timeout)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        text = await response.text()
                        print(f"[警告] 历史查询失败: {response.status} - {text}")
                        return []

        except asyncio.TimeoutError:
            print(f"[警告] 历史查询超时")
            return []
        except aiohttp.ClientError as e:
            print(f"[警告] 无法连接到 aduib-ai 服务: {e}")
            return []
        except Exception as e:
            print(f"[警告] 历史查询异常: {e}")
            return []

    def get_task_history(
        self,
        limit: int = 50,
        offset: int = 0,
        mode: Optional[str] = None,
        backend: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取任务历史（同步接口）

        Args:
            limit: 返回结果数量
            offset: 偏移量
            mode: 过滤执行模式（可选）
            backend: 过滤后端类型（可选）

        Returns:
            任务列表
        """
        return asyncio.run(self._get_task_history_async(limit, offset, mode, backend))

    async def _health_check_async(self) -> bool:
        """
        异步健康检查

        Returns:
            服务是否可用
        """
        try:
            url = f"{self.base_url}/health"
            timeout = aiohttp.ClientTimeout(total=5)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    return response.status == 200

        except:
            return False

    def health_check(self) -> bool:
        """
        健康检查（同步接口）

        Returns:
            服务是否可用
        """
        return asyncio.run(self._health_check_async())

    async def _get_stats_async(self) -> Optional[Dict[str, Any]]:
        """
        异步获取用户统计信息

        Returns:
            统计数据，包括任务总数、缓存命中率等
        """
        try:
            url = f"{self.base_url}/api/stats"
            timeout = aiohttp.ClientTimeout(total=self.timeout)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None

        except Exception as e:
            print(f"[警告] 统计查询失败: {e}")
            return None

    def get_stats(self) -> Optional[Dict[str, Any]]:
        """
        获取用户统计信息（同步接口）

        Returns:
            统计数据，包括任务总数、缓存命中率等
        """
        return asyncio.run(self._get_stats_async())


def main():
    """测试 AduibClient"""
    import argparse

    parser = argparse.ArgumentParser(description="aduib-ai 客户端测试")
    parser.add_argument("--url", help="aduib-ai 服务地址")
    parser.add_argument("--api-key", help="API 密钥")
    parser.add_argument("--action", choices=["health", "stats", "history"], default="health")

    args = parser.parse_args()

    try:
        client = AduibClient(base_url=args.url, api_key=args.api_key)

        if args.action == "health":
            print("执行健康检查...")
            is_healthy = client.health_check()
            print(f"服务状态: {'✓ 可用' if is_healthy else '✗ 不可用'}")

        elif args.action == "stats":
            print("获取统计信息...")
            stats = client.get_stats()
            if stats:
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            else:
                print("无法获取统计信息")

        elif args.action == "history":
            print("获取任务历史...")
            history = client.get_task_history(limit=10)
            if history:
                print(f"最近 {len(history)} 个任务:")
                for i, task in enumerate(history, 1):
                    print(f"{i}. [{task.get('mode')}] {task.get('request')[:50]}... ({task.get('created_at')})")
            else:
                print("暂无历史记录")

    except ValueError as e:
        print(f"错误: {e}")
        print("\n请设置环境变量 ADUIB_API_KEY 或使用 --api-key 参数")
    except Exception as e:
        print(f"异常: {e}")


if __name__ == "__main__":
    main()
