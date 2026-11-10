"""工具类基类"""
from dataclasses import dataclass
from typing import Callable
@dataclass
class Tool():
    name: str
    description: str
    run: Callable[[str],str]

@dataclass
class Evaluation():
    success: bool
    score: float
    feedback: str