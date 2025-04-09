"""自定义类型声明，解决 django-environ 的类型检查问题"""
from typing import Any, Callable, List, TypeVar, overload, Union, Optional
import environ

T = TypeVar('T')

class EnvWithTypes(environ.Env):
    @overload
    def bool(self, var: str, default: bool = ...) -> bool: ...
    
    @overload
    def list(self, var: str, default: List[str] = ...) -> List[str]: ...
    
    @overload
    def db(self, var: str, default: str = ...) -> dict: ...
