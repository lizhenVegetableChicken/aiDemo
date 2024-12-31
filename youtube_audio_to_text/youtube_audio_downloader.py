import os
from yt_dlp import YoutubeDL

def video_to_audio(url, audio_path):
    try:
        # 下载并提取音频
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp_video.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # 重命名音频文件
        if os.path.exists('temp_video.mp3'):
            os.rename('temp_video.mp3', audio_path)
            
        return True
    
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False

# 示例用法
if __name__ == "__main__":
    success = video_to_audio("https://www.youtube.com/watch?v=0XNvD_CFCj0", "fushouer.mp3")
    if success:
        print("音频提取成功！")
    else:
        print("音频提取失败。")