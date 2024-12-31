from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import requests
from browser_handler import BrowserHandler

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
                
                # 首先处理考试弹窗
                try:
                    time.sleep(2)
                    # 使用JavaScript移除考试弹窗
                    js_remove_exam = """
                    function removeExamPopup() {
                        // 1. 查找并移除考试弹窗
                        var examElements = [
                            document.querySelector('.MDL_inner_5-114-0'),
                            document.querySelector('.exam-detail_container__2_FBi'),
                            document.querySelector('[data-testid="beast-core-modal-inner"]'),
                            document.querySelector('.exam-detail_preparationExam__4THSb')
                        ].filter(Boolean);
                        
                        if (examElements.length > 0) {
                            examElements.forEach(el => {
                                // 查找最外层的modal容器
                                var modal = el.closest('[data-testid="beast-core-modal-inner"]');
                                if (modal) {
                                    var modalContainer = modal.parentElement;
                                    if (modalContainer) {
                                        modalContainer.remove();
                                    } else {
                                        modal.remove();
                                    }
                                } else {
                                    el.remove();
                                }
                            });
                            return true;
                        }
                        
                        // 2. 如果找不到具体元素，尝试移除所有modal相关元素
                        var modals = document.querySelectorAll('[class*="MDL_"][class*="modal"], [class*="exam-detail_"]');
                        if (modals.length > 0) {
                            modals.forEach(el => el.remove());
                            return true;
                        }
                        
                        return false;
                    }
                    
                    if (!removeExamPopup()) {
                        // 如果移除失败，尝试隐藏
                        var elements = document.querySelectorAll('.MDL_inner_5-114-0, .exam-detail_container__2_FBi, [data-testid="beast-core-modal-inner"]');
                        elements.forEach(function(el) {
                            if (el) {
                                el.style.display = 'none';
                                el.style.visibility = 'hidden';
                                el.style.opacity = '0';
                                el.style.pointerEvents = 'none';
                            }
                        });
                    }
                    return true;
                    """
                    
                    self.driver.execute_script(js_remove_exam)
                    print("已尝试移除考试弹窗")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"处理考试弹窗失败: {str(e)}")
                
                # 然后处理消息悬浮框
                try:
                    # 等待悬浮框出现
                    time.sleep(2)
                    
                    # 使用JavaScript移除悬浮窗
                    js_code = """
                    function removePopup() {
                        // 1. 首先尝试移除整个portal
                        var portal = document.querySelector('div[data-testid="beast-core-portal"]');
                        if (portal) {
                            portal.remove();
                            return true;
                        }
                        
                        // 2. 尝试移除所有相关的弹窗类
                        var selectors = [
                            '.PT_outerWrapper_5-114-0',
                            '.PP_outerWrapper_5-114-0',
                            '.PT_popover_5-114-0',
                            '.PT_portalBottom_5-114-0',
                            '.PT_portalWithArrow_5-114-0',
                            '.PT_inCustom_5-114-0',
                            '.PP_popover_5-114-0',
                            '.PP_popoverWithTitle_5-114-0'
                        ];
                        
                        var elements = document.querySelectorAll(selectors.join(','));
                        if (elements.length > 0) {
                            elements.forEach(function(el) {
                                el.remove();
                            });
                            return true;
                        }
                        
                        // 3. 如果还是找不到，尝试移除所有可能的弹窗容器
                        var possiblePopups = document.querySelectorAll('div[class*="PT_"][class*="PP_"]');
                        if (possiblePopups.length > 0) {
                            possiblePopups.forEach(function(el) {
                                el.remove();
                            });
                            return true;
                        }
                        
                        return false;
                    }
                    
                    if (!removePopup()) {
                        // 如果移除失败，尝试隐藏
                        var selectors = [
                            'div[data-testid="beast-core-portal"]',
                            '.PT_outerWrapper_5-114-0',
                            '.PP_outerWrapper_5-114-0',
                            '.PT_popover_5-114-0',
                            '.PT_portalBottom_5-114-0',
                            '.PT_portalWithArrow_5-114-0',
                            '.PT_inCustom_5-114-0',
                            '.PP_popover_5-114-0',
                            '.PP_popoverWithTitle_5-114-0'
                        ];
                        
                        document.querySelectorAll(selectors.join(',')).forEach(function(el) {
                            el.style.display = 'none';
                            el.style.visibility = 'hidden';
                            el.style.opacity = '0';
                            el.style.pointerEvents = 'none';
                        });
                    }
                    return true;
                    """
                    
                    self.driver.execute_script(js_code)
                    print("已尝试移除或隐藏消息悬浮框")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"处理消息悬浮框失败: {str(e)}")
                    
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
        
        
