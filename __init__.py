import os
import sys
import subprocess

"""
检测requirements.txt中声明的模块是否已安装，未安装则自动安装
"""
requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
try:
    # 检查pip是否已安装
    subprocess.check_call([sys.executable, "-m", "pip", "--version"])
except subprocess.CalledProcessError:
    print(f"[PromptTranslator] pip is not installed. Attempting to install...")
    try:
        # 尝试安装pip
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--default-pip"])
    except subprocess.CalledProcessError:
        print(f"[PromptTranslator] Failed to install pip. Please install pip manually and try again.")
        sys.exit(1)

print(f"[PromptTranslator] Installing modules from {requirements_file}...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", requirements_file])
    print(f"[PromptTranslator] All modules have been installed successfully.")
except subprocess.CalledProcessError as e:
    print(f"[PromptTranslator] Error installing modules: {e}")
    sys.exit(1)
        



import glob
import importlib
from .utils import log, getExtDir

"""
自动识别要导出的节点及其名称加到字典属性中，以便在UI中显示
"""
NODE_CLASS_MAPPINGS = {} # 注意：key要全局唯一
NODE_DISPLAY_NAME_MAPPINGS = {}

py = getExtDir("nodes")
files = glob.glob(os.path.join(py, "*.py"), recursive=False)
for file in files:
    # 获取文件名称，不含后缀
    module_name = os.path.splitext(os.path.basename(file))[0]    
    try:
        log(f"Importing node: {module_name} ")
        module = importlib.import_module(
            f".nodes.{module_name}", package=__package__ # 注意：这里的__package__是指当前文件所在的包的名称，即__init__.py所在的包的名称
        )
        if hasattr(module, "NODE_CLASS_MAPPINGS") and getattr(module, "NODE_CLASS_MAPPINGS") is not None:
            NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
        if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS") and getattr(module, "NODE_DISPLAY_NAME_MAPPINGS") is not None:
            NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
    except Exception as e:
        log(f"Error loading node: {e}")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]