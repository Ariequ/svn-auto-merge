#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动Hook系统 - 同时启动模拟Hook监控和Hook模式
"""

import subprocess
import sys
import time
import threading
from pathlib import Path

def start_simulate_hook():
    """启动模拟Hook监控"""
    print("🔄 启动模拟Hook监控...")
    try:
        subprocess.run([sys.executable, 'simulate_hook.py'])
    except Exception as e:
        print(f"❌ 模拟Hook监控启动失败: {e}")

def start_hook_mode():
    """启动Hook模式"""
    print("🔄 启动Hook模式...")
    try:
        subprocess.run([sys.executable, 'svn_auto_merge.py', '--hook'])
    except Exception as e:
        print(f"❌ Hook模式启动失败: {e}")

def main():
    """主函数"""
    print("🚀 启动SVN Hook系统...")
    print("=" * 60)
    
    # 检查必要文件
    required_files = ['simulate_hook.py', 'svn_auto_merge.py', 'config.json']
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少必要文件: {file}")
            return
    
    print("✅ 所有必要文件检查完成")
    
    # 启动模拟Hook监控（后台线程）
    print("\n🔄 启动模拟Hook监控（后台）...")
    hook_thread = threading.Thread(target=start_simulate_hook, daemon=True)
    hook_thread.start()
    
    # 等待一下让模拟Hook启动
    time.sleep(2)
    
    # 启动Hook模式（主线程）
    print("🔄 启动Hook模式（前台）...")
    print("💡 按 Ctrl+C 停止整个系统")
    
    try:
        start_hook_mode()
    except KeyboardInterrupt:
        print("\n🛑 系统已停止")

if __name__ == "__main__":
    main()
