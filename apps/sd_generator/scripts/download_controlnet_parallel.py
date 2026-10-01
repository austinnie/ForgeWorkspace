import subprocess
import os
import sys
import time

models = ['depth', 'hed', 'normal', 'mlsd', 'scribble']
hf_home = r'E:\SD_OpenVINO\models\controlnet'

print("=" * 60)
print("并行下载 ControlNet 模型 (5个窗口)")
print("=" * 60)
print()

for i, model in enumerate(models, 1):
    print(f"启动窗口 {i} 下载: {model}")
    
    cmd = f'set HF_HOME={hf_home} && set HF_XET_HIGH_PERFORMANCE=1 && python -c "from diffusers import ControlNetModel; ControlNetModel.from_pretrained(\'lllyasviel/sd-controlnet-{model}\'); print(\'✅ {model} 下载完成!\')" && pause'
    
    subprocess.Popen(
        cmd,
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    time.sleep(1)

print()
print("=" * 60)
print("已启动 5 个下载窗口，请分别查看进度")
print("=" * 60)