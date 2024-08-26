from translate import Translator
import langid
import re

LANGUAGES = {
    '中文': 'zh',
    '日文': 'ja',
    '韩文': 'ko' 
}

def _print(*args):
    print(args)
    return

class CJKCLIPEncode:
    """
    用于 CLIP 的中英文编码节点。

    该节点接收一个 CLIP 模型作为输入，并包含一个文本区域，用于输入中文或英文文本。
    如果输入的是中文，将使用 `translate` 库将其翻译成英文，并将翻译结果打印到控制台。
    此节点使用 ComfyUI 的 CLIP 文本编码方式对文本进行编码，输出 CONDITIONING 类型数据，以便于与 KSampler 等节点连接。
    """

    @classmethod
    def INPUT_TYPES(s):
        # 定义节点的输入类型
        return {
            "required": {
                "clip": ("CLIP",),  # CLIP 模型
                "text": ("STRING", {"multiline": True, "default": ""}),  # 多行文本框，默认值为空字符串
                "from_lang": (
                    ["auto"] + list(LANGUAGES.keys()),
                    {"default": "auto"},
                ),
                "remove_lora_text": ([True, False], {"default": True}),
            },
        }

    # 定义节点的输出类型
    RETURN_TYPES = ("CONDITIONING","STRING")  # 输出 CONDITIONING 类型数据
    FUNCTION = "encode"  # 节点的入口函数为 "encode"

    CATEGORY = "PromptTranslator"  # 节点所属类别为 "AI_Boy"


    def encode(self, clip, text, from_lang, remove_lora_text):
        """
        对输入文本进行翻译然后进行 CLIP 编码。

        参数：
            clip: CLIP 模型。
            text (str): 待编码的文本。

        返回值：
            CONDITIONING: 编码后的 CONDITIONING 数据。
        """
        noLoraText, matches = self.remove_lora_text(text)
    
        if from_lang == 'auto':
            detected_lang = 'zh'
            if self.is_only_english_content(noLoraText):
                _print(f"检测到的语言: is_only_english_content")  # 打印检测结果到控制台
                detected_lang = 'en'
            else:
                detected_lang = self.detect_lang(noLoraText)
                _print(f"检测到的语言:{detected_lang}")  # 打印检测结果到控制台
        else:
            try:
                detected_lang = LANGUAGES[from_lang]['key']
                _print(f"指定的语言:{detected_lang}")  # 打印选择结果到控制台
            except:
                detected_lang = 'zh'

        # 文本非英文需要翻译
        if  'en' not in detected_lang:
            # 如果非英文，则将其翻译成英文。必须指定 from_lang 参数，否则翻译无效
            translator = Translator(to_lang="en", from_lang=detected_lang)
            translated_text = translator.translate(noLoraText)  # 进行翻译
            _print(f"翻译结果：{translated_text}")  # 打印翻译结果到控制台
            # 正则替换字符串中 :空格数字 的内容 为:数字
            translated_text = re.sub(r'\(.+(:[\s.\d]*)?:[\s.\d]*\)', lambda r: re.sub(r'\s*:\s*([.\d]*)\s*', ':\\1',r.group()), translated_text)
            # 执行还原
            text = self.restore_lora_text(translated_text, matches, remove_lora_text) # 将翻译后的文本赋给 text 变量，用于后续的 CLIP 编码


        # 进行 CLIP 文本编码
        tokens = clip.tokenize(text)
        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)

        return ([[cond, {"pooled_output": pooled}]], text)
    
    @staticmethod
    def remove_lora_text(text):
        matches = []
        # 定义替换函数
        def replace_lora(match):
            matches.append(match.group())
            return f'_${len(matches)}'# 打印原始文本到控制台
        
        noLoraText = re.sub(r'\<.+?\>', replace_lora, text)
        _print(f"匹配到的lora：{matches}")  # 打印原始文本到控制台
        return (noLoraText, matches)
    
    @staticmethod
    def restore_lora_text(text, matches, remove_lora_text):
        if len(matches) == 0:
            return text

        # 定义还原函数
        def restore_lora(match):
            if remove_lora_text:
                return ''
            else:
                # 使用 group() 方法获取匹配的文本
                matched_text = match.group()
                # 获取匹配文本中的计数器值
                index = int(matched_text[2:])
                # 从原始配置值列表中取出对应的配置值
                return matches[index - 1]
        
        new_text = re.sub(r'_\$\d+?', restore_lora, text)
        new_text = re.sub(r'[\s,]*,\s*', ', ', new_text)
        _print(f"还原lora后的文本：{new_text}")  # 打印还原后的文本到控制台
        return (new_text)
    
    @staticmethod
    def is_only_english_content(text):
        """检查文本是否只包含英文字符、数字、空白字符和常见英文标点符号"""
        pattern = re.compile(r'^[a-zA-Z\d\s.,!?\'":()-_\$\[\]\{\}\<\>\/|\\]+$')
        return bool(pattern.match(text))
    
    @staticmethod
    def detect_lang(text):
        """根据标点符号分割字符串，然后检测语言。第一个非英文的文本语言作为认定语言"""
        split_text = re.split(r'[.,;!?…—。，;！？、]', text)
        _print(f"分割后的文本：{split_text}")  # 打印分割后的文本到控制台
        for sub_text in split_text:
            if len(sub_text) > 0:
                detected_lang = langid.classify(sub_text)[0]
                if detected_lang != 'en':
                    return detected_lang
        return 'en'
