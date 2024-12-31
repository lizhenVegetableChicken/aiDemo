import whisper
from pydub import AudioSegment
import os
from openai import OpenAI
import time
import math

class AudioTranscriber:
    def __init__(self, model_size="medium", openai_api_key=None):
        """
        初始化转录器
        :param model_size: 模型大小，可选 "tiny", "base", "small", "medium", "large"
        :param openai_api_key: OpenAI API密钥
        """
        print(f"正在加载 Whisper {model_size} 模型...")
        self.model = whisper.load_model(model_size)
        
        # 设置OpenAI客户端
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                print("警告: 未设置OpenAI API密钥，将不会进行智能标点处理")
                self.client = None
            else:
                self.client = OpenAI(api_key=openai_api_key)
    
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

    def split_text(self, text, max_chars=2000):
        """
        将长文本分割成小段
        :param text: 要分割的文本
        :param max_chars: 每段最大字符数
        :return: 分割后的文本段列表
        """
        # 首先按句子分割（用常见的句号、问号、感叹号）
        sentences = []
        current = ""
        for char in text:
            current += char
            if char in '。！？':
                sentences.append(current)
                current = ""
        if current:
            sentences.append(current)

        # 然后将句子组合成段落，确保每段不超过最大长度
        paragraphs = []
        current_paragraph = ""
        
        for sentence in sentences:
            if len(current_paragraph) + len(sentence) <= max_chars:
                current_paragraph += sentence
            else:
                if current_paragraph:
                    paragraphs.append(current_paragraph)
                current_paragraph = sentence
        
        if current_paragraph:
            paragraphs.append(current_paragraph)
            
        return paragraphs

    def add_punctuation(self, text):
        """使用GPT为文本智能添加标点符号"""
        try:
            if not self.client:
                return text
                
            print("正在使用AI添加标点符号...")
            
            # 分割长文本
            text_segments = self.split_text(text)
            formatted_segments = []
            
            # 处理每个文本段
            for i, segment in enumerate(text_segments, 1):
                print(f"\r正在处理第 {i}/{len(text_segments)} 段...", end='', flush=True)
                
                # 构建提示词
                prompt = f"""请为以下文本添加合适的标点符号。要求：
1. 根据语义和语气添加标点符号
2. 保持原文的语气和风格
3. 不要改变原文的内容
4. 只添加常用的中文标点符号（。，！？；：）
5. 注意上下文的连贯性
6. 分段要自然，每段大约200-300字

原文：
{segment}

请直接返回处理后的文本，不要有任何解释。"""

                # 调用GPT API
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个专业的文字编辑，擅长为文本添加合适的标点符号。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # 使用较低的temperature以保持一致性
                    max_tokens=2000
                )
                
                # 获取处理后的文本
                formatted_segment = response.choices[0].message.content.strip()
                formatted_segments.append(formatted_segment)
                
                # 避免触发API限制
                time.sleep(0.5)
            
            print("\n所有文本段处理完成")
            
            # 合并所有处理后的段落
            return "\n\n".join(formatted_segments)
            
        except Exception as e:
            print(f"\nAI处理标点符号时出错：{str(e)}")
            return text  # 如果处理失败，返回原文

    def split_audio(self, audio_path, segment_length=300):
        """
        将音频分割成小段
        :param audio_path: 音频文件路径
        :param segment_length: 每段长度（秒）
        :return: 临时音频文件路径列表
        """
        print("正在分割音频...")
        audio = AudioSegment.from_file(audio_path)
        
        # 计算需要分割的段数
        duration_ms = len(audio)
        segment_length_ms = segment_length * 1000
        num_segments = math.ceil(duration_ms / segment_length_ms)
        
        temp_files = []
        for i in range(num_segments):
            start_ms = i * segment_length_ms
            end_ms = min((i + 1) * segment_length_ms, duration_ms)
            
            # 提取音频段
            segment = audio[start_ms:end_ms]
            
            # 保存临时文件
            temp_file = f"temp_segment_{i}.wav"
            segment.export(temp_file, format="wav")
            temp_files.append(temp_file)
            
        return temp_files

    def transcribe_audio(self, audio_path, language='Chinese'):
        """
        将音频转换为文字
        :param audio_path: 音频文件路径
        :param language: 音频语言，默认中文
        :return: 输出文件路径
        """
        try:
            print(f"开始处理音频：{audio_path}")
            
            # 准备输出文件
            output_file = audio_path.rsplit('.', 1)[0] + '_transcript.txt'
            
            # 分割音频文件
            audio_segments = self.split_audio(audio_path)
            
            try:
                # 逐段处理音频
                for i, segment_path in enumerate(audio_segments, 1):
                    print(f"\n处理第 {i}/{len(audio_segments)} 段音频...")
                    
                    # 转录当前音频段
                    result = self.model.transcribe(
                        segment_path,
                        language=language,
                        task="transcribe",
                        verbose=False
                    )
                    
                    # 处理文本并写入文件
                    if result["text"].strip():
                        # 处理当前段落
                        if self.client:
                            formatted_text = self.add_punctuation_single(result["text"])
                        else:
                            formatted_text = result["text"]
                        
                        # 写入文件
                        mode = 'w' if i == 1 else 'a'
                        with open(output_file, mode, encoding='utf-8') as f:
                            f.write(formatted_text)
                            f.write('\n\n')  # 音频段落之间添加空行
                        
                        print(f"第 {i} 段处理完成并已保存")
                    
            finally:
                # 清理临时文件
                print("清理临时文件...")
                for temp_file in audio_segments:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except Exception as e:
                        print(f"清理临时文件时出错：{str(e)}")
            
            print(f"\n转换结果已保存到：{output_file}")
            return output_file
                
        except Exception as e:
            print(f"转录过程中发生错误：{str(e)}")
            return f"处理过程中发生错误：{str(e)}"

    def add_punctuation_single(self, text):
        """处理单个音频段的文本"""
        try:
            if not self.client:
                return text
                
            # 构建提示词
            prompt = f"""请为以下文本添加合适的标点符号。要求：
1. 根据语义和语气添加标点符号
2. 保持原文的语气和风格
3. 不要改变原文的内容
4. 只添加常用的中文标点符号（。，！？；：）
5. 注意上下文的连贯性

原文：
{text}

请直接返回处理后的文本，不要有任何解释。"""

            # 调用GPT API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的文字编辑，擅长为文本添加合适的标点符号。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # 获取处理后的文本
            formatted_text = response.choices[0].message.content.strip()
            
            # 避免触发API限制
            time.sleep(0.5)
            
            return formatted_text
            
        except Exception as e:
            print(f"\n处理文本时出错：{str(e)}")
            return text  # 如果处理失败，返回原文

def main(audio_path, openai_api_key=None):
    try:
        # 初始化转录器（使用medium模型，可以根据需要调整）
        transcriber = AudioTranscriber(model_size="medium", openai_api_key=openai_api_key)
        
        print(f"准备处理音频文件：{audio_path}")
        
        # 转换音频为文字并保存
        output_file = transcriber.transcribe_audio(audio_path)
        print(f"处理完成，结果已保存到：{output_file}")
        
    except Exception as e:
        print(f"程序执行出错：{str(e)}")

if __name__ == "__main__":
    # 从环境变量获取 API 密钥
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        print("错误：请设置环境变量 OPENAI_API_KEY")
        exit(1)
    main("fushouer.mp3", openai_api_key=OPENAI_API_KEY)