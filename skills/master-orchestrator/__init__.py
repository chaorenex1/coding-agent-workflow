"""
Orchestrator - 跨后端AI任务协调系统

主要模块：
- master_orchestrator: 总协调器入口
- core: 核心后端编排和事件解析
- executors: 命令、Agent、提示词执行器
- clients: 远程服务客户端
- skills: 技能注册和工作流
- analyzers: 意图分析（Claude LLM + 规则引擎）
"""

# 延迟导入避免循环依赖
def _lazy_import():
    from .master_orchestrator import MasterOrchestrator, ExecutionMode, Intent
    from .core.backend_orchestrator import BackendOrchestrator, TaskResult
    return MasterOrchestrator, BackendOrchestrator, ExecutionMode, Intent, TaskResult

# 懒加载导出
def __getattr__(name):
    if name in ["MasterOrchestrator", "BackendOrchestrator", "ExecutionMode", "Intent", "TaskResult"]:
        MasterOrchestrator, BackendOrchestrator, ExecutionMode, Intent, TaskResult = _lazy_import()
        globals().update({
            "MasterOrchestrator": MasterOrchestrator,
            "BackendOrchestrator": BackendOrchestrator,
            "ExecutionMode": ExecutionMode,
            "Intent": Intent,
            "TaskResult": TaskResult,
        })
        return globals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__version__ = "1.0.0"
__all__ = [
    "MasterOrchestrator",
    "BackendOrchestrator",
    "ExecutionMode",
    "Intent",
    "TaskResult",
]
