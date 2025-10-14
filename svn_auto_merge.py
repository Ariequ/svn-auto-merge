#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SVN自动合并智能体工具
支持基于提交信息的自动合并，集成AI智能分析功能
"""

import os
import sys
import json
import re
import subprocess
import logging
import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# 第三方库
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.logging import RichHandler
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

console = Console()

@dataclass
class CommitInfo:
    """提交信息数据类"""
    revision: str
    author: str
    date: str
    message: str
    files: List[str]

@dataclass
class MergeResult:
    """合并结果数据类"""
    success: bool
    revision: str
    message: str
    conflicts: List[str]
    error: Optional[str] = None

class SVNAgent:
    """SVN自动合并智能体"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化智能体"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.last_checked_revision = self._load_last_revision()
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            console.print(f"[red]错误: 配置文件 {config_path} 不存在[/red]")
            sys.exit(1)
        except json.JSONDecodeError as e:
            console.print(f"[red]错误: 配置文件格式错误 - {e}[/red]")
            sys.exit(1)
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('svn_auto_merge')
        logger.setLevel(logging.INFO)
        
        # 创建日志目录
        log_dir = Path(self.config.get('log_file', 'logs/merge.log')).parent
        log_dir.mkdir(exist_ok=True)
        
        # 文件处理器
        file_handler = logging.FileHandler(
            self.config.get('log_file', 'logs/merge.log'),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = RichHandler(console=console, show_time=True)
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_last_revision(self) -> str:
        """加载上次检查的版本号"""
        state_file = Path("logs/last_revision.txt")
        if state_file.exists():
            try:
                return state_file.read_text(encoding='utf-8').strip()
            except:
                return "0"
        return "0"
    
    def _save_last_revision(self, revision: str):
        """保存最后检查的版本号"""
        state_file = Path("logs/last_revision.txt")
        state_file.parent.mkdir(exist_ok=True)
        state_file.write_text(revision, encoding='utf-8')
    
    def check_commit_message(self, message: str) -> Tuple[bool, Dict[str, str]]:
        """检查提交信息是否匹配规则"""
        patterns = self.config.get('match_patterns', {})
        matches = {}
        
        for key, pattern in patterns.items():
            match = re.search(pattern, message)
            if match:
                matches[key] = match.group(1) if match.groups() else match.group(0)
        
        # 必须同时满足所有条件
        required_keys = set(patterns.keys())
        found_keys = set(matches.keys())
        
        return required_keys.issubset(found_keys), matches
    
    def interactive_mode(self):
        """交互式模式"""
        console.print(Panel.fit(
            "[bold blue]SVN自动合并智能体[/bold blue]\n"
            "支持智能冲突分析和自然语言配置",
            title="欢迎"
        ))
        
        while True:
            console.print("\n[bold]可用命令:[/bold]")
            console.print("1. 检查新提交 (check)")
            console.print("2. 查看配置 (config)")
            console.print("3. 退出 (quit)")
            
            command = Prompt.ask("\n请输入命令", default="check")
            
            if command == "check":
                console.print("[green]检查新提交功能开发中...[/green]")
            elif command == "config":
                self.show_config()
            elif command in ["quit", "exit", "q"]:
                break
            else:
                console.print("[red]未知命令[/red]")
    
    def show_config(self):
        """显示当前配置"""
        table = Table(title="当前配置")
        table.add_column("配置项", style="cyan")
        table.add_column("值", style="magenta")
        
        table.add_row("源分支", self.config.get('source_branch', '未配置'))
        table.add_row("目标分支", self.config.get('target_branch', '未配置'))
        table.add_row("检查间隔", f"{self.config.get('check_interval', 300)}秒")
        table.add_row("AI功能", "启用" if self.config.get('ollama', {}).get('enabled') else "禁用")
        
        console.print(table)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='SVN自动合并智能体工具')
    parser.add_argument('--mode', choices=['interactive', 'schedule', 'hook'], 
                       default='interactive', help='运行模式')
    parser.add_argument('--config', default='config.json', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建智能体实例
    agent = SVNAgent(args.config)
    
    if args.mode == 'interactive':
        agent.interactive_mode()

if __name__ == "__main__":
    main()
