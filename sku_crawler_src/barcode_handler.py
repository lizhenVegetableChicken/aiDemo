from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime

class BarcodeHandler:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.setup_dirs()
        
    def setup_dirs(self):
        """创建保存条码的目录"""
        if not os.path.exists('barcodes'):
            os.makedirs('barcodes')
            
    def get_barcode(self, row):
        """获取并保存条码"""
        try:
            # 使用JavaScript滚动到当前行
            self.driver.execute_script("arguments[0].scrollIntoView(true);", row)
            time.sleep(1)  # 等待滚动完成
            
            # 点击"查看条码"按钮
            view_button = row.find_element(By.XPATH, ".//a[.//span[text()='查看条码']]")
            view_button.click()
            print("已点击查看条码按钮")
            
            # 先检查是否出现翻译弹窗
            try:
                translate_modal = self.driver.find_element(By.XPATH, "//div[contains(@class, 'MDL_header') and text()='商品条码内容翻译']")
                if translate_modal:
                    print("检测到翻译弹窗，准备关闭...")
                    # 点击取消按钮
                    cancel_button = self.driver.find_element(By.XPATH, "//button[.//span[text()='取消']]")
                    cancel_button.click()
                    print("已关闭翻译弹窗")
                    return False
            except:
                pass  # 如果没有找到翻译弹窗，继续正常流程
            
            # 等待弹窗出现
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "label-detail-modal_content__1Ib9A"))
            )
            print("条码弹窗已出现")
            
            # 获取商品信息
            skc = self.get_text_by_label("SKC")
            sku = self.get_text_by_label("SKU")
            print(f"商品信息 - SKC: {skc}, SKU: {sku}")
            
            # 点击"打印条码"按钮
            print("等待保存条码按钮...")
            print_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[.//span[text()='保存条码']]")
                )
            )
            for attempt in range(3):  # 尝试3次
                try:
                    print_button.click()
                    break  # 如果点击成功，跳出循环
                except Exception as e:
                    print(f"点击保存条码按钮失败，重试中... ({attempt + 1}/3)")
                    time.sleep(3)  # 每次重试前等待2秒
            else:
                raise Exception("点击保存条码按钮失败，已重试3次")
            print("已点击保存条码按钮")
            
            # 等待 PDF 生成
            time.sleep(1)  # 等待 PDF 生成和下载
            
            # 重命名最新下载的 PDF 文件
            self.rename_latest_pdf(sku)
            
            # 关闭弹窗
            close_button = self.driver.find_element(
                By.XPATH, "//button[.//span[text()='取消']]"
            )
            close_button.click()
            print("已关闭弹窗")
            
            return True
            
        except Exception as e:
            print(f"获取条码时出错: {str(e)}")
            return False
            
    def get_text_by_label(self, label):
        """根据标签获取文本值"""
        try:
            element = self.driver.find_element(
                By.XPATH,
                f"//div[contains(@class, 'label-value-module__label___') and text()='{label}']/following-sibling::div"
            )
            return element.text.strip()
        except:
            return ""
            
    def rename_latest_pdf(self, sku):
        """重命名最新下载的 PDF 文件"""
        try:
            # 获取下载目录
            download_dir = os.path.expanduser("~/Downloads")
            
            # 获取最新的 PDF 文件
            files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
            if not files:
                print("未找到下载的 PDF 文件")
                return
                
            files.sort(key=lambda x: os.path.getmtime(os.path.join(download_dir, x)))
            latest_pdf = files[-1]
            
            # 构造新文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"sku_{sku}_{timestamp}.pdf"
            
            # 移动并重命名文件
            old_path = os.path.join(download_dir, latest_pdf)
            new_path = os.path.join('barcodes', new_name)
            
            os.rename(old_path, new_path)
            print(f"PDF 已保存: {new_path}")
            
        except Exception as e:
            print(f"重命名文件时出错: {str(e)}")
            
    def process_all_products(self):
        """处理所有商品的条码"""
        
        try:
            page = 1
            while True:
                print(f"\n处理第 {page} 页...")
                # 获取当前页面上所有包含"查看条码"按钮的行
                rows = self.driver.find_elements(
                    By.XPATH,
                    "//td[.//a[.//span[text()='查看条码']]]/.."
                )
                print(f"当前页找到 {len(rows)} 个商品")
                
                if not rows:
                    print("没有找到更多商品，处理完成")
                    break
                
                # 处理当前页的所有商品
                for i, row in enumerate(rows, 1):
                    print(f"\n处理第 {i} 个商品...")
                    success = self.get_barcode(row)
                    time.sleep(1)  # 避免操作太快
                
                # 检查是否有下一页
                try:
                    # 检查下一页按钮是否存在且可点击
                    next_button = self.driver.find_element(
                        By.XPATH,
                        "//li[contains(@class, 'PGT_next') and not(contains(@class, 'PGT_disabled'))]"
                    )
                    # 使用JavaScript滚动到下一页按钮
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    time.sleep(1)  # 等待滚动完成
                    next_button.click()
                    print(f"已切换到第 {page + 1} 页")
                    page += 1
                    time.sleep(2)  # 等待页面加载
                except Exception as e:
                    print("没有下一页或翻页失败，处理完成")
                    break
                
        except Exception as e:
            print(f"处理商品列表时出错: {str(e)}") 