---
name: jimeng-ai
description: 即梦AI - 字节跳动旗下AI创意平台（视频生成、图片生成）
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "requires": { "env": ["VOLCENGINE_ACCESS_KEY", "VOLCENGINE_SECRET_KEY"] },
        "primaryEnv": "VOLCENGINE_ACCESS_KEY",
        "install": ["pip3 install volcengine"],
      },
  }
---

# 即梦AI (Jimeng AI) - 火山引擎 API

字节跳动旗下 AI 创意平台，支持视频生成等功能。

## 环境变量

```bash
export VOLCENGINE_ACCESS_KEY="your_access_key"
export VOLCENGINE_SECRET_KEY="your_secret_key"  # Base64 encoded
```

> 💡 凭证需要从火山引擎控制台获取

## 功能列表

| 功能 | 模型标识 (req_key) | 说明 |
|------|-------------------|------|
| **文生视频 3.0** | `jimeng_t2v_v30` | 文本生成视频 |
| **图生视频首帧 3.0** | `jimeng_i2v_first_v30` | 图片+文本生成视频 |

## 使用方法

### 1. 文生视频 (5秒)

```bash
python3 ~/.openclaw/workspace/skills/jimeng-ai/scripts/jimeng.py \
  --mode t2v \
  --prompt "A cute lobster wearing sunglasses on the beach" \
  --output /tmp/video.mp4
```

### 2. 文生视频 (10秒)

```bash
python3 ~/.openclaw/workspace/skills/jimeng-ai/scripts/jimeng.py \
  --mode t2v \
  --prompt "A cute lobster wearing sunglasses on the beach" \
  --frames 241 \
  --output /tmp/video.mp4
```

### 3. 图生视频（首帧）

```bash
python3 ~/.openclaw/workspace/skills/jimeng-ai/scripts/jimeng.py \
  --mode i2v \
  --image /path/to/image.jpg \
  --prompt "Make the image move, add waves" \
  --output /tmp/video.mp4
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--mode` | 生成模式: t2v (文生视频), i2v (图生视频) | t2v |
| `--prompt` | 英文提示词 | 必填 |
| `--image` | 图片路径 (i2v模式) | - |
| `--frames` | 帧数: 121 (5秒), 241 (10秒) | 121 |
| `--aspect` | 宽高比: 16:9, 9:16, 1:1 | 16:9 |
| `--seed` | 随机种子，-1 为随机 | -1 |
| `--output` | 输出路径 | 必填 |

## 视频下载说明

✅ **自动下载**: 视频生成完成后自动下载到指定路径

⚠️ **URL 有效期**: 视频 URL 有效期为 **1 小时**，请及时下载

## 错误码

| 错误码 | 说明 |
|--------|------|
| 10000 | 成功 |
| 50411 | 图片审核未通过 |
| 50412 | 文本审核未通过 |
| 50413 | 文本含敏感词 |
| 50516 | 视频审核未通过 |
| 50429 | QPS超限 |
| 50500 | 内部错误 |

## Windows 使用示例

```bash
# 设置凭证
set VOLCENGINE_ACCESS_KEY=your_key
set VOLCENGINE_SECRET_KEY=your_base64_secret

# 生成视频
python scripts/jimeng.py --mode t2v --prompt "..." --output C:\Users\Gyy\Desktop\video.mp4
```
