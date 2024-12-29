import speech_recognition as sr
from pydub import AudioSegment
import os

class AudioTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def convert_to_wav(self, audio_path):
        """将其他音频格式转换为 WAV 格式"""
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"找不到音频文件：{audio_path}")
                
            print(f"正在转换音频文件：{audio_path}")
            audio_format = audio_path.split('.')[-1].lower()
            
            if audio_format != 'wav':
                # 加载音频文件
                audio = AudioSegment.from_file(audio_path)
                wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
                
                # 标准化音频参数
                audio = audio.set_channels(1)  # 转换为单声道
                audio = audio.set_frame_rate(16000)  # 设置采样率
                audio = audio.set_sample_width(2)  # 设置位深度为16位
                
                print(f"正在导出WAV文件：{wav_path}")
                # 使用简化的导出参数
                audio.export(
                    wav_path,
                    format='wav',
                    codec='pcm_s16le',  # 使用16位PCM编码
                )
                print(f"WAV文件导出成功：{wav_path}")
                return wav_path
            return audio_path
            
        except Exception as e:
            print(f"转换音频时出错：{str(e)}")
            raise

    def split_audio(self, audio_path, chunk_duration=30000):
        """
        将长音频分割成小段
        :param audio_path: 音频文件路径
        :param chunk_duration: 每段时长（毫秒）
        :return: 临时文件路径列表
        """
        audio = AudioSegment.from_file(audio_path)
        chunks = []
        
        # 将音频分割成30秒的片段
        for i, chunk in enumerate(audio[::chunk_duration]):
            chunk_path = f"temp_chunk_{i}.wav"
            chunk.export(chunk_path, format="wav")
            chunks.append(chunk_path)
        
        return chunks

    def transcribe_audio(self, audio_path, language='zh-CN'):
        """
        将音频转换为文字
        :param audio_path: 音频文件路径
        :param language: 音频语言，默认中文
        :return: 转换后的文字
        """
        try:
            # 确保音频格式为 WAV
            wav_path = self.convert_to_wav(audio_path)
            print(f"使用WAV文件进行识别：{wav_path}")
            
            # 分割音频
            chunks = self.split_audio(wav_path)
            full_text = []
            
            # 逐段识别
            for chunk_path in chunks:
                try:
                    with sr.AudioFile(chunk_path) as source:
                        print(f"正在读取音频段：{chunk_path}")
                        audio_data = self.recognizer.record(source)
                        text = self.recognizer.recognize_google(
                            audio_data,
                            language=language
                        )
                        full_text.append(text)
                except Exception as e:
                    print(f"处理音频段 {chunk_path} 时出错：{str(e)}")
                finally:
                    # 删除临时文件
                    if os.path.exists(chunk_path):
                        os.remove(chunk_path)
            
            return " ".join(full_text)
                
        except sr.UnknownValueError:
            print("Google语音识别服务无法识别音频")
            return "无法识别音频内容"
        except sr.RequestError as e:
            print(f"无法连接到Google语音识别服务：{str(e)}")
            return f"无法连接到语音识别服务；{str(e)}"
        except Exception as e:
            print(f"发生未知错误：{str(e)}")
            return f"处理过程中发生错误：{str(e)}"
        finally:
            # 如果创建了临时 WAV 文件，删除它
            if 'wav_path' in locals() and wav_path != audio_path:
                try:
                    os.remove(wav_path)
                    print(f"已删除临时WAV文件：{wav_path}")
                except Exception as e:
                    print(f"删除临时文件时出错：{str(e)}")

def main(audio_path):
    try:
        transcriber = AudioTranscriber()
        
        # 音频文件路径
        print(f"准备处理音频文件：{audio_path}")
        
        # 设置语言
        language = 'zh-CN'
        
        # 转换音频为文字
        result = transcriber.transcribe_audio(audio_path, language)
        
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
    # main("bilibili_output.mp3") 
    main("fushouer.mp3")
