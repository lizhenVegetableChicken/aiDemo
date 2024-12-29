import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, Optional, List

class SkuHandler:
    def __init__(self, session):
        self.session = session
        self.base_url = "https://seller.kuajingmaihuo.com"
        self.headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "content-type": "application/json",
            "mallid": "634418219677180",
            "origin": "https://seller.kuajingmaihuo.com",
            "priority": "u=1, i",
            "referer": "https://seller.kuajingmaihuo.com/main/product/label",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        self._setup_logging()

    def _setup_logging(self):
        """设置日志"""
        # 创建logs目录（如果不存在）
        import os
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # 生成日志文件名，包含时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'logs/sku_crawler_{timestamp}.log'
        
        # 配置日志
        self.logger = logging.getLogger('sku_crawler')
        self.logger.setLevel(logging.DEBUG)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加处理器到logger
        self.logger.addHandler(file_handler)

    def set_cookies(self, cookies: str) -> None:
        """
        设置登录cookies
        :param cookies: 完整的cookie字符串，从浏览器复制
        """
        # 更新session的cookies
        cookie_dict = {}
        for item in cookies.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookie_dict[key] = value
        
        self.session.cookies.update(cookie_dict)
        # 同时将cookies添加到请求头中
        self.headers['Cookie'] = cookies
        self.logger.info("Cookies已更新")

    def get_sku_list(self, page: int = 1, page_size: int = 50) -> Optional[Dict]:
        """
        获取SKU列表
        :param page: 页码，从1开始
        :param page_size: 每页数量
        :return: 响应数据
        """
        url = f"{self.base_url}/bg-visage-mms/labelcode/pageQuery"
        
        payload = {
            "page": page,
            "pageSize": page_size
        }

        try:
            # 记录请求信息
            self.logger.info("\n=== 请求信息 ===")
            self.logger.info(f"请求URL: {url}")
            
            self.logger.info("\n请求头:")
            for key, value in self.headers.items():
                self.logger.info(f"{key}: {value}")
            
            self.logger.info("\n请求体:")
            self.logger.info(json.dumps(payload, ensure_ascii=False, indent=2))
            
            self.logger.info("\nCookies:")
            for cookie in self.session.cookies:
                self.logger.info(f"{cookie.name}: {cookie.value}")
            
            self.logger.info("================\n")

            response = self.session.post(
                url, 
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                # 记录响应信息
                self.logger.info("\n=== 响应信息 ===")
                self.logger.info(f"响应状态码: {response.status_code}")
                
                self.logger.info("\n响应头:")
                for key, value in response.headers.items():
                    self.logger.info(f"{key}: {value}")
                
                self.logger.info("\n响应体:")
                self.logger.info(json.dumps(response.json(), ensure_ascii=False, indent=2))
                self.logger.info("================\n")
                
                return response.json()
            else:
                self.logger.error(f"请求失败，状态码: {response.status_code}")
                self.logger.error(f"响应内容: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"请求发生错误: {str(e)}")
            return None

    def extract_product_sku_ids(self, response_data: Dict) -> List[str]:
        """
        从响应数据中提取productSkuId
        :param response_data: API响应数据
        :return: productSkuId列表
        """
        sku_ids = []
        try:
            # 检查响应是否成功
            if not response_data.get('success'):
                self.logger.error("响应表明请求失败")
                return sku_ids

            # 获取result中的pageItems
            page_items = response_data.get('result', {}).get('pageItems', [])
            total = response_data.get('result', {}).get('total', 0)
            self.logger.info(f"总记录数: {total}")
            self.logger.info(f"当前页面记录数: {len(page_items)}")

            # 遍历每个商品项
            for item in page_items:
                if 'labelCodeVO' in item and 'productSkuId' in item['labelCodeVO']:
                    sku_id = item['labelCodeVO']['productSkuId']
                    product_name = item.get('productName', 'Unknown')
                    self.logger.info(f"提取SKU ID: {sku_id}, 商品名称: {product_name}")
                    sku_ids.append(str(sku_id))  # 转换为字符串以保持一致性

        except Exception as e:
            self.logger.error(f"提取SKU ID时发生错误: {str(e)}")
            
        self.logger.info(f"本页共提取到 {len(sku_ids)} 个SKU ID")
        return sku_ids

    def fetch_all_skus(self) -> List[str]:
        """
        获取所有SKU ID
        :return: 所有的productSkuId列表
        """
        all_sku_ids = []
        page = 1
        
        while True:
            self.logger.info(f"正在获取第 {page} 页数据...")
            response_data = self.get_sku_list(page=page)
            
            if not response_data:
                self.logger.error("获取页面数据失败")
                break
                
            sku_ids = self.extract_product_sku_ids(response_data)
            if not sku_ids:
                self.logger.info("当前页面没有找到SKU ID")
                break
                
            all_sku_ids.extend(sku_ids)
            self.logger.info(f"当前已累计获取 {len(all_sku_ids)} 个SKU ID")
            
            # 检查是否还有下一页
            total = response_data.get('result', {}).get('total', 0)
            if page * 50 >= total:
                self.logger.info(f"已到达最后一页，总记录数: {total}")
                break
                
            page += 1
            time.sleep(1)  # 添加延时，避免请求过快
            
        self.logger.info(f"获取完成，共获取到 {len(all_sku_ids)} 个SKU ID")
        return all_sku_ids

    @staticmethod
    def save_to_file(data: List[str], filename: str = "sku_ids.json") -> None:
        """
        保存SKU ID列表到文件
        :param data: SKU ID列表
        :param filename: 保存的文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.getLogger('sku_crawler').info(f"数据已保存到: {filename}")
        except Exception as e:
            logging.getLogger('sku_crawler').error(f"保存数据时发生错误: {str(e)}") 