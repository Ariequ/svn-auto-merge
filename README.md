# SVN自动合并智能体工具

一个基于AI的SVN自动合并工具，支持智能冲突分析和自然语言配置。当A分支的提交信息包含特定标记时，自动合并到B分支。

## 功能特性

- 🤖 **AI智能分析**: 集成Ollama本地大模型，智能分析合并冲突
- 🔄 **自动合并**: 基于提交信息规则自动触发合并
- 🛡️ **冲突处理**: 检测冲突时自动回滚，保护目标分支
- 📊 **实时监控**: 支持SVN钩子和定时任务两种触发方式
- 💬 **交互式界面**: 命令行对话界面，支持自然语言操作
- 📝 **详细日志**: 完整的操作日志和错误追踪
- 🚀 **一键启动**: 跨平台启动脚本，简化部署

## 快速开始

### 1. 环境要求

- Python 3.7+
- SVN客户端
- 8GB+ RAM (使用AI功能时)

### 2. 安装部署

#### 方法一：一键启动（推荐）

**Windows:**
`cmd
# 双击运行
start.bat
`

**macOS/Linux:**
`ash
# 运行启动脚本
./start.sh
`

### 3. 配置设置

编辑 config.json 文件：

`json
{
  "source_branch": "/path/to/branch_A",
  "target_branch": "/path/to/branch_B",
  "match_patterns": {
    "bug": "--bug=(\\w+)",
    "user": "--user=yingjie\\.cui"
  },
  "log_file": "logs/merge.log",
  "check_interval": 300,
  "ollama": {
    "model": "qwen2.5:7b",
    "base_url": "http://localhost:11434",
    "enabled": true
  }
}
`

## 工作原理

### 1. 提交信息匹配

工具会检查A分支的提交信息是否同时包含：
- --bug=* (任意bug编号)
- --user=yingjie.cui

示例匹配的提交信息：
`
修复登录问题 --bug=12345 --user=yingjie.cui
`

### 2. 自动合并流程

1. **监听提交**: 通过钩子或定时任务检测新提交
2. **匹配规则**: 检查提交信息是否符合合并条件
3. **执行合并**: 将匹配的提交合并到B分支
4. **冲突检测**: 自动检测合并冲突
5. **智能分析**: 使用AI分析冲突原因和解决方案
6. **安全回滚**: 有冲突时自动回滚，保护目标分支

## 使用方式

### 交互式模式（默认）

`ash
python svn_auto_merge.py
`

支持的命令：
- check: 检查新提交
- config: 查看配置
- quit: 退出

## 许可证

MIT License

---

如有问题或建议，请提交Issue或联系维护者。
