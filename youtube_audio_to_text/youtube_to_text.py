import os
from youtube_audio_downloader import video_to_audio, get_chapters
from audio_to_text import AudioTranscriber

class YoutubeToText:
    def __init__(self):
        """初始化 YouTube 转文字工具"""
        # 从环境变量获取 API 密钥
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("请设置环境变量 OPENAI_API_KEY")
            
        self.audio_dir = "./youtube_audio_to_text/audio"
        self.txt_dir = "./youtube_audio_to_text/txt"
        
        # 确保目录存在
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.txt_dir, exist_ok=True)
        
        print("\n正在初始化...")
        print("注意：由于无法使用GPU加速，转录过程将在CPU上运行，可能需要一些时间")
        # 使用 medium 模型以提高准确度
        self.transcriber = AudioTranscriber(model_size="medium", openai_api_key=self.openai_api_key)

    def process(self, video_id, title, chapter_index=None):
        """
        处理YouTube视频
        :param video_id: YouTube视频ID
        :param title: 输出文件标题
        :param chapter_index: 要下载的章节索引（从1开始），None表示下载整个视频
        :return: 是否成功
        """
        try:
            # 构建文件路径
            audio_path = os.path.join(self.audio_dir, f"{title}.mp3")
            
            # 下载并转换为音频
            print(f"\n[1/2] 正在下载视频并提取音频: {video_id}")
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            if not video_to_audio(video_url, audio_path, chapter_index):
                raise Exception("音频提取失败")
            
            # 转录音频为文字
            print(f"\n[2/2] 正在转录音频为文字...")
            self.transcriber.transcribe_audio(audio_path)
            
            origin_txt_path = os.path.join(self.audio_dir, f'{title}_transcript.txt')
            new_txt_path = os.path.join(self.txt_dir, f'{title}_transcript.txt')
            os.path.move(origin_txt_path, new_txt_path)

            print(f"\n处理完成！")
            print(f"音频文件：{audio_path}")
            print(f"文本文件：{new_txt_path}")
            return True
            
        except Exception as e:
            print(f"处理过程中出错: {str(e)}")
            return False

def main():
    print("欢迎使用 YouTube 视频转文字工具！")
    print("注意：转录过程在CPU上可能需要较长时间，请耐心等待。")
    print("请输入视频信息：")
    
    while True:
        try:
            # 获取用户输入
            video_id = input("\n请输入 YouTube 视频ID（例如：wA4mi5004M4）: ").strip()
            if not video_id:
                print("视频ID不能为空！")
                continue
            
            # 获取视频章节信息
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            chapters = get_chapters(video_url)
            
            # 让用户选择是否下载特定章节
            chapter_index = None
            if chapters:
                try:
                    choice = input("\n请输入要下载的章节编号（输入0下载整个视频）: ").strip()
                    if choice and choice != '0':
                        chapter_index = int(choice)
                except ValueError:
                    print("无效的输入，将下载整个视频")
            
            # 获取标题
            title = input("请输入输出文件标题: ").strip()
            if not title:
                print("标题不能为空！")
                continue
            
            print("\n提示：")
            print("1. 模型加载可能需要几分钟时间")
            print("2. 转录过程在CPU上可能需要10-30分钟")
            print("3. 请不要关闭程序，等待处理完成\n")
            
            # 创建处理器并执行
            processor = YoutubeToText()
            if processor.process(video_id, title, chapter_index):
                # 询问是否继续
                choice = input("\n是否继续处理其他视频？(y/n): ").strip().lower()
                if choice != 'y':
                    break
            else:
                print("\n处理失败，请重试。")
                
        except KeyboardInterrupt:
            print("\n\n程序已退出。")
            break
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            print("请重试。")

if __name__ == "__main__":
    main() 