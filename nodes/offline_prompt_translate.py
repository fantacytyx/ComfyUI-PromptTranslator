from ..utils import removeLoraText, restoreLoraText, detectAndTranslate, log, SPLIT_CHARS

LANGUAGES = {
    '中文': 'zh',
    '日本語': 'ja',
    'Русский': 'ru' 
}


class OfflinePromptTranslate:
    """
    将提示词翻译成英文的文本编辑节点。

    该节点包含一个文本区域，用于输入提示词文本。
    如果输入的不是英文，将使用 `transformers` 库将其翻译成英文。
    此节点输出翻译后的提示词文本。
    """

    @classmethod
    def INPUT_TYPES(s):
        # 定义节点的输入类型
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),  # 多行文本框，默认值为空字符串
                "from_lang": (
                    ["auto"] + list(LANGUAGES.keys()),
                    {"default": "auto"},
                ),
                "remove_lora_text": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "prefix_text": ("STRING", {"forceInput": True, "multiline": True, "default": ""}),  # 多行文本框，默认值为空字符串
            }
        }

    # 定义节点的输出类型
    RETURN_TYPES = ("STRING",)  # 输出 翻译后的提示词文本
    RETURN_NAMES = ("STRING",)
    FUNCTION = "encode"  # 节点的入口函数为 "encode"

    CATEGORY = "PromptTranslator"  # 节点所属类别

    def encode(self, text, from_lang, remove_lora_text, prefix_text = ''):
        """
        对输入文本进行翻译。

        参数：
            text (str): 待翻译的文本。
            from_lang (str): 待翻译文本的源语言。
            remove_lora_text (bool): 移除待翻译文本中的rola字符串。

        返回值：
            STRING: 翻译后的 提示词文本。
        """
        if prefix_text and prefix_text[-1] not in SPLIT_CHARS:  # 如果最后一个字符不是 splitChars 中的字符，则加上一个英文逗号"," 作为分隔符。
            prefix_text += ','
        
        text = prefix_text + text
        
        noLoraText, matches = removeLoraText(text)
        _from_lang = 'auto'
        if from_lang in LANGUAGES:
            _from_lang = LANGUAGES[from_lang]
            
        # 如果非英文，则将其翻译成英文。必须指定 from_lang 参数，否则翻译无效
        translated_text = detectAndTranslate(noLoraText, _from_lang)
        log(f"翻译结果：{translated_text}")  # 打印翻译结果到控制台

        # 执行还原
        text = restoreLoraText(translated_text, matches, remove_lora_text)  # 将翻译后的文本赋给 text 变量

        return (text,)


# 导出的节点及其名称
# 注意：key要全局唯一
NODE_CLASS_MAPPINGS = {
    "offline_prompt_translate": OfflinePromptTranslate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "offline_prompt_translate": "Offline prompt translation",
}
