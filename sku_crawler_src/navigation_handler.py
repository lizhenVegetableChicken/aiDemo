from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

class NavigationHandler:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        
    def navigate_to_product_label(self):
        """导航到商品标签页面"""
        try:
            print("等待进入按钮...")
            time.sleep(3)  # 等待页面完全加载
            
            # 使用JavaScript直接查找和点击按钮
            js_code = """
            function findAndClickEnterButton() {
                // 方法1：通过class和文本内容查找
                var elements = document.getElementsByClassName('site-main_btnGroup__3fEoG');
                for (var i = 0; i < elements.length; i++) {
                    if (elements[i].textContent.trim().startsWith('进入')) {
                        elements[i].click();
                        return true;
                    }
                }
                
                // 方法2：通过父元素结构查找
                var siteSection = document.querySelector('.site-main_siteSection__2DBie');
                if (siteSection) {
                    var btnGroup = siteSection.querySelector('.site-main_btnGroup__3fEoG');
                    if (btnGroup) {
                        btnGroup.click();
                        return true;
                    }
                }
                
                // 方法3：通过完整路径查找
                var enterBtn = document.evaluate(
                    "//div[contains(@class, 'site-main_siteSection')]/div[contains(@class, 'site-main_btnGroup') and contains(text(), '进入')]",
                    document,
                    null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                    null
                ).singleNodeValue;
                
                if (enterBtn) {
                    enterBtn.click();
                    return true;
                }
                
                return false;
            }
            return findAndClickEnterButton();
            """
            
            if self.driver.execute_script(js_code):
                print("已点击进入按钮")
                time.sleep(2)  # 等待页面加载
                
                # 验证是否成功进入
                if "/main" in self.driver.current_url:
                    print("成功进入系统")
                    return True
                else:
                    print("导航失败，当前URL:", self.driver.current_url)
                    return False
            else:
                print("未找到进入按钮")
                # 保存页面源码以便调试
                with open("page_source.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("已保存页面源码到page_source.html")
                return False
                
        except Exception as e:
            print(f"导航过程出错: {str(e)}")
            # 保存页面源码以便调试
            try:
                with open("error_page.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("已保存错误页面源码到error_page.html")
            except:
                pass
            return False