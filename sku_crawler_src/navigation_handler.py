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
            # 直接访问商品条码页面
            print("正在访问商品条码页面...")
            self.driver.get("https://seller.kuajingmaihuo.com/main/product/label")
            time.sleep(5)  # 等待页面加载
            
            # 检查当前URL
            current_url = self.driver.current_url
            print(f"当前URL: {current_url}")
            
            # 如果URL包含login，说明需要重新登录
            if "/login" in current_url:
                print("需要重新登录")
                return False
                
            # 如果URL是首页，需要点击进入按钮
            if current_url == "https://seller.kuajingmaihuo.com/":
                print("在首页，尝试点击进入按钮...")
                try:
                    time.sleep(3)
                    # 使用JavaScript点击进入按钮
                    js_code = """
                    var elements = document.getElementsByClassName('site-main_btnGroup__3fEoG');
                    if (elements.length > 0) {
                        elements[0].click();
                        return true;
                    }
                    var elements = document.querySelectorAll('div');
                    for (var el of elements) {
                        if (el.textContent.trim() === '进入 >') {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                    """
                    if self.driver.execute_script(js_code):
                        print("已点击进入按钮")
                        time.sleep(5)
                        # 再次直接访问商品条码页面
                        self.driver.get("https://seller.kuajingmaihuo.com/main/product/label")
                        time.sleep(8)  # 增加等待时间
                    else:
                        print("未找到进入按钮")
                        return False
                except Exception as e:
                    print(f"点击进入按钮失败: {str(e)}")
                    return False
            
            # 等待页面加载完成
            try:
                # 等待页面上的某个特定元素出现
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'container')]"))
                )
                print("页面加载完成")
            except Exception as e:
                print(f"等待页面加载完成失败: {str(e)}")
            
            # 最后再次检查URL
            current_url = self.driver.current_url
            if "/main/product/label" not in current_url:
                print(f"导航失败，当前URL: {current_url}")
                return False
                
            print("成功导航到商品条码页面")
            # 额外等待，确保页面完全加载
            time.sleep(5)
            return True
                
        except Exception as e:
            print(f"导航过程出错: {str(e)}")
            return False