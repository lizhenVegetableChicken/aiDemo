from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

class HttpsCrawler:
    def __init__(self):
        """初始化浏览器"""
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self, username, password):
        """登录系统"""
        try:
            # 访问登录页面
            self.driver.get("https://seller.kuajingmaihuo.com/login")
            
            # 等待并填写用户名
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(username)
            
            # 填写密码
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(password)
            
            # 点击登录按钮
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '登录')]")
            login_button.click()
            
            # 等待登录成功
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"登录失败: {str(e)}")
            return False

    def get_sku_data(self):
        """获取SKU数据"""
        try:
            # 访问SKU页面
            self.driver.get("https://seller.kuajingmaihuo.com/main/product/label")
            
            # 等待数据加载
            time.sleep(3)
            
            # 获取页面内容
            page_source = self.driver.page_source
            
            # 保存页面内容
            with open("page_content.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            
            # 获取网络请求
            logs = self.driver.get_log('performance')
            requests_data = []
            
            for log in logs:
                if 'message' in log:
                    try:
                        message = json.loads(log['message'])
                        if 'message' in message and 'method' in message['message']:
                            if message['message']['method'] == 'Network.responseReceived':
                                request = message['message']['params']
                                requests_data.append(request)
                    except:
                        continue
            
            # 保存请求数据
            with open("requests_data.json", "w", encoding="utf-8") as f:
                json.dump(requests_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"获取数据失败: {str(e)}")
            return False
    
    def close(self):
        """关闭浏览器"""
        self.driver.quit()

def main():
    crawler = HttpsCrawler()
    try:
        # 登录
        username = "18237084494"
        password = "Isa981213"
        
        if crawler.login(username, password):
            print("登录成功")
            
            # 获取SKU数据
            if crawler.get_sku_data():
                print("数据获取成功")
            else:
                print("数据获取失败")
        else:
            print("登录失败")
            
    finally:
        crawler.close()

if __name__ == "__main__":
    main() 