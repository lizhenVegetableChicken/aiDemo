from PIL import Image
import fitz  # PyMuPDF
import os
from datetime import datetime
import re
import tempfile

class LabelGenerator:
    def __init__(self):
        self.barcodes_dir = "barcodes"
        self.output_dir = "labels"
        self.temp_dir = tempfile.mkdtemp()  # 创建临时目录
        self.template_path = os.path.join(os.path.dirname(__file__), "template.png")
        
        print(f"模板文件路径: {self.template_path}")
        print(f"临时文件目录: {self.temp_dir}")
        
        self.setup_dirs()

    def setup_dirs(self):
        """创建输出目录"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if not os.path.exists(self.barcodes_dir):
            os.makedirs(self.barcodes_dir)

    def convert_pdf_to_image(self, pdf_path):
        """将PDF转换为图片"""
        try:
            # 打开源PDF
            doc = fitz.open(pdf_path)
            page = doc[0]
            
            # 将PDF页面转换为图片，使用RGB模式，增加分辨率
            pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), alpha=False)  # 4x缩放以获得更好的质量
            image_path = os.path.join(self.temp_dir, f"temp_sku_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            pix.save(image_path)
            
            # 打开保存的图片并确保背景是白色
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 创建一个白色背景
            white_bg = Image.new('RGB', img.size, 'white')
            white_bg.paste(img, mask=None)
            
            # 裁剪掉多余的空白边距
            bbox = white_bg.getbbox()  # 获取非空白区域
            if bbox:
                white_bg = white_bg.crop(bbox)
            
            white_bg.save(image_path, quality=100)
            
            doc.close()
            return image_path
            
        except Exception as e:
            print(f"转换PDF时出错: {str(e)}")
            if 'doc' in locals():
                doc.close()
            return None

    def merge_images(self, template_path, sku_image_path, output_path):
        """合并图片"""
        try:
            # 打开模板图片
            template = Image.open(template_path)
            if template.mode != 'RGB':
                template = template.convert('RGB')
            template_width, template_height = template.size
            print(f"模板图片尺寸: {template.size}")
            
            # 打开SKU图片
            sku_image = Image.open(sku_image_path)
            if sku_image.mode != 'RGB':
                sku_image = sku_image.convert('RGB')
            
            # 定义SKU区域的位置和大小
            # 调整这些值以更好地适应条形码
            sku_box = (30, 165, 1250, 435)  # 左、上、右、下
            
            # 调整SKU图片大小以适应目标区域，保持宽高比
            target_width = sku_box[2] - sku_box[0]
            target_height = sku_box[3] - sku_box[1]
            
            # 计算缩放比例
            width_ratio = target_width / sku_image.width
            height_ratio = target_height / sku_image.height
            ratio = min(width_ratio, height_ratio)
            print(f"原始宽度: {sku_image.width}")
            print(f"原始高度: {sku_image.height}")
            print(f"缩放比例: {ratio}")
            
            new_width = int(sku_image.width * ratio)
            new_height = int(sku_image.height * ratio)
            
            # 调整大小
            sku_image = sku_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 计算居中位置
            paste_x = sku_box[0] + (target_width - new_width) // 2
            paste_y = sku_box[1] + (target_height - new_height) // 2
            
            # 将SKU图片粘贴到模板上
            template.paste(sku_image, (paste_x, paste_y))
            
            # 将结果保存为PDF，使用高质量设置
            template.save(output_path, "PDF", resolution=300.0, quality=100)
            
            return True
            
        except Exception as e:
            print(f"合并图片时出错: {str(e)}")
            return False

    def generate_label(self, sku, barcode_pdf_path):
        """为指定的SKU生成标签"""
        try:
            print(f"\n处理 SKU: {sku}")
            print(f"PDF路径: {barcode_pdf_path}")
            
            # 检查模板文件是否存在
            if not os.path.exists(self.template_path):
                print(f"错误：模板图片不存在: {self.template_path}")
                return False
            
            # 将SKU PDF转换为图片
            sku_image = self.convert_pdf_to_image(barcode_pdf_path)
            if not sku_image:
                print(f"无法转换PDF: {barcode_pdf_path}")
                return False

            # 生成输出文件路径
            output_path = os.path.join(self.output_dir, f"label_{sku}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            
            # 合并图片
            success = self.merge_images(self.template_path, sku_image, output_path)
            
            # 清理临时文件
            try:
                if os.path.exists(sku_image):
                    os.remove(sku_image)
            except Exception as e:
                print(f"清理临时文件时出错: {str(e)}")

            if success:
                print(f"成功生成标签: {output_path}")
                return True
            else:
                print("生成标签失败")
                return False

        except Exception as e:
            print(f"生成标签时出错: {str(e)}")
            return False

    def process_all_skus(self):
        """处理所有SKU的标签生成"""
        # 获取所有条形码PDF文件
        barcode_files = [f for f in os.listdir(self.barcodes_dir) if f.endswith('.pdf')]
        print(f"找到 {len(barcode_files)} 个条形码PDF文件")
        
        for barcode_file in barcode_files:
            # 从文件名中提取SKU，只提取数字部分
            sku_match = re.search(r'sku_(\d+)_', barcode_file)
            if sku_match:
                sku = sku_match.group(1)  # 只获取数字部分
                barcode_path = os.path.join(self.barcodes_dir, barcode_file)
                self.generate_label(sku, barcode_path)
            else:
                print(f"无法从文件名中提取SKU: {barcode_file}")

    def __del__(self):
        """清理临时目录"""
        try:
            if hasattr(self, 'temp_dir'):
                import shutil
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"清理临时目录时出错: {str(e)}")

def main():
    generator = LabelGenerator()
    generator.process_all_skus()

if __name__ == "__main__":
    main() 