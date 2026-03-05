#!/usr/bin/env python3
"""
即梦AI 图片生成 - 使用火山引擎 SDK
"""

import os
import sys
import json
import argparse
import base64
from volcengine.ApiInfo import ApiInfo
from volcengine.Credentials import Credentials
from volcengine.base.Service import Service


def generate_image(access_key, secret_key, prompt, model="jimeng-image-4.0",
                   size="1024x1024", num=1):
    """生成图片"""
    
    service = Service(
        service_info=ApiInfo(
            service='visual',
            version='2022-08-31',
            host='visual.volcengineapi.com',
            header={},
            credentials=Credentials(access_key, secret_key, '', 'cn-north-1')
        ),
        api_info={
            'CVMotionPic': ApiInfo(
                method='POST',
                url='/',
                query=['Action', 'Version', 'Service', 'Region', 'Timestamp'],
                body={'ReqData': json.dumps({
                    "model": model,
                    "prompt": prompt,
                    "size": size,
                    "n": num
                })}
            )
        }
    )
    
    # 发送请求
    try:
        response = service.post('CVMotionPic', {}, {})
        return response
    except Exception as e:
        return {"error": str(e)}


def download_image(url, output_path):
    """下载图片"""
    import requests
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"图片已保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="即梦AI 图片生成")
    parser.add_argument("--prompt", required=True, help="英文提示词")
    parser.add_argument("--model", default="jimeng-image-4.0", help="模型版本")
    parser.add_argument("--size", default="1024x1024", help="图片尺寸")
    parser.add_argument("--num", type=int, default=1, help="生成数量")
    parser.add_argument("--output", required=True, help="输出路径")
    parser.add_argument("--access-key", default=os.environ.get("VOLCENGINE_ACCESS_KEY"))
    parser.add_argument("--secret-key", default=os.environ.get("VOLCENGINE_SECRET_KEY"))
    
    args = parser.parse_args()
    
    secret_key = args.secret_key
    if secret_key:
        try:
            secret_key = base64.b64decode(secret_key).decode('utf-8')
            print(f"Secret Key decoded: {secret_key[:10]}...")
        except:
            pass
    
    if not args.access_key or not secret_key:
        print("错误: 缺少 API 凭证")
        sys.exit(1)
    
    try:
        print(f"生成图片: {args.prompt}")
        
        result = generate_image(args.access_key, secret_key, args.prompt, args.model, args.size, args.num)
        
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
