from typing import Callable, Dict
from .rules import LifeRule, DEFAULT_RULE
from .engines.sparse import SparseEngine

_REGISTRY: Dict[str, Callable[[LifeRule], object]] = {}


def register(name: str):
    """类装饰器：注册引擎到工厂。"""
    def deco(cls):
        _REGISTRY[name.lower()] = lambda rule: cls(rule)
        return cls
    return deco


def create_engine(name: str, rule: LifeRule = DEFAULT_RULE):
    """根据名称创建引擎实例（带容错回退）。"""
    key = name.lower()
    if key in _REGISTRY:
        return _REGISTRY[key](rule)
    if key == "sparse":
        return SparseEngine(rule)
    if key == "hashlife":
        try:
            from .engines.hashlife_adapter import HashlifeEngine
            return HashlifeEngine(rule)
        except Exception as ex:
            # 在 ARM 或缺依赖时回退到稀疏引擎
            print(f"[lifex] 警告：HashLife 引擎不可用（{ex.__class__.__name__}: {ex}），已回退到 sparse。")
            return SparseEngine(rule)
    raise KeyError(f"未知引擎: {name}. 可选: {list(_REGISTRY.keys()) + ['sparse','hashlife']}")
