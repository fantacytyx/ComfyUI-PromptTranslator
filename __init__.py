from .CJK_clip_encode import CJKCLIPEncode
from .offline_translate_clip_encode import OfflineTranslateClipEncode


# 包含要导出的所有节点及其名称的字典
# 注意：名称应全局唯一
NODE_CLASS_MAPPINGS = {
    "CJK_clip_encode": CJKCLIPEncode,  # 将 CJKCLIPEncode 类注册为名为 "CJK_clip_encode" 的节点
    "offline_translate_clip_encode": OfflineTranslateClipEncode,  # 将 OfflineTranslateClipEncode 类注册为名为 "offline_translate_clip_encode" 的节点
}

# 节点名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "CJK_clip_encode": "CJK CLIP Encode",
    "offline_translate_clip_encode": "CLIP Encode (Offline translate Prompt)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']