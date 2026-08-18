from __future__ import annotations
from .rules import LifeRule, DEFAULT_RULE


def create_engine(name: str, rule: LifeRule = DEFAULT_RULE):
    """Build an engine by name, with hashlife -> sparse fallback on missing dep."""
    from .engines.sparse import SparseEngine
    key = name.lower()
    if key == "sparse":
        return SparseEngine(rule)
    if key == "hashlife":
        try:
            from .engines.hashlife_adapter import HashlifeEngine
            return HashlifeEngine(rule)
        except Exception:
            return SparseEngine(rule)
    raise KeyError(f"unknown engine: {name} (options: sparse, hashlife)")
