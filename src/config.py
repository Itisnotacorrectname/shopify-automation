"""
Config Module - 配置管理
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Optional


class Config:
    """配置管理器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load()
    
    def _load(self) -> Dict:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save(self):
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
    
    def get_env(self, name: str = None) -> Dict:
        """获取环境配置"""
        if name is None:
            name = self.config.get("current_env", "dev")
        return self.config["environments"].get(name, {})
    
    def set_current_env(self, name: str):
        """设置当前环境"""
        if name not in self.config["environments"]:
            raise ValueError(f"Environment '{name}' not found")
        self.config["current_env"] = name
        self.save()
    
    def update_env(self, name: str, **kwargs):
        """更新环境配置"""
        if name not in self.config["environments"]:
            self.config["environments"][name] = {}
        
        self.config["environments"][name].update(kwargs)
        self.save()
    
    @classmethod
    def from_env(cls) -> 'Config':
        """从环境变量创建配置"""
        config = cls()
        
        # 检查环境变量
        store = os.getenv("SHOPIFY_STORE")
        token = os.getenv("SHOPIFY_TOKEN")
        theme_id = os.getenv("SHOPIFY_THEME_ID")
        
        if store and token:
            # 更新当前环境
            env_name = config.config.get("current_env", "dev")
            config.update_env(
                env_name,
                store=store,
                token=token,
                theme_id=int(theme_id) if theme_id else None
            )
        
        return config