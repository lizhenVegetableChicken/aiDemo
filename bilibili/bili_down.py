from bilibili_api import video, sync
import aiohttp
import os
import asyncio

async def download_bilibili_video(bv_id, output_path):
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
        video_info = await v.get_info()
        print(f"正在下载: {video_info['title']}")
    
        # 获取视频下载地址
        video_data = await v.get_download_url(0)
        
        # 获取视频和音频的URL
        video_url = video_data["dash"]["video"][0]["baseUrl"]
        audio_url = video_data["dash"]["audio"][0]["baseUrl"]
        
        # 下载视频和音频
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.bilibili.com"
        }
        
        # 临时文件名
        temp_video = "temp_video.m4s"
        temp_audio = "temp_audio.m4s"
        
        # 下载视频部分
        print("下载视频中...")
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url, headers=headers) as resp:
                with open(temp_video, 'wb') as f:
                    f.write(await resp.read())
        
        # 下载音频部分
        print("下载音频中...")
        async with aiohttp.ClientSession() as session:
            async with session.get(audio_url, headers=headers) as resp:
                with open(temp_ayudio, 'wb') as f:
                    f.write(await resp.read())
        
        # 合并视频和音频
        print("合并视频和音频中...")
        os.system(f'ffmpeg -i {temp_video} -i {temp_audio} -c:v copy -c:a aac {output_path}')
        
        # 清理临时文件
        os.remove(temp_video)
        os.remove(temp_audio)
        
        print(f"下载完成！保存至: {output_path}")
        return True
        
    except Exception as e:
        print(f"下载视频时发生错误: {str(e)}")
        # 清理可能存在的临时文件
        for temp_file in [temp_video, temp_audio]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        return False

async def main():
    # 示例用法
    BV_ID = "BV1Lq4y1t7Wb"  # 替换为实际的BV号
    OUTPUT_FILE = "output.mp4"
    
    success = await download_bilibili_video(BV_ID, OUTPUT_FILE)
    if success:
        print("视频下载成功！")
    else:
        print("视频下载失败。")

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())