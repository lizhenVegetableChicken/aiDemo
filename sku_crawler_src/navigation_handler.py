from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

class NavigationHandler:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        
    def navigate_to_product_label(self):
        """点击进入按钮"""
        try:
            print("等待进入按钮...")
            time.sleep(3)  # 等待页面加载
            
            # 使用JavaScript点击按钮
            js_code = """
            var btnGroup = document.querySelector('.site-main_btnGroup__3fEoG');
            if (btnGroup) {
                btnGroup.click();
                return true;
            }
            return false;
            """
            
            if self.driver.execute_script(js_code):
                print("已点击进入按钮")
                time.sleep(3)  # 等待页面加载
                return True
            else:
                print("未找到进入按钮")
                return False
                
        except Exception as e:
            print(f"点击进入按钮失败: {str(e)}")
            return False