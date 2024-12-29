from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

class NavigationHandler:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        
    def navigate_to_product_label(self):
        """导航到商品条码管理页面"""
        try:
            # 1. 点击"进入"按钮
            print("等待进入按钮...")
            try:
                # 等待页面加载完成
                time.sleep(3)
                
                # 使用JavaScript直接查找并点击按钮
                js_code = """
                var elements = document.getElementsByClassName('site-main_btnGroup__3fEoG');
                if (elements.length > 0) {
                    elements[0].click();
                    return true;
                }
                return false;
                """
                
                if not self.driver.execute_script(js_code):
                    # 如果通过class查找失败，尝试通过文本内容查找
                    js_code = """
                    var elements = document.querySelectorAll('div');
                    for (var el of elements) {
                        if (el.textContent.trim() === '进入 >') {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                    """
                    if not self.driver.execute_script(js_code):
                        print("未找到进入按钮")
                        return False
                    
                print("已点击进入按钮")
                time.sleep(3)  # 等待页面加载
                return True
                    
            except Exception as e:
                print(f"点击进入按钮失败: {str(e)}")
                return False
                
        except Exception as e:
            print(f"导航过程出错: {str(e)}")
            return False