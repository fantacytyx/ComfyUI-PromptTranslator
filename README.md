
# PromptTranslator
**Add Node / PromptTranslator / offline_translate_clip_encode**

基于翻译模型 [https://huggingface.co/Helsinki-NLP]

该翻译插件不需要联网翻译，只需要下载翻译模型就可以正常工作

只支持翻译成英文，所以请下载 opus-mt-{待翻译语言}-en 模型

模型需要放到 ComfyUI\custom_nodes\ConfyUI-PromptTranslator Helsinki-NLP 目录下


例如：
- [opus-mt-zh-en](https://huggingface.co/Helsinki-NLP/opus-mt-zh-en)
- [opus-mt-ru-en](https://huggingface.co/Helsinki-NLP/opus-mt-ru-en)

需要下载7个文件，分别是：
- config.json
- generation_config.json
- pytorch_model.bin
- source.spm
- target.spm
- tokenizer_config.json
- vocab.json

![example.png](assets/example.png)

# Install
Clone this repository into the custom_nodes directory of ComfyUI, and then restart ComfyUI.


