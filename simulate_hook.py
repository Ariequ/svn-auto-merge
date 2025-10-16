#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟SVN Hook系统 - 通过监控SVN日志文件来检测新提交
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

def simulate_hook_system():
    """模拟Hook系统"""
    print("🔧 启动模拟SVN Hook系统...")
    print("=" * 60)
    
    # 读取配置文件
    try:
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        source_branch = config.get('source_branch')
        match_patterns = config.get('match_patterns', {})
        
        if not source_branch:
            print("❌ 未配置源分支路径")
            return
        
        print(f"📁 源分支: {source_branch}")
        print(f"📋 匹配规则: {match_patterns}")
        
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return
    
    # 获取初始版本号
    try:
        cmd = ['svn', 'info', source_branch, '--show-item', 'revision']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            last_revision = int(result.stdout.strip())
            print(f"📊 初始版本号: {last_revision}")
        else:
            print(f"❌ 获取版本号失败: {result.stderr}")
            return
    except Exception as e:
        print(f"❌ 获取版本号时出错: {e}")
        return
    
    print("\n🔄 开始监控SVN提交...")
    print("💡 按 Ctrl+C 停止监控")
    
    try:
        while True:
            # 检查新版本
            try:
                cmd = ['svn', 'info', source_branch, '--show-item', 'revision']
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    current_revision = int(result.stdout.strip())
                    
                    if current_revision > last_revision:
                        print(f"\n[cyan]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 发现新提交![/cyan]")
                        print(f"📊 版本变化: {last_revision} -> {current_revision}")
                        
                        # 检查新提交
                        for rev in range(last_revision + 1, current_revision + 1):
                            check_commit(source_branch, rev, match_patterns)
                        
                        last_revision = current_revision
                
            except Exception as e:
                print(f"❌ 检查版本时出错: {e}")
            
            time.sleep(5)  # 每5秒检查一次
            
    except KeyboardInterrupt:
        print("\n[yellow]监控已停止[/yellow]")

def check_commit(source_branch, revision, match_patterns):
    """检查单个提交"""
    try:
        # 获取提交信息
        cmd = ['svn', 'log', source_branch, '-r', str(revision), '--xml']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ 获取提交 {revision} 信息失败")
            return
        
        # 解析提交信息
        import re
        msg_pattern = r'<msg>(.*?)</msg>'
        author_pattern = r'<author>(.*?)</author>'
        
        messages = re.findall(msg_pattern, result.stdout, re.DOTALL)
        authors = re.findall(author_pattern, result.stdout)
        
        if not messages or not authors:
            print(f"❌ 无法解析提交 {revision} 信息")
            return
        
        commit_message = messages[0].strip()
        author = authors[0]
        
        print(f"📝 提交 {revision}: {author} - {commit_message[:50]}...")
        
        # 检查匹配规则
        should_merge = False
        matched_rules = []
        for pattern_name, pattern in match_patterns.items():
            if re.search(pattern, commit_message, re.IGNORECASE):
                should_merge = True
                matched_rules.append(pattern_name)
        
        if should_merge:
            print(f"✅ 提交 {revision} 匹配规则: {matched_rules}")
            print(f"🎯 触发自动合并...")
            
            # 创建合并请求
            create_merge_request(revision, author, commit_message)
        else:
            print(f"❌ 提交 {revision} 不匹配任何规则")
            
    except Exception as e:
        print(f"❌ 检查提交 {revision} 时出错: {e}")

def create_merge_request(revision, author, commit_message):
    """创建合并请求"""
    try:
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
        
        print(f"📄 合并请求已保存: 版本 {revision}")
        
        # 创建信号文件
        signal_file = Path("hook_signal.txt")
        signal_file.write_text(str(time.time()), encoding='utf-8')
        print(f"📡 信号已发送")
        
    except Exception as e:
        print(f"❌ 创建合并请求失败: {e}")

def main():
    """主函数"""
    simulate_hook_system()

if __name__ == "__main__":
    main()
