# SVN Auto Merge Tool - 部署指南

## 🚀 快速部署

### 1. 环境要求
- Python 3.7+
- SVN客户端
- Windows环境（当前版本）

### 2. 安装步骤

#### 克隆项目
```bash
git clone <repository-url>
cd svn-auto-merge
```

#### 安装依赖
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate.bat

# 安装依赖
pip install -r requirements.txt
```

#### 配置设置
1. 编辑 `config.json` 文件
2. 设置正确的分支路径
3. 配置匹配规则

```json
{
  "source_branch": "你的源分支路径",
  "target_branch": "你的目标分支路径",
  "match_patterns": {
    "bug": "--bug=(\\w+)",
    "user": "--user=你的用户名"
  }
}
```

### 3. 启动服务

#### 方式1: 使用启动脚本（推荐）
```bash
.\start.bat
```

#### 方式2: 直接运行
```bash
python start_hook_system.py
```

#### 方式3: 轮询模式
```bash
python svn_auto_merge.py --auto-start
```

### 4. 验证部署

#### 检查日志
```bash
# 查看合并日志
type logs\merge.log

# 查看版本记录
type logs\last_revision.txt
```

#### 测试功能
1. 在源分支创建一个匹配规则的提交
2. 观察Hook系统是否检测到
3. 检查是否自动合并到目标分支

### 5. 监控和维护

#### 日志监控
- 定期检查 `logs/merge.log`
- 关注错误信息和警告
- 监控合并成功率

#### 性能监控
- 检查SVN操作性能
- 监控磁盘空间使用
- 关注内存使用情况

#### 故障排除
- 检查SVN锁定问题
- 验证分支路径正确性
- 确认权限设置

### 6. 生产环境建议

#### 安全设置
- 使用专用SVN账户
- 设置适当的文件权限
- 定期备份配置文件

#### 性能优化
- 调整检查间隔
- 优化匹配规则
- 监控系统资源

#### 高可用性
- 设置自动重启机制
- 配置监控告警
- 准备故障恢复方案

---

**注意**: 请根据实际环境调整配置参数
