from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

class LoginHandler:
    def __init__(self, driver, wait, session):
        self.driver = driver
        self.wait = wait
        self.session = session
        self.base_url = "https://seller.kuajingmaihuo.com"
        
    def get_anti_content(self):
        """获取anti-content值"""
        try:
            # 等待页面完全加载
            time.sleep(3)
            
            # 尝试从页面源码中查找anti-content相关信息
            page_source = self.driver.page_source
            if "anti" in page_source.lower():
                print("找到anti相关信息，正在分析...")
                
            # 尝试执行页面上的所有script标签
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                src = script.get_attribute("src")
                if src and ("anti" in src.lower() or "security" in src.lower()):
                    print(f"找到可能相关的脚本: {src}")
            
            # 尝试多种可能的方式获取anti-content
            scripts = [
                "return window._anti_content;",  # 直接从window对象获取
                "return document.querySelector('meta[name=\"anti-content\"]')?.content;",  # 从meta标签获取
                "return localStorage.getItem('anti-content');",  # 从localStorage获取
                "return sessionStorage.getItem('anti-content');",  # 从sessionStorage获取
                "return window.localStorage.getItem('anti-content');",  # 从window.localStorage获取
                """
                for (let key in window) {
                    if (key.toLowerCase().includes('anti')) {
                        return window[key];
                    }
                }
                return null;
                """  # 遍历window对象
            ]
            
            for script in scripts:
                try:
                    value = self.driver.execute_script(script)
                    if value:
                        print(f"成功获取anti-content: {value[:50]}...")  # 只打印前50个字符
                        return value
                except Exception as e:
                    continue
                    
            # 如果上述方法都失败，尝试从Network面板获取
            print("无法直接获取anti-content，请在开发者工具中查看请求头")
            return None
            
        except Exception as e:
            print(f"获取anti-content失败: {str(e)}")
            return None
            
    def get_mall_id(self):
        """获取商家ID"""
        try:
            # 等待页面完全加载
            time.sleep(3)
            
            # 尝试从页面源码中查找mallId相关信息
            page_source = self.driver.page_source
            if "mallId" in page_source or "mall_id" in page_source:
                print("找到mallId相关信息，正在分析...")
            
            # 尝试多种可能的方式获取mallid
            scripts = [
                "return window.mallId;",  # 直接从window对象获取
                "return localStorage.getItem('mallId');",  # 从localStorage获取
                "return document.querySelector('meta[name=\"mall-id\"]')?.content;",  # 从meta标签获取
                "return sessionStorage.getItem('mallId');",  # 从sessionStorage获取
                """
                for (let key in window) {
                    if (key.toLowerCase().includes('mall')) {
                        return window[key];
                    }
                }
                return null;
                """,  # 遍历window对象
                """
                const scripts = document.getElementsByTagName('script');
                for (let script of scripts) {
                    const content = script.textContent;
                    if (content && content.includes('mallId')) {
                        const match = content.match(/mallId['":\s]+([^'"}\s]+)/);
                        if (match) return match[1];
                    }
                }
                return null;
                """  # 从script标签内容中查找
            ]
            
            for script in scripts:
                try:
                    value = self.driver.execute_script(script)
                    if value:
                        print(f"成功获取mallid: {value}")
                        return value
                except Exception as e:
                    continue
                    
            # 如果上述方法都失败，尝试从URL或其他地方获取
            current_url = self.driver.current_url
            print(f"当前URL: {current_url}")
            
            # 尝试打印页面源码中包含mall的部分
            if "mall" in page_source.lower():
                print("页面源码中包含mall相关信息，正在分析...")
                # 尝试找到包含mall的script标签
                scripts = self.driver.find_elements(By.TAG_NAME, "script")
                for script in scripts:
                    try:
                        content = script.get_attribute("textContent")
                        if content and "mall" in content.lower():
                            print("找到包含mall的脚本内容")
                    except:
                        continue
            
            return None
            
        except Exception as e:
            print(f"获取mallid失败: {str(e)}")
            return None
            
    def login(self, username, password):
        """使用Selenium模拟登录"""
        try:
            print("开始登录...")
            # 直接访问登录页面
            self.driver.get(f"{self.base_url}/login")
            print("已打开登录页面")
            time.sleep(2)  # 等待页面完全加载
            
            # 切换到账号登录标签（如果需要）
            try:
                account_login_tab = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[text()='账号登录']"))
                )
                account_login_tab.click()
                print("已切换到账号登录")
                time.sleep(1)
            except Exception as e:
                print("已经在账号登录页面或切换失败")
            
            # 等待并填写用户名
            print("等待用户名输入框...")
            username_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='手机号码']"))
            )
            username_input.clear()
            username_input.send_keys(username)
            print("已输入用户名")
            
            # 填写密码
            print("等待密码输入框...")
            password_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='密码']"))
            )
            password_input.clear()
            password_input.send_keys(password)
            print("已输入密码")
            
            # 查找并点击同意复选框
            print("查找并点击同意复选框...")
            try:
                # 等待复选框可见
                time.sleep(1)
                
                # 首先尝试使用label点击
                try:
                    checkbox_label = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//label[contains(@class, 'CBX_outerWrapper')]"))
                    )
                    checkbox_label.click()
                    print("已点击复选框label")
                except Exception as e:
                    print(f"点击复选框label失败: {str(e)}")
                    
                    # 如果label点击失败，尝试直接点击复选框
                    try:
                        checkbox = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox']"))
                        )
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        print("已通过JavaScript点击复选框")
                    except Exception as e:
                        print(f"JavaScript点击复选框失败: {str(e)}")
                        
                        # 最后尝试使用JavaScript设置复选框状态
                        js_code = """
                        var checkboxes = document.querySelectorAll('input[type="checkbox"]');
                        var found = false;
                        for (var checkbox of checkboxes) {
                            if (!checkbox.checked) {
                                checkbox.checked = true;
                                checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                                found = true;
                            }
                        }
                        return found;
                        """
                        if self.driver.execute_script(js_code):
                            print("已通过JavaScript设置复选框状态")
                        else:
                            print("未找到未选中的复选框")
                
                # 验证复选框是否被选中
                time.sleep(1)
                checkbox_status = self.driver.execute_script("""
                    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
                    for (var checkbox of checkboxes) {
                        if (checkbox.checked) return true;
                    }
                    return false;
                """)
                
                if not checkbox_status:
                    print("警告：复选框可能未被正确选中")
                else:
                    print("确认复选框已被选中")
                
            except Exception as e:
                print(f"处理复选框时出错: {str(e)}")
            
            # 确保等待一下再进行下一步操作
            time.sleep(1)
            
            # 点击登录按钮
            print("点击登录按钮...")
            try:
                login_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'BTN') and .//span[text()='登录']]"))
                )
                login_button.click()
                print("已点击登录按钮")
                
                # 等待并检查验证码输入框
                try:
                    verification_input = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, '验证码')]"))
                    )
                    if verification_input:
                        print("检测到验证码输入框")
                        # 点击获取验证码按钮
                        get_code_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '获取验证码')]"))
                        )
                        get_code_button.click()
                        print("已点击获取验证码按钮")
                        
                        # 等待用户手动输入
                        verification_code = input("请输入收到的验证码: ")
                        verification_input.clear()
                        verification_input.send_keys(verification_code)
                        print("已输入验证码")
                        
                        # 再次点击登录按钮
                        login_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'BTN') and .//span[text()='登录']]"))
                        )
                        login_button.click()
                        print("已再次点击登录按钮")
                except Exception as e:
                    print(f"验证码处理失败: {str(e)}")
            except Exception as e:
                print(f"登录按钮操作失败: {str(e)}")
            
            # 检查是否登录成功
            try:
                time.sleep(4)  # 等待登录请求完成
                current_url = self.driver.current_url
                if "/main/" in current_url or "/settle/site-main" in current_url:
                    print("检测到登录成功，当前URL:", current_url)
                    
                    # 获取所有cookies
                    cookies = self.driver.get_cookies()
                    print(f"获取到 {len(cookies)} 个cookies")
                    
                    # 将cookies添加到requests session中
                    for cookie in cookies:
                        self.session.cookies.set(
                            cookie['name'], 
                            cookie['value'],
                            domain=cookie.get('domain', ''),
                            path=cookie.get('path', '/')
                        )
                    return True
                else:
                    print("登录失败，当前URL:", current_url)
                    return False
            except Exception as e:
                print(f"检查登录状态时出错: {str(e)}")
                return False
            
        except Exception as e:
            print(f"登录失败: {str(e)}")
            # 保存页面源码以便调试
            try:
                with open("error_page.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("已保存错误页面源码到 error_page.html")
            except:
                pass
            return False
