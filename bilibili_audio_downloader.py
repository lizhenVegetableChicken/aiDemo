from moviepy.video.io.VideoFileClip import VideoFileClip
from pytube import YouTube
from bilibili_api import video, sync
import os
import aiohttp
import asyncio

async def bilibili_to_audio(bv_id, audio_path):
    """
    从Bilibili下载视频并提取音频
    :param bv_id: Bilibili视频的BV号（例如：BV1xx411c7mD）
    :param audio_path: 输出音频文件路径
    :return: bool 表示是否成功
    """
    temp_file = None
    try:
        # 创建视频对象
        v = video.Video(bvid=bv_id)
        
        # 获取视频信息
        video_info = await v.get_info()
        print(f"正在下载: {video_info['title']}")
        
        # 获取视频下载地址
        temp_file = 'temp_bilibili_video.m4s'
        video_data = await v.get_download_url(0)
        
        # 获取音频URL
        audio_url = video_data["dash"]["audio"][0]["baseUrl"]
        
        # 下载音频
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.bilibili.com"
        }
        
        print("下载音频中...")
        async with aiohttp.ClientSession() as session:
            async with session.get(audio_url, headers=headers) as resp:
                if resp.status in [200, 206]:  # 接受206状态码
                    total_size = int(resp.headers.get('content-length', 0))
                    downloaded = 0
                    with open(temp_file, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                # 显示下载进度
                                if total_size > 0:
                                    percent = downloaded * 100 / total_size
                                    print(f"\r下载进度: {percent:.1f}%", end='', flush=True)
                else:
                    raise Exception(f"下载失败，状态码: {resp.status}")
        
        print("\n下载完成，正在保存...")
        
        # 直接将下载的音频文件重命名为目标文件
        if os.path.exists(audio_path):
            os.remove(audio_path)
        os.rename(temp_file, audio_path)
        print(f"音频已保存至: {audio_path}")
        return True
        
    except Exception as e:
        print(f"从Bilibili提取音频时发生错误: {str(e)}")
        return False
        
    finally:
        # 清理资源
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

async def main():
    try:
        # Bilibili示例
        success = await bilibili_to_audio("BV1Lq4y1t7Wb", "bilibili_output.mp3")
        if success:
            print("Bilibili音频提取成功！")
        else:
            print("Bilibili音频提取失败。")
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        # 确保所有异步资源都被正确关闭
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main()) 