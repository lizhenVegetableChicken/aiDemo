from bilibili_api import video, sync
import requests
import os

def download_bilibili_video(bv_id, output_path):
    """
    下载Bilibili视频
    :param bv_id: Bilibili视频的BV号（例如：BV1xx411c7mD）
    :param output_path: 输出视频文件路径
    :return: bool 表示是否成功
    """
    try:
        # 创建视频对象
        v = video.Video(bvid=bv_id)
        
        # 获取视频信息
        video_info = sync(v.get_info())
        print(f"正在下载: {video_info['title']}")
        
        # 获取视频下载地址
        video_data = sync(v.get_download_url(0))
        
        # 获取视频URL
        video_url = video_data["dash"]["video"][0]["baseUrl"]
        
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.bilibili.com"
        }
        
        # 下载视频
        print("下载视频中...")
        response = requests.get(video_url, headers=headers, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    f.write(data)
                    done = int(50 * downloaded / total_size)
                    print(f"\r下载进度: [{'=' * done}{' ' * (50-done)}] {downloaded}/{total_size} 字节", 
                          end='', flush=True)
        
        print(f"\n下载完成！保存至: {output_path}")
        return True
        
    except Exception as e:
        print(f"下载视频时发生错误: {str(e)}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

if __name__ == "__main__":
    # 示例用法
    BV_ID = "BV1Lq4y1t7Wb"  # 替换为实际的BV号
    OUTPUT_FILE = "output.mp4"
    
    success = download_bilibili_video(BV_ID, OUTPUT_FILE)
    if success:
        print("视频下载成功！")
    else:
        print("视频下载失败。") 