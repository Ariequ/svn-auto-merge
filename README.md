# SVN自动合并智能体工具

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

一个基于AI的SVN自动合并工具，支持智能冲突分析和自然语言配置。当A分支的提交信息包含特定标记时，自动合并到B分支。

## ✨ 功能特性

- 🤖 **AI智能分析**: 集成Ollama本地大模型，智能分析合并冲突
- 🔄 **自动合并**: 基于提交信息规则自动触发合并
- 🛡️ **冲突处理**: 检测冲突时自动回滚，保护目标分支
- 📊 **实时监控**: 支持SVN钩子和定时任务两种触发方式
- 💬 **交互式界面**: 命令行对话界面，支持自然语言操作
- 📝 **详细日志**: 完整的操作日志和错误追踪
- 🚀 **一键启动**: 跨平台启动脚本，简化部署

## 🚀 快速开始

### 环境要求

- Python 3.7+
- SVN客户端
- 8GB+ RAM (使用AI功能时)

### 安装部署

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

#### 方法二：手动安装

`ash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/svn-auto-merge.git
cd svn-auto-merge

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt
`

### 配置设置

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

## 🎯 工作原理

### 提交信息匹配

工具会检查A分支的提交信息是否同时包含：
- --bug=* (任意bug编号)
- --user=yingjie.cui

示例匹配的提交信息：
`
修复登录问题 --bug=12345 --user=yingjie.cui
`

### 自动合并流程

1. **监听提交**: 通过钩子或定时任务检测新提交
2. **匹配规则**: 检查提交信息是否符合合并条件
3. **执行合并**: 将匹配的提交合并到B分支
4. **冲突检测**: 自动检测合并冲突
5. **智能分析**: 使用AI分析冲突原因和解决方案
6. **安全回滚**: 有冲突时自动回滚，保护目标分支

## 📖 使用方式

### 交互式模式（默认）

`ash
python svn_auto_merge.py
`

支持的命令：
- check: 检查新提交
- config: 查看配置
- merge <revision>: 手动合并指定版本
- logs: 查看日志
- schedule: 启动定时模式
- quit: 退出

### 定时检查模式

`ash
python svn_auto_merge.py --mode schedule
`

### SVN钩子模式

`ash
python svn_auto_merge.py --mode hook --revision 123 --repo-path /path/to/repo
`

## 🤖 AI功能设置

### 安装Ollama

**macOS/Linux:**
`ash
curl -fsSL https://ollama.ai/install.sh | sh
`

**Windows:**
下载安装包：https://ollama.ai/download

### 下载模型

`ash
# 下载Qwen2.5模型
ollama pull qwen2.5:7b

# 启动Ollama服务
ollama serve
`

## 📁 项目结构

`
svn-auto-merge/
├── svn_auto_merge.py          # 主程序
├── config.json                # 配置文件
├── requirements.txt           # 依赖列表
├── start.bat/.sh              # 一键启动脚本
├── hooks/                     # SVN钩子脚本
├── README.md                  # 使用说明
├── PROJECT_SUMMARY.md         # 项目总结
├── GITHUB_SETUP.md           # GitHub设置指南
└── .gitignore                # Git忽略文件
`

## 🔧 部署选项

### 开发环境
- 交互式模式，便于调试和测试
- 手动触发合并操作
- 实时查看日志和状态

### 生产环境
- SVN钩子模式，实时响应提交
- 定时任务模式，定期检查
- 系统服务部署，后台运行

## 🛡️ 安全特性

- 冲突时自动回滚
- 详细的操作日志
- 权限控制和访问限制
- 配置文件验证

## 📊 日志和监控

### 日志文件
- logs/merge.log: 主要操作日志
- logs/hook.log: 钩子执行日志
- logs/last_revision.txt: 最后检查的版本号

## 🐛 故障排除

### 常见问题

1. **Python依赖安装失败**
   `ash
   pip install --upgrade pip
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   `

2. **SVN命令找不到**
   - Windows: 安装TortoiseSVN或VisualSVN
   - macOS: rew install subversion
   - Linux: sudo apt-get install subversion

3. **Ollama连接失败**
   `ash
   curl http://localhost:11434/api/tags
   ollama serve
   `

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个工具。

### 开发环境设置

`ash
git clone https://github.com/YOUR_USERNAME/svn-auto-merge.git
cd svn-auto-merge
pip install -r requirements.txt
`

## 📄 许可证

MIT License

## 📝 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的自动合并功能
- 集成AI冲突分析
- 提供交互式界面
- 支持多种触发方式

---

如有问题或建议，请提交Issue或联系维护者。
