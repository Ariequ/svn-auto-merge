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
    
    def _load_last_revision(self) -> int:
        """加载上次检查的版本号"""
        state_file = Path("logs/last_revision.txt")
        if state_file.exists():
            try:
                return int(state_file.read_text(encoding='utf-8').strip())
            except:
                return 0
        return 0
    
    def _save_last_revision(self, revision: int):
        """保存最后检查的版本号"""
        state_file = Path("logs/last_revision.txt")
        state_file.parent.mkdir(exist_ok=True)
        state_file.write_text(str(revision), encoding='utf-8')
    
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
    
    def auto_start_mode(self):
        """自动启动模式：立即检查并进入轮询"""
        console.print(Panel(
            "[bold blue]SVN自动合并智能体[/bold blue]\n"
            "自动启动模式 - 只检查启动后的新提交",
            title="自动启动"
        ))
        
        # 记录启动时的版本号
        console.print("[blue]记录启动时的版本号...[/blue]")
        self._record_startup_revision()
        
        # 立即执行一次检查（此时应该没有新提交）
        console.print("[green]正在执行初始检查...[/green]")
        self.check_new_commits()
        
        # 进入轮询模式
        console.print(f"[yellow]进入轮询模式，检查间隔: {self.config.get('check_interval', 300)}秒[/yellow]")
        console.print("[dim]只检查启动后的新提交，按 Ctrl+C 停止轮询[/dim]")
        
        try:
            while True:
                time.sleep(self.config.get('check_interval', 300))
                console.print(f"\n[cyan]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 执行定期检查...[/cyan]")
                self.check_new_commits()
        except KeyboardInterrupt:
            console.print("\n[yellow]轮询已停止[/yellow]")
    
    def hook_mode(self):
        """Hook模式：监听SVN hook信号"""
        console.print(Panel(
            "[bold blue]SVN自动合并智能体[/bold blue]\n"
            "Hook模式 - 实时监听SVN提交",
            title="Hook模式"
        ))
        
        # 记录启动时的版本号
        console.print("[blue]记录启动时的版本号...[/blue]")
        self._record_startup_revision()
        
        # 立即执行一次检查
        console.print("[green]正在执行初始检查...[/green]")
        self.check_new_commits()
        
        # 进入hook监听模式
        console.print("[yellow]进入Hook监听模式[/yellow]")
        console.print("[dim]监听SVN hook信号，按 Ctrl+C 停止监听[/dim]")
        
        signal_file = Path("hook_signal.txt")
        last_signal_time = 0
        
        try:
            while True:
                # 检查hook信号文件
                if signal_file.exists():
                    try:
                        signal_time = float(signal_file.read_text(encoding='utf-8').strip())
                        if signal_time > last_signal_time:
                            last_signal_time = signal_time
                            console.print(f"\n[cyan]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 收到Hook信号[/cyan]")
                            self._process_hook_requests()
                    except:
                        pass
                
                # 检查合并请求文件
                self._check_merge_requests()
                
                time.sleep(1)  # 1秒检查一次
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Hook监听已停止[/yellow]")
    
    def _process_hook_requests(self):
        """处理Hook请求"""
        try:
            request_file = Path("merge_requests.json")
            if not request_file.exists():
                console.print("[dim]没有找到合并请求文件[/dim]")
                return
            
            with open(request_file, 'r', encoding='utf-8') as f:
                requests = json.load(f)
            
            console.print(f"[blue]发现 {len(requests)} 个合并请求[/blue]")
            self.logger.info(f"开始处理 {len(requests)} 个合并请求")
            
            # 处理待处理的请求
            pending_requests = [req for req in requests if req.get('status') == 'pending']
            if not pending_requests:
                console.print("[dim]没有待处理的请求[/dim]")
                return
            
            console.print(f"[yellow]处理 {len(pending_requests)} 个待处理的请求[/yellow]")
            self.logger.info(f"处理 {len(pending_requests)} 个待处理的请求")
            
            for i, request in enumerate(pending_requests, 1):
                console.print(f"\n[cyan]处理请求 {i}/{len(pending_requests)}[/cyan]")
                console.print(f"[dim]版本: {request['revision']}[/dim]")
                console.print(f"[dim]作者: {request['author']}[/dim]")
                console.print(f"[dim]消息: {request['message'][:60]}...[/dim]")
                
                self.logger.info(f"处理Hook请求 {i}/{len(pending_requests)}: 版本 {request['revision']}")
                
                # 创建提交对象
                commit = {
                    'revision': int(request['revision']),
                    'author': request['author'],
                    'message': request['message']
                }
                
                # 执行合并
                if self._should_merge(commit):
                    console.print(f"[yellow]提交 {commit['revision']} 匹配合并规则，开始自动合并...[/yellow]")
                    self.logger.info(f"提交 {commit['revision']} 匹配合并规则，开始自动合并")
                    
                    if self._perform_merge(commit):
                        request['status'] = 'completed'
                        console.print(f"[green]✅ Hook合并成功: 版本 {commit['revision']}[/green]")
                        self.logger.info(f"Hook合并成功: 版本 {commit['revision']}")
                    else:
                        request['status'] = 'failed'
                        console.print(f"[red]❌ Hook合并失败: 版本 {commit['revision']}[/red]")
                        self.logger.error(f"Hook合并失败: 版本 {commit['revision']}")
                else:
                    request['status'] = 'skipped'
                    console.print(f"[dim]提交 {commit['revision']} 不匹配合并规则，跳过[/dim]")
                    self.logger.info(f"提交 {commit['revision']} 不匹配合并规则，跳过")
            
            # 保存更新后的请求
            with open(request_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, indent=2, ensure_ascii=False)
            
            console.print(f"\n[green]✅ 完成处理 {len(pending_requests)} 个请求[/green]")
            self.logger.info(f"完成处理 {len(pending_requests)} 个请求")
                
        except Exception as e:
            console.print(f"[red]处理Hook请求时出错: {e}[/red]")
            self.logger.error(f"处理Hook请求时出错: {e}")
    
    def _check_merge_requests(self):
        """检查合并请求文件"""
        try:
            request_file = Path("merge_requests.json")
            if not request_file.exists():
                return
            
            with open(request_file, 'r', encoding='utf-8') as f:
                requests = json.load(f)
            
            # 检查是否有新的待处理请求
            pending_requests = [r for r in requests if r.get('status') == 'pending']
            if pending_requests:
                console.print(f"[blue]发现 {len(pending_requests)} 个待处理的合并请求[/blue]")
                self._process_hook_requests()
                
        except Exception as e:
            console.print(f"[red]检查合并请求时出错: {e}[/red]")
    
    def schedule_mode(self):
        """定时模式"""
        console.print("[green]定时模式功能开发中...[/green]")
    
    
    def check_new_commits(self):
        """检查新提交"""
        try:
            source_branch = self.config.get('source_branch')
            if not source_branch:
                console.print("[red]错误: 未配置源分支路径[/red]")
                return
            
            # 获取源分支的最新版本号
            latest_revision = self._get_latest_revision(source_branch)
            if not latest_revision:
                console.print("[red]无法获取源分支最新版本[/red]")
                return
            
            console.print(f"[blue]源分支最新版本: {latest_revision}[/blue]")
            console.print(f"[blue]上次检查版本: {self.last_checked_revision}[/blue]")
            
            # 检查是否有新提交
            if latest_revision > self.last_checked_revision:
                console.print(f"[green]发现新提交! 版本 {self.last_checked_revision} -> {latest_revision}[/green]")
                
                # 获取新提交的详细信息
                new_commits = self._get_commits_info(source_branch, self.last_checked_revision, latest_revision)
                console.print(f"[blue]获取到 {len(new_commits)} 个新提交[/blue]")
                
                # 检查提交信息是否匹配规则
                merge_success_count = 0
                for commit in new_commits:
                    if self._should_merge(commit):
                        console.print(f"[yellow]提交 {commit['revision']} 匹配合并规则，开始自动合并...[/yellow]")
                        if self._perform_merge(commit):
                            merge_success_count += 1
                    else:
                        console.print(f"[dim]提交 {commit['revision']} 不匹配合并规则，跳过[/dim]")
                
                # 只有在有成功合并时才更新最后检查的版本号
                if merge_success_count > 0:
                    self._save_last_revision(latest_revision)
                    console.print(f"[green]已更新检查版本为: {latest_revision}[/green]")
                else:
                    console.print(f"[yellow]没有成功合并的提交，保持检查版本: {self.last_checked_revision}[/yellow]")
            else:
                console.print("[dim]没有发现新提交[/dim]")
                
        except Exception as e:
            console.print(f"[red]检查新提交时出错: {e}[/red]")
            import traceback
            console.print(f"[red]详细错误信息: {traceback.format_exc()}[/red]")
            self.logger.error(f"检查新提交时出错: {e}")
            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
    
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
    
    def _get_latest_revision(self, branch_path: str) -> Optional[int]:
        """获取分支的最新版本号"""
        try:
            cmd = ['svn', 'info', branch_path, '--show-item', 'revision']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return int(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError) as e:
            self.logger.error(f"获取最新版本号失败: {e}")
            return None
    
    def _get_commits_info(self, branch_path: str, from_revision: int, to_revision: int) -> List[Dict]:
        """获取指定版本范围内的提交信息"""
        commits = []
        try:
            cmd = ['svn', 'log', branch_path, '-r', f'{from_revision+1}:{to_revision}', '--xml']
            console.print(f"[dim]执行命令: {' '.join(cmd)}[/dim]")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            console.print(f"[dim]SVN log输出: {result.stdout[:200]}...[/dim]")
            
            # 简单的XML解析（实际项目中建议使用xml.etree.ElementTree）
            import re
            revision_pattern = r'<logentry\s+revision="(\d+)"'
            author_pattern = r'<author>(.*?)</author>'
            msg_pattern = r'<msg>(.*?)</msg>'
            
            revisions = re.findall(revision_pattern, result.stdout)
            authors = re.findall(author_pattern, result.stdout)
            messages = re.findall(msg_pattern, result.stdout, re.DOTALL)
            
            console.print(f"[dim]解析结果: {len(revisions)} 个版本, {len(authors)} 个作者, {len(messages)} 个消息[/dim]")
            
            for i, revision in enumerate(revisions):
                commits.append({
                    'revision': int(revision),
                    'author': authors[i] if i < len(authors) else 'unknown',
                    'message': messages[i] if i < len(messages) else ''
                })
                
        except subprocess.CalledProcessError as e:
            console.print(f"[red]获取提交信息失败: {e}[/red]")
            console.print(f"[red]错误输出: {e.stderr if hasattr(e, 'stderr') else 'N/A'}[/red]")
            self.logger.error(f"获取提交信息失败: {e}")
        except Exception as e:
            console.print(f"[red]解析提交信息时出错: {e}[/red]")
            self.logger.error(f"解析提交信息时出错: {e}")
            
        return commits
    
    def _should_merge(self, commit: Dict) -> bool:
        """检查提交是否应该被合并"""
        message = commit.get('message', '')
        author = commit.get('author', '')
        
        # 检查匹配规则
        match_patterns = self.config.get('match_patterns', {})
        
        for pattern_name, pattern in match_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                console.print(f"[green]提交 {commit['revision']} 匹配规则 '{pattern_name}': {pattern}[/green]")
                return True
        
        # 如果没有匹配规则，默认不合并
        return False
    
    def _perform_merge(self, commit: Dict) -> bool:
        """执行自动合并，返回是否成功"""
        try:
            source_branch = self.config.get('source_branch')
            target_branch = self.config.get('target_branch')
            
            if not target_branch:
                console.print("[red]错误: 未配置目标分支路径[/red]")
                self.logger.error("未配置目标分支路径")
                return False
            
            console.print(f"\n[bold cyan]开始合并提交 {commit['revision']}[/bold cyan]")
            console.print(f"[dim]作者: {commit['author']}[/dim]")
            console.print(f"[dim]消息: {commit['message'][:80]}...[/dim]")
            
            # 1. 确认清理目标分支
            console.print(f"\n[blue]步骤1: 确认清理目标分支[/blue]")
            console.print(f"[dim]目标分支: {target_branch}[/dim]")
            self.logger.info(f"步骤1: 确认清理目标分支 {target_branch}")
            
            if not self._confirm_target_branch_cleanup(target_branch):
                console.print("[yellow]用户取消目标分支清理，取消合并[/yellow]")
                self.logger.info("用户取消目标分支清理，取消合并")
                return False
            
            # 2. 清理并更新目标分支
            console.print(f"\n[blue]步骤2: 清理并更新目标分支[/blue]")
            console.print(f"[dim]目标分支: {target_branch}[/dim]")
            self.logger.info(f"步骤2: 开始清理并更新目标分支 {target_branch}")
            
            if not self._clean_and_update_target_branch(target_branch):
                console.print("[red]目标分支清理更新失败，取消合并[/red]")
                self.logger.error("目标分支清理更新失败，取消合并")
                return False
            
            console.print("[green]步骤2完成: 目标分支清理更新成功[/green]")
            self.logger.info("步骤2完成: 目标分支清理更新成功")
            
            # 3. 显示合并确认对话框
            console.print(f"\n[yellow]步骤3: 确认合并提交[/yellow]")
            self.logger.info(f"步骤3: 显示合并确认对话框，提交 {commit['revision']}")
            
            if not self._show_merge_confirmation(commit):
                console.print("[yellow]用户取消合并操作[/yellow]")
                self.logger.info("用户取消合并操作")
                return False
            
            console.print("[green]步骤3完成: 用户确认合并[/green]")
            self.logger.info("步骤3完成: 用户确认合并")
            
            # 4. 执行SVN合并
            console.print(f"\n[yellow]步骤4: 执行SVN合并操作[/yellow]")
            console.print(f"[dim]源分支: {source_branch}[/dim]")
            console.print(f"[dim]目标分支: {target_branch}[/dim]")
            console.print(f"[dim]合并版本: {commit['revision']}[/dim]")
            self.logger.info(f"步骤4: 开始执行SVN合并，版本 {commit['revision']}")
            
            merge_result = self._execute_svn_merge(source_branch, target_branch, commit)
            
            if merge_result['success']:
                console.print("[green]步骤4完成: SVN合并操作成功[/green]")
                self.logger.info("步骤4完成: SVN合并操作成功")
                
                # 5. 生成并提交合并信息
                console.print(f"\n[blue]步骤5: 生成并提交合并信息[/blue]")
                self.logger.info("步骤5: 开始生成并提交合并信息")
                
                self._commit_merge_with_message(source_branch, target_branch, commit, merge_result)
                
                console.print("[green]步骤5完成: 合并信息提交成功[/green]")
                self.logger.info("步骤5完成: 合并信息提交成功")
                
                console.print(f"\n[bold green]✅ 合并成功! 提交 {commit['revision']} 已合并到目标分支[/bold green]")
                self.logger.info(f"自动合并成功: 提交 {commit['revision']} 从 {source_branch} 合并到 {target_branch}")
                
                # 如果有AI功能，可以进行冲突分析
                if self.config.get('ollama', {}).get('enabled'):
                    self._analyze_conflicts(commit)
                
                return True
                    
            else:
                console.print(f"[red]步骤4失败: SVN合并操作失败[/red]")
                console.print(f"[red]错误信息: {merge_result['error']}[/red]")
                self.logger.error(f"步骤4失败: SVN合并操作失败 - {merge_result['error']}")
                
                # 检查是否是冲突问题
                if "conflict" in merge_result['error'].lower():
                    self._show_manual_resolve_prompt(commit, merge_result['error'])
                else:
                    self._show_merge_failure_prompt(commit, merge_result['error'])
                
                return False
                
        except Exception as e:
            console.print(f"[red]执行合并时出错: {e}[/red]")
            self.logger.error(f"执行合并时出错: {e}")
            return False
    
    def _clean_and_update_target_branch(self, target_branch: str) -> bool:
        """清理并更新目标分支"""
        try:
            # 检查是否跳过清理步骤
            skip_cleanup_file = Path("skip_cleanup.json")
            skip_cleanup = False
            if skip_cleanup_file.exists():
                try:
                    with open(skip_cleanup_file, 'r', encoding='utf-8') as f:
                        skip_config = json.load(f)
                        skip_cleanup = skip_config.get('skip_cleanup', False)
                        if skip_cleanup:
                            console.print("[yellow]检测到跳过清理配置，将跳过清理步骤[/yellow]")
                except:
                    pass
            
            # 切换到目标分支目录
            original_dir = os.getcwd()
            os.chdir(target_branch)
            
            console.print(f"[dim]切换到目标分支目录: {target_branch}[/dim]")
            
            if not skip_cleanup:
                # 1. 清理工作副本（移除未版本控制的文件）
                console.print("[dim]清理工作副本...[/dim]")
                cleanup_cmd = ['svn', 'cleanup']
                result = subprocess.run(cleanup_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    console.print(f"[yellow]清理警告: {result.stderr}[/yellow]")
                    
                    # 检查是否是锁定问题
                    if "E155004" in result.stderr and "locked" in result.stderr:
                        console.print("[yellow]检测到SVN锁定问题，尝试自动修复...[/yellow]")
                        if self._fix_svn_locks(target_branch):
                            console.print("[green]SVN锁定问题已自动修复[/green]")
                            # 重新尝试清理
                            result = subprocess.run(cleanup_cmd, capture_output=True, text=True)
                            if result.returncode == 0:
                                console.print("[green]清理成功[/green]")
                            else:
                                console.print(f"[yellow]清理仍然失败: {result.stderr}[/yellow]")
                                skip_cleanup = True
                        else:
                            console.print("[red]自动修复SVN锁定失败[/red]")
                            skip_cleanup = True
                    else:
                        # 如果清理失败，尝试跳过清理继续
                        console.print("[yellow]清理失败，尝试跳过清理步骤继续...[/yellow]")
                        skip_cleanup = True
                
                if not skip_cleanup:
                    # 2. 还原所有本地修改
                    console.print("[dim]还原本地修改...[/dim]")
                    revert_cmd = ['svn', 'revert', '-R', '.']
                    result = subprocess.run(revert_cmd, capture_output=True, text=True)
                    if result.returncode != 0:
                        console.print(f"[yellow]还原警告: {result.stderr}[/yellow]")
            
            # 3. 更新到最新版本
            console.print("[dim]更新到最新版本...[/dim]")
            update_cmd = ['svn', 'update']
            result = subprocess.run(update_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("[green]目标分支更新成功[/green]")
                # 显示更新信息
                if "Updated to revision" in result.stdout:
                    revision_line = [line for line in result.stdout.split('\n') if 'Updated to revision' in line]
                    if revision_line:
                        console.print(f"[blue]{revision_line[0]}[/blue]")
                return True
            else:
                console.print(f"[red]更新失败: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]清理更新目标分支时出错: {e}[/red]")
            return False
        finally:
            # 恢复原始目录
            os.chdir(original_dir)
    
    def _fix_svn_locks(self, target_branch: str) -> bool:
        """自动修复SVN锁定问题"""
        try:
            console.print("[blue]开始自动修复SVN锁定问题...[/blue]")
            
            # 1. 终止SVN进程
            try:
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq svn.exe'], 
                                      capture_output=True, text=True)
                if 'svn.exe' in result.stdout:
                    console.print("[dim]终止SVN进程...[/dim]")
                    subprocess.run(['taskkill', '/IM', 'svn.exe', '/F'], 
                                  capture_output=True, text=True)
                    time.sleep(1)
            except:
                pass
            
            # 2. 删除锁定文件
            lock_files = ['.svn/wc.db-journal', '.svn/lock', '.svn/entries.lock']
            deleted_count = 0
            
            for lock_file in lock_files:
                if os.path.exists(lock_file):
                    try:
                        os.remove(lock_file)
                        deleted_count += 1
                    except:
                        pass
            
            if deleted_count > 0:
                console.print(f"[dim]删除了 {deleted_count} 个锁定文件[/dim]")
            
            # 3. 重新尝试清理
            cleanup_cmd = ['svn', 'cleanup']
            result = subprocess.run(cleanup_cmd, capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            console.print(f"[red]修复SVN锁定时出错: {e}[/red]")
            return False
    
    def _confirm_target_branch_cleanup(self, target_branch: str) -> bool:
        """确认清理目标分支"""
        try:
            # 检查是否在Hook模式下运行
            if self._is_hook_mode():
                console.print("\n" + "="*60)
                console.print("[bold green]Hook模式自动确认清理目标分支[/bold green]")
                console.print("="*60)
                console.print(f"[cyan]目标分支:[/cyan] {target_branch}")
                console.print("[yellow]⚠️  即将执行以下操作:[/yellow]")
                console.print("  • 清理工作副本 (svn cleanup)")
                console.print("  • 还原本地修改 (svn revert -R .)")
                console.print("  • 更新到最新版本 (svn update)")
                console.print("="*60)
                console.print("[green]✅ Hook模式自动确认清理[/green]")
                return True

            # 交互模式下显示确认对话框
            console.print("\n" + "="*60)
            console.print("[bold yellow]清理目标分支确认[/bold yellow]")
            console.print("="*60)
            console.print(f"[cyan]目标分支:[/cyan] {target_branch}")
            console.print("[yellow]⚠️  即将执行以下操作:[/yellow]")
            console.print("  • 清理工作副本 (svn cleanup)")
            console.print("  • 还原本地修改 (svn revert -R .)")
            console.print("  • 更新到最新版本 (svn update)")
            console.print("="*60)
            console.print("[red]⚠️  注意: 这将清除目标分支的所有本地修改![/red]")
            console.print("="*60)

            # 使用rich的Prompt来获取用户确认
            from rich.prompt import Confirm
            confirm = Confirm.ask("是否确认清理目标分支?", default=False)

            return confirm

        except Exception as e:
            console.print(f"[red]显示清理确认对话框时出错: {e}[/red]")
            # 如果确认对话框失败，默认不清理
            return False
    
    def _show_merge_confirmation(self, commit: Dict) -> bool:
        """显示合并确认对话框"""
        try:
            # 检查是否在Hook模式下运行
            if self._is_hook_mode():
                console.print("\n" + "="*60)
                console.print("[bold green]Hook模式自动确认合并[/bold green]")
                console.print("="*60)
                console.print(f"[cyan]提交版本:[/cyan] {commit['revision']}")
                console.print(f"[cyan]作者:[/cyan] {commit['author']}")
                console.print(f"[cyan]提交信息:[/cyan] {commit['message']}")
                console.print("="*60)
                console.print("[green]✅ Hook模式自动确认合并[/green]")
                return True
            
            # 交互模式下显示确认对话框
            console.print("\n" + "="*60)
            console.print("[bold yellow]合并确认[/bold yellow]")
            console.print("="*60)
            console.print(f"[cyan]提交版本:[/cyan] {commit['revision']}")
            console.print(f"[cyan]作者:[/cyan] {commit['author']}")
            console.print(f"[cyan]提交信息:[/cyan] {commit['message']}")
            console.print("="*60)
            
            # 使用rich的Prompt来获取用户确认
            from rich.prompt import Confirm
            confirm = Confirm.ask("是否确认合并此提交?", default=True)
            
            return confirm
            
        except Exception as e:
            console.print(f"[red]显示确认对话框时出错: {e}[/red]")
            # 如果确认对话框失败，默认不合并
            return False
    
    def _is_hook_mode(self) -> bool:
        """检查是否在Hook模式下运行"""
        try:
            # 检查是否有Hook信号文件存在
            signal_file = Path("hook_signal.txt")
            if signal_file.exists():
                return True
            
            # 检查是否有合并请求文件存在
            request_file = Path("merge_requests.json")
            if request_file.exists():
                return True
            
            # 检查命令行参数
            import sys
            if '--hook' in sys.argv:
                return True
            
            return False
        except:
            return False
    
    def _execute_svn_merge(self, source_branch: str, target_branch: str, commit: Dict) -> Dict:
        """执行SVN合并操作"""
        try:
            # 切换到目标分支目录
            original_dir = os.getcwd()
            os.chdir(target_branch)
            
            # 执行SVN合并
            merge_cmd = ['svn', 'merge', source_branch, '-r', f'{commit["revision"]-1}:{commit["revision"]}']
            console.print(f"[dim]执行合并命令: {' '.join(merge_cmd)}[/dim]")
            
            result = subprocess.run(merge_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("[green]SVN合并操作成功[/green]")
                return {
                    'success': True,
                    'output': result.stdout,
                    'merged_files': self._extract_merged_files(result.stdout)
                }
            else:
                console.print(f"[red]SVN合并操作失败: {result.stderr}[/red]")
                return {
                    'success': False,
                    'error': result.stderr
                }
                
        except Exception as e:
            console.print(f"[red]执行SVN合并时出错: {e}[/red]")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # 恢复原始目录
            os.chdir(original_dir)
    
    def _extract_merged_files(self, merge_output: str) -> List[str]:
        """从合并输出中提取合并的文件列表"""
        merged_files = []
        for line in merge_output.split('\n'):
            if line.strip().startswith(('A ', 'M ', 'D ', 'C ', 'G ')):
                # SVN状态码: A=添加, M=修改, D=删除, C=冲突, G=合并
                file_path = line.strip()[2:].strip()
                if file_path:
                    merged_files.append(file_path)
        return merged_files
    
    def _commit_merge_with_message(self, source_branch: str, target_branch: str, commit: Dict, merge_result: Dict):
        """使用标准SVN合并信息格式提交合并"""
        try:
            # 切换到目标分支目录
            original_dir = os.getcwd()
            os.chdir(target_branch)
            
            # 生成标准SVN合并信息
            merge_message = self._generate_merge_message(source_branch, commit, merge_result)
            
            console.print(f"[dim]合并提交信息:[/dim]")
            console.print(f"[dim]{merge_message}[/dim]")
            
            # 执行提交
            commit_cmd = ['svn', 'commit', '-m', merge_message]
            result = subprocess.run(commit_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("[green]合并提交成功[/green]")
                # 显示提交结果
                if "Committed revision" in result.stdout:
                    revision_line = [line for line in result.stdout.split('\n') if 'Committed revision' in line]
                    if revision_line:
                        console.print(f"[blue]{revision_line[0]}[/blue]")
            else:
                console.print(f"[red]合并提交失败: {result.stderr}[/red]")
                
        except Exception as e:
            console.print(f"[red]提交合并时出错: {e}[/red]")
        finally:
            # 恢复原始目录
            os.chdir(original_dir)
    
    def _generate_merge_message(self, source_branch: str, commit: Dict, merge_result: Dict) -> str:
        """生成标准SVN合并信息格式"""
        # 提取源分支名称（从完整路径中）
        branch_name = source_branch.split('\\')[-1] if '\\' in source_branch else source_branch.split('/')[-1]
        
        # 生成合并信息
        merge_message = f"Merged revision(s) {commit['revision']} from branches/{branch_name}:\n"
        merge_message += f"{commit['message']}\n"
        
        # 添加合并的文件信息
        merged_files = merge_result.get('merged_files', [])
        if merged_files:
            merge_message += "\n合并的文件:\n"
            for file_path in merged_files[:10]:  # 最多显示10个文件
                merge_message += f"  {file_path}\n"
            if len(merged_files) > 10:
                merge_message += f"  ... 还有 {len(merged_files) - 10} 个文件\n"
        
        return merge_message.strip()
    
    def _analyze_conflicts(self, commit: Dict):
        """使用AI分析冲突（如果启用）"""
        if not self.config.get('ai_features', {}).get('conflict_analysis'):
            return
            
        console.print("[blue]使用AI分析合并结果...[/blue]")
        # TODO: 实现AI冲突分析功能
        console.print("[dim]AI冲突分析功能开发中...[/dim]")
    
    def _show_manual_resolve_prompt(self, commit: Dict, error_message: str):
        """显示手动解决冲突的提示"""
        console.print("\n" + "="*80)
        console.print(Panel(
            f"[bold red]⚠️  自动合并失败 - 检测到冲突[/bold red]\n\n"
            f"[yellow]提交信息:[/yellow]\n"
            f"版本: {commit['revision']}\n"
            f"作者: {commit['author']}\n"
            f"消息: {commit['message']}\n\n"
            f"[red]错误信息:[/red]\n{error_message}\n\n"
            f"[bold yellow]需要手动解决冲突![/bold yellow]",
            title="合并冲突",
            border_style="red"
        ))
        
        console.print("\n[bold blue]手动解决步骤:[/bold blue]")
        console.print("1. 打开目标分支目录")
        console.print("2. 查找冲突文件（通常包含 <<<<<<< ======= >>>>>>> 标记）")
        console.print("3. 编辑冲突文件，选择要保留的代码")
        console.print("4. 删除冲突标记（<<<<<<< ======= >>>>>>>）")
        console.print("5. 保存文件")
        console.print("6. 运行: svn resolve --accept working <文件名>")
        console.print("7. 运行: svn commit -m '解决合并冲突'")
        
        console.print(f"\n[dim]目标分支: {self.config.get('target_branch')}[/dim]")
        
        # 记录到日志
        self.logger.error(f"合并冲突需要手动解决: 提交 {commit['revision']} - {error_message}")
        
        # 询问用户是否继续
        try:
            from rich.prompt import Confirm
            continue_choice = Confirm.ask("\n是否继续处理其他提交？", default=False)
            if not continue_choice:
                console.print("[yellow]用户选择停止处理[/yellow]")
                return False
        except:
            console.print("[dim]无法获取用户输入，继续处理其他提交...[/dim]")
        
        return True
    
    def _show_merge_failure_prompt(self, commit: Dict, error_message: str):
        """显示合并失败的提示"""
        console.print("\n" + "="*80)
        console.print(Panel(
            f"[bold red]❌ 自动合并失败[/bold red]\n\n"
            f"[yellow]提交信息:[/yellow]\n"
            f"版本: {commit['revision']}\n"
            f"作者: {commit['author']}\n"
            f"消息: {commit['message']}\n\n"
            f"[red]错误信息:[/red]\n{error_message}\n\n"
            f"[bold yellow]请检查错误信息并手动处理![/bold yellow]",
            title="合并失败",
            border_style="red"
        ))
        
        console.print("\n[bold blue]可能的解决方案:[/bold blue]")
        if "locked" in error_message.lower():
            console.print("1. 运行: svn cleanup")
            console.print("2. 检查是否有其他SVN进程在运行")
            console.print("3. 重启计算机释放文件锁")
        elif "permission" in error_message.lower():
            console.print("1. 检查SVN权限")
            console.print("2. 确认有写入权限")
        else:
            console.print("1. 检查SVN状态")
            console.print("2. 查看详细错误信息")
            console.print("3. 手动执行合并操作")
        
        console.print(f"\n[dim]目标分支: {self.config.get('target_branch')}[/dim]")
        
        # 记录到日志
        self.logger.error(f"合并失败: 提交 {commit['revision']} - {error_message}")
        
        # 询问用户是否继续
        try:
            from rich.prompt import Confirm
            continue_choice = Confirm.ask("\n是否继续处理其他提交？", default=True)
            if not continue_choice:
                console.print("[yellow]用户选择停止处理[/yellow]")
                return False
        except:
            console.print("[dim]无法获取用户输入，继续处理其他提交...[/dim]")
        
        return True
    
    def _record_startup_revision(self):
        """记录启动时的版本号"""
        try:
            source_branch = self.config.get('source_branch')
            if not source_branch:
                console.print("[red]错误: 未配置源分支路径[/red]")
                return
            
            # 获取当前最新版本号
            current_revision = self._get_latest_revision(source_branch)
            if current_revision:
                # 如果last_revision.txt不存在，则创建并设置为当前版本
                revision_file = Path("logs/last_revision.txt")
                if not revision_file.exists():
                    revision_file.parent.mkdir(exist_ok=True)
                    revision_file.write_text(str(current_revision), encoding='utf-8')
                    self.last_checked_revision = current_revision
                    console.print(f"[green]已记录启动版本: {current_revision}[/green]")
                    console.print(f"[dim]将只检查版本 {current_revision} 之后的新提交[/dim]")
                else:
                    # 如果文件已存在，读取现有版本
                    existing_revision = int(revision_file.read_text(encoding='utf-8').strip())
                    self.last_checked_revision = existing_revision
                    console.print(f"[blue]使用已存在的检查版本: {existing_revision}[/blue]")
                    console.print(f"[dim]将检查版本 {existing_revision} 之后的新提交[/dim]")
            else:
                console.print("[red]无法获取当前版本号[/red]")
                
        except Exception as e:
            console.print(f"[red]记录启动版本时出错: {e}[/red]")
            self.logger.error(f"记录启动版本时出错: {e}")
    
    def _save_last_revision(self, revision: int):
        """保存最后检查的版本号"""
        try:
            revision_file = Path("logs/last_revision.txt")
            revision_file.parent.mkdir(exist_ok=True)
            revision_file.write_text(str(revision), encoding='utf-8')
            self.last_checked_revision = revision
        except Exception as e:
            self.logger.error(f"保存版本号失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='SVN自动合并智能体工具')
    parser.add_argument('--mode', choices=['interactive', 'schedule', 'hook'], 
                       default='interactive', help='运行模式')
    parser.add_argument('--config', default='config.json', help='配置文件路径')
    parser.add_argument('--auto-start', action='store_true', help='自动启动检查并进入轮询模式')
    parser.add_argument('--hook', action='store_true', help='Hook模式，监听SVN hook信号')
    
    args = parser.parse_args()
    
    # 创建智能体实例
    agent = SVNAgent(args.config)
    
    if args.hook:
        agent.hook_mode()
    elif args.auto_start:
        agent.auto_start_mode()
    elif args.mode == 'interactive':
        agent.interactive_mode()
    elif args.mode == 'schedule':
        agent.schedule_mode()
    elif args.mode == 'hook':
        agent.hook_mode()

if __name__ == "__main__":
    main()
