import json
import os
from datetime import datetime

class SkuHandler:
    def __init__(self, session):
        self.session = session
        
    def process_sku_data(self, data):
        """处理API返回的SKU数据"""
        try:
            # 根据实际API响应结构处理数据
            if not data or 'data' not in data:
                return None
                
            items = data['data'].get('items', [])
            processed_items = []
            
            for item in items:
                processed_item = {
                    'sku_id': item.get('skuId'),
                    'product_name': item.get('productName'),
                    'barcode': item.get('barcode'),
                    # 添加其他需要的字段...
                }
                processed_items.append(processed_item)
                
            return processed_items
            
        except Exception as e:
            print(f"处理SKU数据失败: {str(e)}")
            return None
            
    def save_to_file(self, data, filename=None):
        """保存SKU数据到文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'sku_data_{timestamp}.json'
            
        try:
            # 确保输出目录存在
            output_dir = 'output'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"数据已保存到文件: {filepath}")
            return True
            
        except Exception as e:
            print(f"保存数据失败: {str(e)}")
            return False 