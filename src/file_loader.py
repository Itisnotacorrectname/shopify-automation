"""
文件加载工具
支持从相对路径加载主题文件
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class FileLoader:
    """主题文件加载器"""
    
    def __init__(self, theme_dir: str = None):
        """
        初始化加载器
        
        Args:
            theme_dir: 主题目录路径，默认使用 ../HYL独立站/hyl-shopify-theme
        """
        if theme_dir is None:
            # 假设文件在 shopify-automation/theme/
            theme_dir = Path(__file__).parent.parent.parent / "HYL独立站" / "hyl-shopify-theme"
        
        self.theme_dir = Path(theme_dir)
        self._cache: Dict[str, str] = {}
        self._hash_cache: Dict[str, str] = {}
    
    def load_file(self, relative_path: str) -> Optional[str]:
        """
        加载文件内容
        
        Args:
            relative_path: 相对于 theme_dir 的路径
            
        Returns:
            文件内容，文件不存在返回 None
        """
        # 检查缓存
        if relative_path in self._cache:
            return self._cache[relative_path]
        
        file_path = self.theme_dir / relative_path
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self._cache[relative_path] = content
                return content
        except Exception as e:
            print(f"Error loading {relative_path}: {e}")
            return None
    
    def save_file(self, relative_path: str, content: str) -> bool:
        """
        保存文件
        
        Args:
            relative_path: 相对于 theme_dir 的路径
            content: 文件内容
            
        Returns:
            是否成功
        """
        file_path = self.theme_dir / relative_path
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # 更新缓存
            self._cache[relative_path] = content
            self._hash_cache[relative_path] = self._compute_hash(content)
            return True
        except Exception as e:
            print(f"Error saving {relative_path}: {e}")
            return False
    
    def get_file_hash(self, relative_path: str) -> Optional[str]:
        """获取文件的 MD5 哈希"""
        if relative_path in self._hash_cache:
            return self._hash_cache[relative_path]
        
        content = self.load_file(relative_path)
        if content is None:
            return None
        
        hash_value = self._compute_hash(content)
        self._hash_cache[relative_path] = hash_value
        return hash_value
    
    def _compute_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def list_files(self, pattern: str = "**/*", 
                   extensions: List[str] = None) -> List[str]:
        """
        列出目录中的文件
        
        Args:
            pattern: glob 模式
            extensions: 文件扩展名过滤，如 ['.liquid', '.json']
            
        Returns:
            文件路径列表（相对于 theme_dir）
        """
        files = []
        
        for file_path in self.theme_dir.glob(pattern):
            if file_path.is_file():
                relative = file_path.relative_to(self.theme_dir).as_posix()
                
                # 扩展名过滤
                if extensions and file_path.suffix not in extensions:
                    continue
                
                files.append(relative)
        
        return sorted(files)
    
    def get_sections(self) -> List[str]:
        """获取所有 section 文件"""
        return self.list_files("sections/*.liquid")
    
    def get_templates(self) -> List[str]:
        """获取所有模板文件"""
        return self.list_files("templates/*.json")
    
    def get_snippets(self) -> List[str]:
        """获取所有 snippet 文件"""
        return self.list_files("snippets/*.liquid")
    
    def get_assets(self) -> List[str]:
        """获取所有资源文件"""
        return self.list_files("assets/*", extensions=[".css", ".js", ".png", ".jpg", ".svg"])
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        self._hash_cache.clear()
    
    def compare_remote(self, remote_hashes: Dict[str, str]) -> Tuple[List[str], List[str], List[str]]:
        """
        比较本地文件和远程文件
        
        Args:
            remote_hashes: 远程文件的 MD5 哈希字典
            
        Returns:
            (需要上传的文件列表, 需要删除的文件列表, 未变化的文件列表)
        """
        to_upload = []
        to_delete = []
        unchanged = []
        
        # 获取本地所有文件
        local_files = set(self.list_files())
        
        # 获取远程所有文件
        remote_files = set(remote_hashes.keys())
        
        # 新增或修改的文件
        for file_path in local_files:
            local_hash = self.get_file_hash(file_path)
            remote_hash = remote_hashes.get(file_path)
            
            if local_hash != remote_hash:
                to_upload.append(file_path)
            else:
                unchanged.append(file_path)
        
        # 远程有但本地没有的文件
        for file_path in remote_files - local_files:
            to_delete.append(file_path)
        
        return to_upload, to_delete, unchanged