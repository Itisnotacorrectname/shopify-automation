"""
Shopify API Client
统一的 API 客户端，包含重试、限流、错误处理等功能
"""

import time
import hashlib
import logging
from typing import Any, Dict, Optional
from pathlib import Path

import requests
import yaml


class ShopifyAPIError(Exception):
    """API 错误异常"""
    pass


class ShopifyClient:
    """Shopify API 客户端"""
    
    def __init__(self, config_path: str = None, env: str = None):
        """
        初始化客户端
        
        Args:
            config_path: 配置文件路径，默认使用 config.yaml
            env: 环境名称(dev/staging/prod)，默认使用配置文件中的 current_env
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
        
        self.config = self._load_config(config_path)
        
        # 确定使用哪个环境
        if env is None:
            env = self.config.get("current_env", "dev")
        
        env_config = self.config["environments"].get(env)
        if not env_config:
            raise ValueError(f"Environment '{env}' not found in config")
        
        self.store = env_config["store"]
        self.token = env_config["token"]
        self.theme_id = env_config["theme_id"]
        self.api_version = env_config["api_version"]
        
        self.base_url = f"https://{self.store}/admin/api/{self.api_version}"
        self.headers = {
            "X-Shopify-Access-Token": self.token,
            "Content-Type": "application/json"
        }
        
        # 限流配置
        self.rate_limit = self.config.get("rate_limit", {})
        self.max_retries = self.rate_limit.get("max_retries", 3)
        self.retry_delay = self.rate_limit.get("retry_delay", 2)
        self.min_request_interval = 1.0 / self.rate_limit.get("requests_per_second", 2)
        
        # 日志
        self._setup_logging()
        
        # 请求计数
        self._last_request_time = 0
        
        # 缓存（用于增量部署）
        self._cache = {}
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self):
        """设置日志"""
        log_config = self.config.get("logging", {})
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, log_config.get("level", "INFO")),
            format=log_config.get("format", "%(asctime)s - %(levelname)s - %(message)s"),
            handlers=[
                logging.FileHandler(log_dir / "shopify.log", encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ShopifyAPI")
    
    def _rate_limit(self):
        """限流：确保请求间隔"""
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self._last_request_time = time.time()
    
    def _request(self, method: str, endpoint: str, data: Dict = None, 
                 retries: int = None) -> Dict:
        """
        发送 API 请求（带重试机制）
        
        Args:
            method: HTTP 方法 (GET, PUT, POST, DELETE)
            endpoint: API 端点
            data: 请求数据
            retries: 重试次数，默认使用配置值
        
        Returns:
            API 响应数据
        """
        if retries is None:
            retries = self.max_retries
        
        self._rate_limit()
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(retries):
            try:
                if method == "GET":
                    resp = requests.get(url, headers=self.headers, timeout=30)
                elif method == "PUT":
                    resp = requests.put(url, headers=self.headers, json=data, timeout=30)
                elif method == "POST":
                    resp = requests.post(url, headers=self.headers, json=data, timeout=30)
                elif method == "DELETE":
                    resp = requests.delete(url, headers=self.headers, timeout=30)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                # 检查响应状态
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 429:
                    # 限流，等待后重试
                    wait_time = int(resp.headers.get("Retry-After", self.retry_delay))
                    self.logger.warning(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif resp.status_code == 422:
                    # 验证错误，不再重试
                    self.logger.error(f"Validation error: {resp.text}")
                    raise ShopifyAPIError(f"422 Error: {resp.text}")
                else:
                    self.logger.warning(f"Request failed ({resp.status_code}), attempt {attempt + 1}/{retries}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request error: {e}, attempt {attempt + 1}/{retries}")
                if attempt < retries - 1:
                    time.sleep(self.retry_delay)
        
        raise ShopifyAPIError(f"Failed after {retries} retries")
    
    # ========== 资源操作 ==========
    
    def get_asset(self, key: str) -> Optional[Dict]:
        """获取单个资源"""
        try:
            data = self._request("GET", f"themes/{self.theme_id}/assets.json?asset[key]={key}")
            return data.get("asset", {})
        except ShopifyAPIError:
            return None
    
    def upload_asset(self, key: str, value: str) -> Dict:
        """上传资源"""
        data = {"asset": {"key": key, "value": value}}
        result = self._request("PUT", f"themes/{self.theme_id}/assets.json", data)
        self.logger.info(f"Uploaded: {key}")
        return result
    
    def delete_asset(self, key: str) -> Dict:
        """删除资源"""
        result = self._request("DELETE", f"themes/{self.theme_id}/assets.json?asset[key]={key}")
        self.logger.info(f"Deleted: {key}")
        return result
    
    def get_all_assets(self) -> Dict[str, str]:
        """获取所有资源的 MD5 哈希（用于增量部署）"""
        assets = {}
        url = f"themes/{self.theme_id}/assets.json"
        
        while url:
            data = self._request("GET", url.replace(self.base_url + "/", ""))
            for asset in data.get("assets", []):
                key = asset["key"]
                # 缓存内容用于比较
                assets[key] = hashlib.md5(str(asset.get("value", "")).encode()).hexdigest()
            
            # 处理分页
            next_url = data.get("pagination", {}).get("next_url")
            url = next_url if next_url else None
        
        return assets
    
    def md5_hash(self, content: str) -> str:
        """计算内容 MD5 哈希"""
        return hashlib.md5(content.encode()).hexdigest()
    
    # ========== 产品操作 ==========
    
    def get_products(self, limit: int = 50) -> list:
        """获取产品列表"""
        data = self._request("GET", f"products.json?limit={limit}")
        return data.get("products", [])
    
    def create_product(self, product_data: Dict) -> Dict:
        """创建产品"""
        data = self._request("POST", "products.json", {"product": product_data})
        return data.get("product", {})
    
    def update_product(self, product_id: int, product_data: Dict) -> Dict:
        """更新产品"""
        data = self._request("PUT", f"products/{product_id}.json", {"product": product_data})
        return data.get("product", {})
    
    # ========== 页面操作 ==========
    
    def get_pages(self) -> list:
        """获取页面列表"""
        data = self._request("GET", "pages.json")
        return data.get("pages", [])
    
    def create_page(self, page_data: Dict) -> Dict:
        """创建页面"""
        data = self._request("POST", "pages.json", {"page": page_data})
        return data.get("page", {})
    
    # ========== 导航操作 ==========
    
    def get_navigation(self) -> list:
        """获取导航链接列表"""
        data = self._request("GET", "navigation.json")
        return data.get("navigation", [])
    
    def create_navigation(self, nav_data: Dict) -> Dict:
        """创建导航链接"""
        data = self._request("POST", "navigation.json", nav_data)
        return data.get("navigation", {})