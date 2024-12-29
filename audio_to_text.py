import whisper
from pydub import AudioSegment
import os

class AudioTranscriber:
    def __init__(self, model_size="medium"):
        """
        初始化转录器
        :param model_size: 模型大小，可选 "tiny", "base", "small", "medium", "large"
        """
        print(f"正在加载 Whisper {model_size} 模型...")
        self.model = whisper.load_model(model_size)
    
    def convert_to_wav(self, audio_path):
        """将其他音频格式转换为 WAV 格式"""
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"找不到音频文件：{audio_path}")
                
            print(f"正在转换音频文件：{audio_path}")
            audio_format = audio_path.split('.')[-1].lower()
            
            if audio_format != 'wav':
                audio = AudioSegment.from_file(audio_path)
                wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
                
                # 标准化音频参数
                audio = audio.set_channels(1)
                audio = audio.set_frame_rate(16000)
                audio = audio.set_sample_width(2)
                
                print(f"正在导出WAV文件：{wav_path}")
                audio.export(wav_path, format='wav')
                print(f"WAV文件导出成功：{wav_path}")
                return wav_path
            return audio_path
            
        except Exception as e:
            print(f"转换音频时出错：{str(e)}")
            raise

    def transcribe_audio(self, audio_path, language='Chinese'):
        """
        将音频转换为文字
        :param audio_path: 音频文件路径
        :param language: 音频语言，默认中文
        :return: 转换后的文字
        """
        try:
            print(f"开始转录音频：{audio_path}")
            
            # 使用 Whisper 进行转录
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                verbose=True
            )
            
            return result["text"]
                
        except Exception as e:
            print(f"转录过程中发生错误：{str(e)}")
            return f"处理过程中发生错误：{str(e)}"

def main(audio_path):
    try:
        # 初始化转录器（使用medium模型，可以根据需要调整）
        transcriber = AudioTranscriber(model_size="medium")
        
        print(f"准备处理音频文件：{audio_path}")
        
        # 转换音频为文字
        result = transcriber.transcribe_audio(audio_path)
        
        # 打印结果
        print("\n转换结果：")
        print(result)
        
        # 保存结果到文件
        output_file = audio_path.rsplit('.', 1)[0] + '_transcript.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"\n转换结果已保存到：{output_file}")
        
    except Exception as e:
        print(f"程序执行出错：{str(e)}")

if __name__ == "__main__":
    main("fushouer.mp3")
