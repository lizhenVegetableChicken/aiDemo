from PIL import Image, ImageDraw, ImageFont
import os

def create_template():
    # 创建空白图片（A4大小，300DPI）
    width = 2480  # 8.27 inches * 300 DPI
    height = 3508  # 11.69 inches * 300 DPI
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # 加载字体（使用默认字体，实际使用时需要指定正确的字体文件）
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 绘制EC REP框
    box_left = 100
    box_top = 100
    box_width = 200
    box_height = 100
    draw.rectangle([box_left, box_top, box_left + box_width, box_top + box_height], outline='black', width=2)
    draw.line([box_left + box_width//2, box_top, box_left + box_width//2, box_top + box_height], fill='black', width=2)
    draw.text((box_left + 20, box_top + 30), "EC", font=font, fill='black')
    draw.text((box_left + box_width//2 + 20, box_top + 30), "REP", font=font, fill='black')

    # 绘制公司信息
    company_info_left = box_left + box_width + 50
    draw.text((company_info_left, box_top), "Name: Apex CE Specialists GmbH", font=font, fill='black')
    draw.text((company_info_left, box_top + 70), "Address:Grafenberger Allee 277,40237 Düsseldorf,DE", font=font_small, fill='black')
    draw.text((company_info_left, box_top + 140), "Email: info@apex-ce.com", font=font, fill='black')

    # 留出条形码区域（红框1）
    barcode_top = box_top + 250
    draw.rectangle([100, barcode_top, width-100, barcode_top + 200], outline='red', width=2)

    # 绘制制造商信息
    manufacturer_top = barcode_top + 250
    draw.text((100, manufacturer_top), "Manufacturer: Shenzhenshixingchenkejimaoyi Co., Ltd.", font=font, fill='black')
    draw.text((100, manufacturer_top + 70), "Manufacturer Address: 101, Building 12, Xianglong Garden,", font=font, fill='black')
    draw.text((100, manufacturer_top + 140), "Bantian Street, Longgang District, Shenzhen City,", font=font, fill='black')
    draw.text((100, manufacturer_top + 210), "Guangdong Province,China", font=font, fill='black')
    draw.text((100, manufacturer_top + 280), "Manufacturer Email: isa@sparkx.top", font=font, fill='black')
    draw.text((100, manufacturer_top + 350), "Batch Code:", font=font, fill='black')

    # 留出底部回收标志区域（红框2）
    recycling_top = height - 400
    draw.rectangle([100, recycling_top, width-100, recycling_top + 200], outline='red', width=2)

    # 保存模板
    template_path = os.path.join(os.path.dirname(__file__), "template.png")
    image.save(template_path, "PNG", dpi=(300, 300))
    print(f"模板已创建: {template_path}")

if __name__ == "__main__":
    create_template() 