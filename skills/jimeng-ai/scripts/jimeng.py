#!/usr/bin/env python3
"""
即梦AI - 火山引擎 Visual API v3 (最终版)
支持: 文生视频3.0、图生视频首帧3.0
"""

import os
import sys
import json
import argparse
import time
import requests
import base64
from volcengine.visual.VisualService import VisualService


def submit_task(service, req_key, prompt, image_path=None, frames=121, seed=-1, aspect_ratio="16:9"):
    """提交异步任务"""
    form = {
        "req_key": req_key,
        "prompt": prompt,
        "frames": frames,
        "seed": seed,
        "aspect_ratio": aspect_ratio
    }
    
    if image_path:
        # 图生视频: 读取图片并转为 base64
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
        form["binary_data_base64"] = [image_base64]
    
    print(f"📤 提交任务: {req_key}")
    print(f"   Prompt: {prompt}")
    if image_path:
        print(f"   Image: {image_path}")
    print(f"   Frames: {frames} ({frames//24}秒)")
    print(f"   Aspect: {aspect_ratio}")
    
    response = service.cv_sync2async_submit_task(form)
    return response


def query_task(service, req_key, task_id):
    """查询任务状态"""
    form = {
        "req_key": req_key,
        "task_id": task_id
    }
    response = service.cv_sync2async_get_result(form)
    return response


def poll_task(service, req_key, task_id, max_wait=300, interval=3):
    """轮询等待任务完成"""
    print(f"⏳ 等待任务完成 (最多 {max_wait}s)...")
    start = time.time()
    last_status = ""
    
    while time.time() - start < max_wait:
        response = query_task(service, req_key, task_id)
        
        if response.get("code") != 10000:
            error_msg = response.get("message", "Unknown error")
            print(f"❌ 任务失败: {error_msg}")
            return None, None
        
        data = response.get("data", {})
        status = data.get("status", "")
        
        if status != last_status:
            print(f"   Status: {status}")
            last_status = status
        
        if status == "done":
            video_url = data.get("video_url")
            # 获取更多元信息
            video_duration = data.get("video_duration", "N/A")
            video_width = data.get("video_width", "N/A")
            video_height = data.get("video_height", "N/A")
            
            if video_url:
                print(f"✅ 任务完成!")
                print(f"   Duration: {video_duration}s")
                print(f"   Resolution: {video_width}x{video_height}")
                return video_url, data
            else:
                message = response.get("message", "")
                print(f"❌ 任务完成但无视频: {message}")
                return None, None
        elif status in ["not_found", "expired"]:
            print(f"❌ 任务不可用: {status}")
            return None, None
        elif status == "generating":
            # 生成中，继续等待
            pass
        
        time.sleep(interval)
    
    print(f"⏰ 等待超时 ({max_wait}s)")
    return None, None


def download_video(url, output_path):
    """下载视频到本地"""
    print(f"📥 下载视频: {output_path}")
    
    try:
        response = requests.get(url, timeout=120, stream=True)
        response.raise_for_status()
        
        total = int(response.headers.get("content-length", 0))
        downloaded = 0
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = downloaded * 100 // total
                        print(f"   进度: {pct}% ({downloaded//1024}KB/{total//1024}KB)", end="\r")
        
        print(f"\n✅ 下载完成: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="即梦AI 视频生成")
    parser.add_argument("--mode", choices=["t2v", "i2v"], default="t2v", 
                        help="模式: t2v=文生视频, i2v=图生视频")
    parser.add_argument("--prompt", required=True, help="提示词")
    parser.add_argument("--image", help="图片路径 (i2v模式必填)")
    parser.add_argument("--frames", type=int, default=121, choices=[121, 241],
                        help="帧数: 121=5秒, 241=10秒 (默认5秒)")
    parser.add_argument("--aspect", default="16:9", choices=["16:9", "9:16", "1:1"],
                        help="宽高比 (默认16:9)")
    parser.add_argument("--seed", type=int, default=-1, help="随机种子 (-1=随机)")
    parser.add_argument("--output", required=True, help="输出路径")
    parser.add_argument("--access-key", default=os.environ.get("VOLCENGINE_ACCESS_KEY"))
    parser.add_argument("--secret-key", default=os.environ.get("VOLCENGINE_SECRET_KEY"))
    parser.add_argument("--no-download", action="store_true", help="只生成，不下载视频")
    
    args = parser.parse_args()
    
    # 凭证检查
    if not args.access_key or not args.secret_key:
        print("❌ 错误: 缺少 API 凭证")
        print("   设置环境变量:")
        print("   export VOLCENGINE_ACCESS_KEY='your_access_key'")
        print("   export VOLCENGINE_SECRET_KEY='your_secret_key'  # Base64 encoded")
        sys.exit(1)
    
    # 模式对应的 req_key
    req_keys = {
        "t2v": "jimeng_t2v_v30",       # 文生视频 3.0
        "i2v": "jimeng_i2v_first_v30"  # 图生视频首帧 3.0
    }
    req_key = req_keys[args.mode]
    
    if args.mode == "i2v" and not args.image:
        print("❌ 错误: i2v 模式需要 --image 参数")
        sys.exit(1)
    
    # 初始化服务
    service = VisualService()
    service.set_ak(args.access_key)
    service.set_sk(args.secret_key)
    
    # 1. 提交任务
    response = submit_task(
        service, req_key, args.prompt, 
        image_path=args.image if args.mode == "i2v" else None,
        frames=args.frames,
        seed=args.seed,
        aspect_ratio=args.aspect
    )
    
    if response.get("code") != 10000:
        print(f"❌ 提交失败: {response.get('message')}")
        sys.exit(1)
    
    task_id = response.get("data", {}).get("task_id")
    if not task_id:
        print(f"❌ 未获取到 task_id: {response}")
        sys.exit(1)
    
    print(f"📋 Task ID: {task_id}")
    
    # 2. 轮询等待
    video_url, video_meta = poll_task(service, req_key, task_id)
    
    if not video_url:
        sys.exit(1)
    
    # 3. 下载视频
    if not args.no_download:
        success = download_video(video_url, args.output)
        if success:
            print(f"\n🎉 完成! 视频保存至: {args.output}")
        else:
            print(f"\n⚠️  视频生成成功，但下载失败")
            print(f"🔗 请手动下载 (有效期1小时): {video_url}")
            # 保存 URL 到文件
            url_file = args.output + ".url.txt"
            with open(url_file, "w") as f:
                f.write(video_url)
            print(f"📝 URL已保存至: {url_file}")
    else:
        print(f"\n🔗 视频链接 (有效期1小时): {video_url}")
        if video_meta:
            print(f"📊 视频信息: {json.dumps(video_meta, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
