import requests
from browser_handler import BrowserHandler
from login_handler import LoginHandler
from sku_handler import SkuHandler
from navigation_handler import NavigationHandler

def main():
    driver = None
    try:
        # 初始化浏览器
        driver, wait = BrowserHandler.init_browser()
        session = requests.Session()
        
        # 登录处理
        login_handler = LoginHandler(driver, wait, session)
        username = '18237084494'
        password = 'Isa981213'
        
        if not login_handler.login(username, password):
            print("登录失败，程序退出")
            return
        
        # 导航到商品条码管理页面
        print("开始导航到商品条码管理页面...")
        navigation_handler = NavigationHandler(driver, wait)
        if not navigation_handler.navigate_to_product_label():
            print("导航到商品条码管理页面失败，程序退出")
            return
            
        # SKU数据处理
        sku_handler = SkuHandler(session)
        all_skus = sku_handler.fetch_all_skus()
        
        if all_skus:
            sku_handler.save_to_file(all_skus)
            print(f"共获取 {len(all_skus)} 条SKU数据")
        else:
            print("未获取到SKU数据")
            
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main() 