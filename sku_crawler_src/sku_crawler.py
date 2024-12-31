import requests
import time
from login_handler import LoginHandler
from browser_handler import BrowserHandler
from navigation_handler import NavigationHandler
from sku_handler import SkuHandler
from barcode_handler import BarcodeHandler
from label_generator import LabelGenerator


def main():
    # 创建session对象
    session = requests.Session()
    
    # 初始化浏览器
    driver, wait = BrowserHandler.init_browser()
    
    try:
        # 登录处理
        login_handler = LoginHandler(driver, wait, session)
        username = '18237084494'
        password = 'Isa981213'
        
        if not login_handler.login(username, password):
            print("登录失败")
            return
            
        print("登录成功")
        
        # 导航到商品条码页面
        navigation_handler = NavigationHandler(driver, wait)
        if not navigation_handler.navigate_to_product_label():
            print("导航失败")
            return
            
        print("导航成功")
        # 等待页面完全加载和权限初始化
        time.sleep(5)
        
        # 获取所有条码
        print("\n开始获取商品条码...")
        barcode_handler = BarcodeHandler(driver, wait)
        barcode_handler.process_all_products()
        print("条码获取完成")
        
        # generator = LabelGenerator()
        # generator.process_all_skus()
        
        # 获取SKU信息
        # sku_handler = SkuHandler(session)
        # all_sku_ids = sku_handler.fetch_all_skus()
        
        # if all_sku_ids:
        #     print(f"成功获取到 {len(all_sku_ids)} 个SKU ID")
        #     # 保存到文件
        #     sku_handler.save_to_file(all_sku_ids)
        # else:
        #     print("未获取到SKU数据")
            
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
    finally:
        # 关闭浏览器
        if driver:
            time.sleep(1200)
            print("关闭浏览器")
            # driver.quit()

if __name__ == "__main__":
    main() 