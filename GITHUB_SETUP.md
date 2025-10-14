# GitHub仓库创建和推送指南

## 步骤1: 在GitHub上创建新仓库

1. 访问 https://github.com
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - Repository name: svn-auto-merge
   - Description: SVN自动合并智能体工具 - 基于AI的智能SVN合并工具
   - 选择 Public 或 Private
   - 不要勾选 "Add a README file"（我们已经有了）
   - 不要勾选 "Add .gitignore"（我们已经有了）
   - 不要选择 License（可选）
4. 点击 "Create repository"

## 步骤2: 连接本地仓库到GitHub

在项目目录中运行以下命令（替换 YOUR_USERNAME 为您的GitHub用户名）：

`ash
git remote add origin https://github.com/YOUR_USERNAME/svn-auto-merge.git
git branch -M main
git push -u origin main
`

## 步骤3: 验证推送

推送完成后，您可以在GitHub上看到：
- 所有项目文件
- README.md 自动显示
- 提交历史记录

## 项目文件说明

- svn_auto_merge.py: 主程序文件
- config.json: 配置文件模板
- equirements.txt: Python依赖列表
- start.bat: Windows一键启动脚本
- README.md: 详细使用说明
- PROJECT_SUMMARY.md: 项目总结
- hooks/: SVN钩子脚本目录
- .gitignore: Git忽略文件配置

## 后续操作

1. 克隆仓库到其他机器：
   `ash
   git clone https://github.com/YOUR_USERNAME/svn-auto-merge.git
   `

2. 更新代码：
   `ash
   git add .
   git commit -m "更新说明"
   git push
   `

3. 创建Release版本：
   - 在GitHub仓库页面点击 "Releases"
   - 点击 "Create a new release"
   - 填写版本号和发布说明
