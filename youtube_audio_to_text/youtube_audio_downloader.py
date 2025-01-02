import os
from yt_dlp import YoutubeDL

class YoutubeDownloader:
    def __init__(self):
        """初始化下载器"""
        self.base_options = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp_video.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    def get_video_info(self, url):
        """
        获取视频信息，包括章节和时长
        :param url: YouTube视频URL
        :return: 视频信息字典
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', ''),
                    'duration': info.get('duration', 0),
                    'chapters': info.get('chapters', [])
                }
        except Exception as e:
            print(f"获取视频信息时出错: {str(e)}")
            return None

    def print_chapters(self, chapters):
        """
        打印章节信息
        :param chapters: 章节列表
        """
        if chapters:
            print("\n可用章节：")
            for i, chapter in enumerate(chapters, 1):
                start_time = chapter.get('start_time', 0)
                title = chapter.get('title', f'Chapter {i}')
                print(f"{i}. {title} (开始时间: {start_time}秒)")
        else:
            print("该视频没有章节信息")

    def download_full_video(self, url, output_path):
        """
        下载完整视频的音频
        :param url: YouTube视频URL
        :param output_path: 输出音频文件路径
        :return: bool 表示是否成功
        """
        try:
            # 使用基础选项
            ydl_opts = self.base_options.copy()
            
            # 执行下载
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # 重命名音频文件
            if os.path.exists('temp_video.mp3'):
                os.rename('temp_video.mp3', output_path)
                return True
            return False
            
        except Exception as e:
            print(f"下载完整视频时出错: {str(e)}")
            return False

    def download_chapter(self, url, output_path, chapter_index):
        """
        下载指定章节的音频
        :param url: YouTube视频URL
        :param output_path: 输出音频文件路径
        :param chapter_index: 章节索引（从1开始）
        :return: bool 表示是否成功
        """
        try:
            # 获取视频信息
            info = self.get_video_info(url)
            if not info or not info['chapters']:
                print("无法获取章节信息")
                return False
            
            chapters = info['chapters']
            if chapter_index < 1 or chapter_index > len(chapters):
                print("无效的章节索引")
                return False
            
            # 获取章节时间范围
            chapter = chapters[chapter_index - 1]
            start_time = chapter.get('start_time', 0)
            end_time = None
            
            if chapter_index < len(chapters):
                end_time = chapters[chapter_index]['start_time']
            else:
                end_time = info['duration']
            
            # 下载指定时间范围
            return self.download_time_range(url, output_path, start_time, end_time)
            
        except Exception as e:
            print(f"下载章节时出错: {str(e)}")
            return False

    def download_time_range(self, url, output_path, start_time, end_time=None):
        """
        下载指定时间范围的音频
        :param url: YouTube视频URL
        :param output_path: 输出音频文件路径
        :param start_time: 开始时间（秒）
        :param end_time: 结束时间（秒），None表示到视频结束
        :return: bool 表示是否成功
        """
        try:
            # 复制基础选项并添加时间范围参数
            ydl_opts = self.base_options.copy()
            ydl_opts['postprocessor_args'] = [
                '-ss', str(start_time)
            ]
            
            if end_time is not None:
                duration = end_time - start_time
                ydl_opts['postprocessor_args'].extend(['-t', str(duration)])
            
            # 执行下载
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # 重命名音频文件
            if os.path.exists('temp_video.mp3'):
                os.rename('temp_video.mp3', output_path)
                return True
            return False
            
        except Exception as e:
            print(f"下载时间范围时出错: {str(e)}")
            return False

def video_to_audio(url, audio_path, chapter_index=None, start_time=None, end_time=None):
    """
    统一的下载接口，支持完整下载、章节下载和时间范围下载
    :param url: YouTube视频URL
    :param audio_path: 输出音频文件路径
    :param chapter_index: 要下载的章节索引（从1开始），None表示不使用章节下载
    :param start_time: 开始时间（秒），None表示从开始
    :param end_time: 结束时间（秒），None表示到结束
    :return: bool 表示是否成功
    """
    downloader = YoutubeDownloader()
    
    if chapter_index is not None:
        return downloader.download_chapter(url, audio_path, chapter_index)
    elif start_time is not None:
        return downloader.download_time_range(url, audio_path, start_time, end_time)
    else:
        return downloader.download_full_video(url, audio_path)

def get_chapters(url):
    """
    获取视频的章节信息（保持向后兼容）
    :param url: YouTube视频URL
    :return: 章节列表或None
    """
    downloader = YoutubeDownloader()
    info = downloader.get_video_info(url)
    if info and info['chapters']:
        downloader.print_chapters(info['chapters'])
        return info['chapters']
    return None

# 示例用法
if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=Lo5YF3U57T0"
    
    # 创建下载器实例
    downloader = YoutubeDownloader()
    
    # 获取视频信息
    info = downloader.get_video_info(url)
    if info:
        print(f"\n视频标题: {info['title']}")
        print(f"视频时长: {info['duration']}秒")
        downloader.print_chapters(info['chapters'])
        
        print("\n请选择下载方式：")
        print("1. 下载完整视频")
        print("2. 下载指定章节")
        print("3. 下载指定时间范围")
        
        choice = input("\n请输入选择（1-3）: ").strip()
        
        if choice == '1':
            success = downloader.download_full_video(url, "full_video.mp3")
        elif choice == '2':
            chapter_index = int(input("请输入章节编号: "))
            success = downloader.download_chapter(url, "chapter.mp3", chapter_index)
        elif choice == '3':
            start_time = float(input("请输入开始时间（秒）: "))
            end_time = input("请输入结束时间（秒，直接回车表示到结束）: ").strip()
            end_time = float(end_time) if end_time else None
            success = downloader.download_time_range(url, "time_range.mp3", start_time, end_time)
        else:
            print("无效的选择")
            success = False
        
        if success:
            print("音频提取成功！")
        else:
            print("音频提取失败。")