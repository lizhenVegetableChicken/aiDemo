import requests
import json
from typing import Dict, Optional

class HttpSkuCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://seller.kuajingmaihuo.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://seller.kuajingmaihuo.com",
            "Referer": "https://seller.kuajingmaihuo.com/main/product/label",
        }

    def login(self, cookies: str) -> None:
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

    def get_sku_list(self, page: int = 1, page_size: int = 20) -> Optional[Dict]:
        """
        获取SKU列表
        :param page: 页码，从1开始
        :param page_size: 每页数量
        :return: 响应数据
        """
        url = f"{self.base_url}/bg-visage-mms/labelcode/pageQuery"
        
        payload = {
            "pageNo": page,
            "pageSize": page_size
        }

        try:
            response = self.session.post(url, 
                                       headers=self.headers,
                                       json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                return None
        except Exception as e:
            print(f"请求发生错误: {str(e)}")
            return None

    def extract_product_sku_ids(self, response_data: Dict) -> list:
        """
        从响应数据中提取productSkuId
        :param response_data: API响应数据
        :return: productSkuId列表
        """
        sku_ids = []
        if not response_data or 'ult' not in response_data:
            return sku_ids
            
        try:
            for item in response_data['ult'].get('pageItems', []):
                if 'labelCodeV0' in item and 'productSkuId' in item['labelCodeV0']:
                    sku_ids.append(item['labelCodeV0']['productSkuId'])
        except Exception as e:
            print(f"提取SKU ID时发生错误: {str(e)}")
            
        return sku_ids

def main():
    # 创建爬虫实例
    crawler = HttpSkuCrawler()
    
    # 设置cookies（需要从浏览器中复制完整的cookie字符串）
    cookies = input("请输入cookies字符串: ")
    crawler.login(cookies)
    
    # 获取第一页数据
    response_data = crawler.get_sku_list(page=1, page_size=20)
    
    if response_data:
        # 提取productSkuId
        sku_ids = crawler.extract_product_sku_ids(response_data)
        print(f"获取到的productSkuId列表:")
        for sku_id in sku_ids:
            print(sku_id)
    else:
        print("获取数据失败")

if __name__ == "__main__":
    main() 