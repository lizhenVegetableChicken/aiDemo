from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

class BarcodeHandler:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        
    def navigate_to_barcode_page(self):
        """导航到商品条码管理页面"""
        try:
            print("等待商品条码管理链接...")
            try:
                # 首先尝试点击备货单管理展开菜单
                menu_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'bg-shell-theme-name')]/div/div[text()='备货单管理']"))
                )
                menu_button.click()
                time.sleep(2)  # 等待子菜单展开
                
                # 然后点击商品条码管理
                barcode_link = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@href='/main/product/label']//div[contains(@class, 'bg-shell-theme-name')]//div[contains(text(), '商品条码管理')]"))
                )
                barcode_link.click()
                print("已点击商品条码管理链接")
                
            except Exception as e:
                print(f"点击商品条码管理失败: {str(e)}")
                return False
            
            time.sleep(2)  # 等待页面加载
            
            # 验证是否成功进入商品条码管理页面
            if "/main/product/label" in self.driver.current_url:
                print("已成功进入商品条码管理页面")
                return True
            else:
                print("导航失败，当前URL:", self.driver.current_url)
                return False
                
        except Exception as e:
            print(f"导航过程出错: {str(e)}")
            return False 