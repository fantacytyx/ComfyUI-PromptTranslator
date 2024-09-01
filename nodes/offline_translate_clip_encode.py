from ..utils import removeLoraText, restoreLoraText, detectAndTranslate, log

LANGUAGES = {
    '中文': 'zh',
    '日本語': 'ja',
    'Русский': 'ru' 
}


class OfflineTranslateClipEncode:
    """
    将提示词翻译成英文的 CLIP 编码节点。

    该节点接收一个 CLIP 模型作为输入，并包含一个文本区域，用于输入提示词文本。
    如果输入的不是英文，将使用 `transformers` 库将其翻译成英文。
    此节点使用 ComfyUI 的 CLIP 文本编码方式对文本进行编码，输出 CONDITIONING 数据以及翻译后的提示词文本，可方便的与 KSampler 等节点连接。
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
                "remove_lora_text": ("BOOLEAN", {"default": True}),
            },
        }

    # 定义节点的输出类型
    RETURN_TYPES = ("CONDITIONING", "STRING",)  # 输出 CONDITIONING 类型数据
    FUNCTION = "encode"  # 节点的入口函数为 "encode"

    CATEGORY = "PromptTranslator"  # 节点所属类别

    def encode(self, clip, text, from_lang, remove_lora_text):
        """
        对输入文本进行翻译然后进行 CLIP 编码。

        参数：
            clip: CLIP 模型。
            text (str): 待编码的文本。
            from_lang (str): 待编码文本的源语言。
            remove_lora_text (bool): 移除待编码文本中的rola字符串。

        返回值：
            CONDITIONING: 编码后的 CONDITIONING 数据。
        """
        
        noLoraText, matches = removeLoraText(text)
        _from_lang = 'auto'
        if from_lang in LANGUAGES:
            _from_lang = LANGUAGES[from_lang]
            
        # 如果非英文，则将其翻译成英文。必须指定 from_lang 参数，否则翻译无效
        translated_text = detectAndTranslate(noLoraText, _from_lang)
        log(f"翻译结果：{translated_text}")  # 打印翻译结果到控制台

        # 执行还原
        text = restoreLoraText(translated_text, matches, remove_lora_text)  # 将翻译后的文本赋给 text 变量，用于后续的 CLIP 编码

        # 进行 CLIP 文本编码
        tokens = clip.tokenize(text)
        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)

        return ([[cond, {"pooled_output": pooled}]], text,)


# 导出的节点及其名称
# 注意：key要全局唯一
NODE_CLASS_MAPPINGS = {
    "offline_translate_clip_encode": OfflineTranslateClipEncode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "offline_translate_clip_encode": "CLIP Encode (Offline prompt translation)",
}
