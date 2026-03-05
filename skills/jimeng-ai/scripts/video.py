#!/usr/bin/env python3
"""
即梦AI 视频生成 - 支持文生视频/图生视频
"""

import os
import sys
import json
import argparse
import base64
from volcengine.visual.VisualService import VisualService


def text_to_video(access_key, secret_key, prompt, frames=121, aspect_ratio="16:9", seed=-1):
    """文生视频"""
    
    service = VisualService()
    service.set_ak(access_key)
    service.set_sk(secret_key)
    
    form = {
        'req_key': 'jimeng_t2v_v30',
        'prompt': prompt,
        'seed': seed,
        'frames': frames,
        'aspect_ratio': aspect_ratio
    }
    
    result = service.img2video3d(form)
    return result


def image_to_video(access_key, secret_key, image_path=None, image_url=None, prompt="", frames=121, seed=-1):
    """图生视频（首帧）"""
    
    service = VisualService()
    service.set_ak(access_key)
    service.set_sk(secret_key)
    
    form = {
        'req_key': 'jimeng_i2v_first_v30',
        'prompt': prompt,
        'seed': seed,
        'frames': frames,
    }
    
    # 图片来源：URL 或 Base64
    if image_url:
        form['image_urls'] = [image_url]
    elif image_path:
        # 读取图片并转为base64
        with open(image_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        form['binary_data_base64'] = [img_data]
    
    result = service.img2video3d(form)
    return result


def main():
    parser = argparse.ArgumentParser(description="即梦AI 视频生成")
    parser.add_argument("--mode", choices=["t2v", "i2v"], default="t2v", help="模式: t2v=文生视频, i2v=图生视频")
    parser.add_argument("--prompt", required=True, help="提示词")
    parser.add_argument("--image", help="图片路径 (图生视频模式)")
    parser.add_argument("--image-url", help="图片URL (图生视频模式)")
    parser.add_argument("--frames", type=int, default=121, choices=[121, 241], help="帧数 (121=5秒, 241=10秒)")
    parser.add_argument("--aspect", default="16:9", help="宽高比")
    parser.add_argument("--seed", type=int, default=-1, help="随机种子")
    parser.add_argument("--output", default="/tmp/video.mp4", help="输出路径")
    parser.add_argument("--access-key", default=os.environ.get("VOLCENGINE_ACCESS_KEY"))
    parser.add_argument("--secret-key", default=os.environ.get("VOLCENGINE_SECRET_KEY"))
    
    args = parser.parse_args()
    
    if not args.access_key or not args.secret_key:
        print("错误: 请设置 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY 环境变量")
        sys.exit(1)
    
    try:
        mode_name = "文生视频" if args.mode == "t2v" else "图生视频"
        print(f"🎬 生成{mode_name}: {args.prompt}")
        
        if args.mode == "t2v":
            result = text_to_video(
                args.access_key, args.secret_key,
                args.prompt, args.frames, args.aspect, args.seed
            )
        else:
            result = image_to_video(
                args.access_key, args.secret_key,
                args.image, args.image_url,
                args.prompt, args.frames, args.seed
            )
        
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 解析结果
        if result.get("code") == 10000 and result.get("data"):
            data = result["data"]
            video_urls = data.get("urls", [])
            
            if video_urls:
                video_url = video_urls[0]
                meta = json.loads(data.get("video_meta", ["{}"])[0])
                
                print("\n" + "=" * 50)
                print("✅ 视频生成成功!")
                print("=" * 50)
                print(f"📹 视频URL:")
                print(video_url)
                print("=" * 50)
                print(f"⏱️ 时长: {meta.get('duration', '?')}秒")
                print(f"📐 分辨率: {meta.get('width', '?')}x{meta.get('height', '?')}")
                print(f"💾 大小: {meta.get('size', 0)/1024/1024:.2f} MB")
                print("=" * 50)
                
                # 保存URL到文件
                url_file = os.path.join(os.path.dirname(args.output), "latest_video_url.txt")
                with open(url_file, 'w') as f:
                    f.write(video_url)
                print(f"\n📝 URL已保存到: {url_file}")
            else:
                print("警告: 无视频URL")
        else:
            print(f"❌ 错误: {result.get('message', 'Unknown error')}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
