#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SVN Hook脚本 - 检测新提交并触发自动合并
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

def main():
    """SVN Hook主函数"""
    # SVN Hook会通过命令行参数传递信息
    # 参数格式: repository_path revision
    
    if len(sys.argv) < 3:
        print("Usage: svn_hook_script.py <repository_path> <revision>")
        sys.exit(1)
    
    repository_path = sys.argv[1]
    revision = sys.argv[2]
    
    print(f"SVN Hook triggered: repository={repository_path}, revision={revision}")
    
    # 检查是否是portrait分支
    if 'portrait' not in repository_path:
        print("Not portrait branch, skipping...")
        sys.exit(0)
    
    # 读取配置文件
    config_file = Path("config.json")
    if not config_file.exists():
        print("Config file not found")
        sys.exit(1)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Failed to read config: {e}")
        sys.exit(1)
    
    # 检查匹配规则
    match_patterns = config.get('match_patterns', {})
    if not match_patterns:
        print("No match patterns configured")
        sys.exit(0)
    
    # 获取提交信息
    try:
        cmd = ['svn', 'log', repository_path, '-r', revision, '--xml']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to get commit info: {result.stderr}")
            sys.exit(1)
        
        # 解析提交信息
        import re
        msg_pattern = r'<msg>(.*?)</msg>'
        author_pattern = r'<author>(.*?)</author>'
        
        messages = re.findall(msg_pattern, result.stdout, re.DOTALL)
        authors = re.findall(author_pattern, result.stdout)
        
        if not messages or not authors:
            print("Failed to parse commit info")
            sys.exit(1)
        
        commit_message = messages[0].strip()
        author = authors[0]
        
        print(f"Commit {revision}: {author} - {commit_message[:50]}...")
        
        # 检查匹配规则
        should_merge = False
        for pattern_name, pattern in match_patterns.items():
            if re.search(pattern, commit_message, re.IGNORECASE):
                print(f"Matched rule: {pattern_name}")
                should_merge = True
                break
        
        if not should_merge:
            print("Commit does not match merge rules, skipping...")
            sys.exit(0)
        
        # 触发自动合并
        print("Triggering auto merge...")
        trigger_auto_merge(config, revision, author, commit_message)
        
    except Exception as e:
        print(f"Error in hook: {e}")
        sys.exit(1)

def trigger_auto_merge(config, revision, author, commit_message):
    """触发自动合并"""
    try:
        # 创建合并请求文件
        merge_request = {
            "revision": revision,
            "author": author,
            "message": commit_message,
            "timestamp": time.time(),
            "status": "pending"
        }
        
        # 保存到文件
        request_file = Path("merge_requests.json")
        requests = []
        
        if request_file.exists():
            try:
                with open(request_file, 'r', encoding='utf-8') as f:
                    requests = json.load(f)
            except:
                requests = []
        
        requests.append(merge_request)
        
        with open(request_file, 'w', encoding='utf-8') as f:
            json.dump(requests, f, indent=2, ensure_ascii=False)
        
        print(f"Merge request saved for revision {revision}")
        
        # 通知主程序处理合并请求
        notify_main_program()
        
    except Exception as e:
        print(f"Failed to trigger auto merge: {e}")

def notify_main_program():
    """通知主程序处理合并请求"""
    try:
        # 创建一个信号文件
        signal_file = Path("hook_signal.txt")
        signal_file.write_text(str(time.time()), encoding='utf-8')
        print("Signal sent to main program")
    except Exception as e:
        print(f"Failed to notify main program: {e}")

if __name__ == "__main__":
    main()
