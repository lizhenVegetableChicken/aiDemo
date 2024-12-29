import requests
import json
import time

class SkuHandler:
    def __init__(self, session):
        self.session = session
        self.base_url = "https://seller.kuajingmaihuo.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://seller.kuajingmaihuo.com",
            "Referer": "https://seller.kuajingmaihuo.com/main/product/label",
            "X-Requested-With": "XMLHttpRequest"
        }

    def get_sku_list(self, page=1, size=20):
        """获取SKU列表"""
        try:
            url = f"{self.base_url}/main/product/label/list"
            params = {
                "page": page,
                "pageSize": size,
                "sortField": "createTime",
                "sortOrder": "desc"
            }
            
            response = self.session.get(
                url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('code') == 200:
                        return data.get('data', {})
                    else:
                        print(f"获取数据失败: {data.get('message', '未知错误')}")
                except:
                    print(f"解析响应失败: {response.text}")
            else:
                print(f"获取SKU列表失败: {response.text}")
            return None
                
        except Exception as e:
            print(f"获取SKU列表时发生错误: {str(e)}")
            return None

    @staticmethod
    def save_to_file(data, filename="sku_data.json"):
        """保存数据到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到: {filename}")
        except Exception as e:
            print(f"保存数据时发生错误: {str(e)}")
            
    def fetch_all_skus(self):
        """获取所有SKU数据"""
        all_skus = []
        page = 1
        
        while True:
            print(f"正在获取第 {page} 页数据...")
            data = self.get_sku_list(page=page)
            
            if not data:
                break
                
            items = data.get('items', [])
            if not items:
                break
                
            all_skus.extend(items)
            
            if page >= data.get('totalPages', 1):
                break
                
            page += 1
            time.sleep(1)
            
        return all_skus 