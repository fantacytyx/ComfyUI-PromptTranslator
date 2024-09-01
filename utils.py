import os
import re
import langid
from transformers import MarianMTModel, MarianTokenizer

DEBUG_MODE = False  # 是否在控制台打印日志信息

MARIAN_LOADED = {}

MARIAN_LIST = [
    "opus-mt-zh-en",
    "opus-mt-rn-en",
    "opus-mt-taw-en",
    "opus-mt-az-en",
    "opus-mt-ru-en",
    "opus-mt-ja-en"
]


def log(msg):
    if DEBUG_MODE:
        print(f'[PromptTranslator] {msg}')
    return None


ROOT_PATH = os.path.dirname(__file__)


def getExtDir(subpath=None, mkdir=False):
    _dir = ROOT_PATH
    if subpath is not None:
        _dir = os.path.join(_dir, subpath)

    _dir = os.path.abspath(_dir)

    if mkdir and not os.path.exists(_dir):
        os.makedirs(_dir)
    return _dir


def removeLoraText(text):
    matches = []

    # 定义替换函数
    def replace_lora(match):
        matches.append(match.group())
        return f'_${len(matches)}'  # 打印原始文本到控制台
    
    noLoraText = re.sub(r'\<.+?\>', replace_lora, text)
    log(f"匹配到的lora：{matches}")  # 打印原始文本到控制台
    return (noLoraText, matches)


def restoreLoraText(text, matches, remove_lora_text):
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
    log(f"还原lora后的文本：{new_text}")  # 打印还原后的文本到控制台
    return new_text


def is_only_english_content(text):
    """检查文本是否只包含英文字符、数字、空白字符和常见英文标点符号"""
    pattern = re.compile(r'^[a-zA-Z\d\s.,!?\'":()-_\$\[\]\{\}\<\>\/|\\]+$')
    return bool(pattern.match(text))

    
def load_marian_mt(from_lang):
    # 读取 MARIAN_LOADED 缓存
    if from_lang in MARIAN_LOADED:
        log(f"Loaded model: {MARIAN_LOADED[from_lang]['model_path']}")
        return (MARIAN_LOADED[from_lang]['model'], MARIAN_LOADED[from_lang]['tokenizer'])
    
    # 获取模型所在的目录
    models_directory = getExtDir('Helsinki-NLP')
    model_path = os.path.join(models_directory, f'opus-mt-{from_lang}-en')
    
    #  判断model_path文件是否存在
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    tokenizer = MarianTokenizer.from_pretrained(model_path)
    model = MarianMTModel.from_pretrained(model_path)
    
    # 设置MARIAN_LOADED缓存，防止重复加载
    if from_lang not in MARIAN_LOADED:
        MARIAN_LOADED[from_lang] = {
            'model_path': model_path,
            'model': model,
            'tokenizer': tokenizer
        }
    
    log(f"===Loading model: {model_path}")

    return (model, tokenizer)


def translate(noLoraText, from_lang):
    try:
        model, tokenizer = load_marian_mt(from_lang)
        translated = model.generate(**tokenizer(noLoraText, return_tensors="pt", padding=True))
        text = ""
        for t in translated:
            text += tokenizer.decode(t, skip_special_tokens=True) 

        # 正则替换字符串中 :空格数字 的内容 为:数字
        text = re.sub(r'\(.+(:[\s.\d]*)?:[\s.\d]*\)', lambda r: re.sub(r'\s*:\s*([.\d]*)\s*', ':\\1', r.group()), text)
        # 去掉末尾的 ,. 字符
        text = re.sub(r'[,.]$', '', text)
        # 首字母小写
        text = text[0].lower() + text[1:]
        log(f"翻译结果：{text}")  # 打印翻译结果到控制台
    except:
        text = noLoraText
    
    return (text)


SPLIT_CHARS = "',;!?…—。，；！？、"
splitCharRegex = re.compile('\s*[' + SPLIT_CHARS + ']\s*')


def detectAndTranslate(text, from_lang):
    """根据标点符号分割字符串，然后检测语言。第一个非英文的文本语言作为认定语言"""
    splites = re.findall(splitCharRegex, text)
    splited_text = re.split(splitCharRegex, text)
    log(f"找到的分割符：{splites}")  # 打印分割后的文本到控制台
    log(f"分割后的文本：{splited_text}")  # 打印分割后的文本到控制台
    sub_text_after_translate = []
    isAllEnglish = True
    for sub_text in splited_text:
        if len(sub_text) <= 0:
            sub_text_after_translate.append(sub_text)
            continue
        
        sub_text = sub_text.strip()
        
        if is_only_english_content(sub_text):
            sub_text_after_translate.append(sub_text)
            continue
        
        isAllEnglish = False
        detected_lang = langid.classify(sub_text)[0]
        log(f"字符串:{sub_text} 检测为：{detected_lang} ")  # 打印检测结果到控制台
        if detected_lang == from_lang:
            new_text = translate(sub_text, detected_lang)  # 进行翻译
            sub_text_after_translate.append(new_text)
            continue
        
        if from_lang == 'auto' or detected_lang == from_lang:
            new_text = translate(sub_text, detected_lang)  # 进行翻译
            sub_text_after_translate.append(new_text)
            continue
        
        sub_text_after_translate.append(sub_text)
    
    if isAllEnglish: 
        return text
    
    new_text = ''
    for index, sub_text in enumerate(sub_text_after_translate):
        new_text += sub_text
        new_split_text = splites[index] if index < len(splites) else ''
        # 如果new_split_text包含，或。换成,或.
        if '，' in new_split_text:
            new_split_text = new_split_text.replace('，', ',')
        if '。' in new_split_text:
            new_split_text = new_split_text.replace('。', '.')
        if '；' in new_split_text:
            new_split_text = new_split_text.replace('；', ';')
        if '！' in new_split_text:
            new_split_text = new_split_text.replace('！', '!')
        if '？' in new_split_text:
            new_split_text = new_split_text.replace('？', '?')
        if '、' in new_split_text:
            new_split_text = new_split_text.replace('、', ',')
        new_text += new_split_text
    
    log(f"翻译后的文本:{new_text}")  # 打印检测结果到控制台
    return new_text
