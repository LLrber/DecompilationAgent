"""
配置管理模块

负责管理应用程序的各种配置。
"""

from .settings import Settings, get_settings

__all__ = ['Settings', 'get_settings'] 