#!/usr/bin/env python3
"""
即梦AI 智能超清（图像增强）脚本
Usage: python3 enhance.py --input /tmp/image.jpg --output /tmp/hd_image.jpg
"""

import os
import sys
import json
import argparse
import hashlib
import hmac
import base64
import requests
from datetime import datetime

# Volcengine API endpoint
API_HOST = "visual.volcengineapi.com"
API_ACTION = "CVSmartRescale"
API_VERSION = "2022-08-31"


def sign(method, url, params, secret_key):
    """生成火山引擎签名"""
    sorted_params = sorted(params.items())
    string_to_sign = f"{method.upper()}\n{url}\n"
    string_to_sign += "&".join([f"{k}={v}" for k, v in sorted_params])
    signature = hmac.new(
        secret_key.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')


def enhance_image(access_key, secret_key, image_path):
    """智能超清图像增强"""
    
    params = {
        "Action": API_ACTION,
        "Version": API_VERSION,
        "Service": "visual",
        "AccessKeyId": access_key,
        "Timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Region": "cn-north-1",
        "SignatureMethod": "HMAC-SHA256",
    }
    
    # 读取图片并转为 base64
    with open(image_path, 'rb') as f:
        import base64
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # 请求体
    payload = {
        "req_id": f"enhance_{int(time.time())}",
        "function": "super_resolution",
        "image_data": image_data
    }
    
    params["ReqData"] = json.dumps(payload)
    
    # 生成签名
    signature = sign("POST", f"/", params, secret_key)
    params["Signature"] = signature
    
    # 发送请求
    url = f"https://{API_HOST}/"
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, params=params, json=payload, headers=headers)
    result = response.json()
    
    return result


def main():
    parser = argparse.ArgumentParser(description="即梦AI 智能超清")
    parser.add_argument("--input", required=True, help="输入图片路径")
    parser.add_argument("--output", required=True, help="输出图片路径")
    
    # API 凭证
    parser.add_argument("--access-key", default=os.environ.get("VOLCENGINE_ACCESS_KEY"),
                       help="Volcengine Access Key")
    parser.add_argument("--secret-key", default=os.environ.get("VOLCENGINE_SECRET_KEY"),
                       help="Volcengine Secret Key")
    
    args = parser.parse_args()
    
    if not args.access_key or not args.secret_key:
        print("错误: 请设置 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY 环境变量")
        print("或使用 --access-key 和 --secret-key 参数")
        sys.exit(1)
    
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        sys.exit(1)
    
    try:
        print(f"图像增强中...")
        print(f"输入: {args.input}")
        
        result = enhance_image(args.access_key, args.secret_key, args.input)
        
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 解析结果
        if "ReqData" in result:
            req_data = json.loads(result["ReqData"])
            if "data" in req_data and "image_url" in req_data["data"]:
                # 下载增强后的图片
                image_url = req_data["data"]["image_url"]
                response = requests.get(image_url)
                response.raise_for_status()
                
                with open(args.output, 'wb') as f:
                    f.write(response.content)
                
                print(f"增强图片已保存到: {args.output}")
            else:
                print(f"响应中无增强图片数据")
        else:
            print(f"响应格式异常")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import time
    main()
