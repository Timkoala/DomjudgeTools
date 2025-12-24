# DOMjudge 工具集

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.6+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Flask-3.0.0-green.svg" alt="Flask Version">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

一个简单易用的 DOMjudge 工具集，包含：
- 📄 **队伍账号生成器** - 根据学号和姓名快速生成标准格式的 teams.tsv 和 accounts.tsv 文件
- 📦 **题目包生成器** - 根据题面PDF和测试数据生成符合DOMjudge格式的题目压缩包

## ✨ 功能特性

### 账号生成器
- 📁 **多格式支持** - 支持文本文件(.txt)和Excel文件(.xlsx/.xls)
- 👁️ **实时预览** - 生成前可预览文件内容，确保数据正确
- ⬇️ **一键下载** - 自动打包为 ZIP 文件，方便使用
- 🔒 **安全密码** - 自动生成8位纯数字密码（1-9，不含0）
- 🚀 **双模式运行** - 支持命令行和 Web 界面两种使用方式

### 题目包生成器
- 📄 **PDF解析** - 自动从题面PDF中提取题目名称、时间限制、内存限制
- 🧠 **智能补全** - 未填写的信息自动从PDF解析，解析失败使用默认值
- 📊 **测试数据管理** - 支持正式测试数据和样例数据分类
- 🎨 **可选配置** - 支持自定义气球颜色等可选项
- ✅ **格式验证** - 自动验证数据完整性和文件配对
- 🎨 **现代化界面** - 简洁美观的 Web 界面
- 📱 **响应式设计** - 支持桌面端和移动端

## 文件格式说明

### 输入格式
文本文件格式：每行一个学生，使用 Tab 分隔
```
2307110101	黄宇
2307110103	向燕萍
2307110104	邓诗榕
```

### 输出格式

#### teams.tsv
```
teams	1
学号	队伍ID	类别	姓名			
2307110101	GXU2307110101	3	黄宇			
```

#### accounts.tsv
```
accounts	1		
team	姓名	学号	密码
team	黄宇	2307110101	12345678
```

## 安装和运行

### 方式一：Web 界面（推荐）

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 启动 Web 服务
```bash
python app.py
```

3. 打开浏览器访问 `http://127.0.0.1:5000`

4. 使用界面操作：
   - 上传 .txt 文件或直接输入文本
   - 点击"预览"查看生成结果
   - 点击"生成并下载"获取文件

### 方式二：命令行工具

```bash
python generator.py input.txt
```

这将在同目录下生成 `teams.tsv` 和 `accounts.tsv` 文件。

## 题目包格式说明

题目包生成器根据 DOMjudge 标准格式生成压缩包，包含以下文件：

### 生成的压缩包结构
```
题目名称_problem.zip
├── domjudge-problem.ini    # 题目基本配置
├── problem.pdf            # 题目题面文档
├── problem.yaml           # 题目详细配置
└── data/                  # 测试数据目录
    ├── secret/            # 正式测试数据
    │   ├── 1.in
    │   ├── 1.ans
    │   ├── 2.in
    │   └── 2.ans
    └── sample/            # 样例数据（可选）
        ├── example1.in
        └── example1.ans
```

### 配置文件说明

#### domjudge-problem.ini
```ini
[problem]
timelimit = 1.0
color = '#FF0000'
```

#### problem.yaml
```yaml
name: 'A + B Problem'
limits:
  memory: 256
```

### 测试数据要求
- 输入文件：`.in` 或 `.input` 扩展名
- 输出文件：`.ans`、`.out` 或 `.output` 扩展名
- 文件名包含 `sample` 或 `example` 的将归类为样例数据
- 其他文件自动归类为正式测试数据

## 项目结构

```
DomjudgeTools/
├── app.py                  # Flask Web 应用
├── generator.py           # 账号生成逻辑
├── problem_generator.py   # 题目包生成逻辑
├── requirements.txt       # Python 依赖
├── README.md             # 说明文档
└── templates/
    ├── index.html         # 账号生成界面
    └── problem.html       # 题目包生成界面
```

## 技术栈

- **后端**: Python + Flask
- **前端**: HTML + CSS + JavaScript
- **功能**: 文件处理、密码生成、ZIP 打包

## 配置说明

### 队伍类别设置
默认队伍类别为 `3`，可在 `generator.py` 中修改：

```python
def generate_teams_tsv(students, category='3'):
```

### 密码生成规则
- 长度：8位
- 字符：纯数字 1-9（不含0）
- 每次生成随机密码

## 使用示例

### Web 界面使用
1. 打开 http://127.0.0.1:5000
2. 准备学号姓名数据（格式：学号[Tab]姓名）
3. 上传文件或粘贴文本
4. 预览生成结果
5. 下载 ZIP 文件

### 命令行使用
```bash
# 创建输入文件
echo -e "2307110101\t黄宇\n2307110103\t向燕萍" > input.txt

# 生成账号文件
python generator.py input.txt

# 查看生成的文件
ls -la *.tsv
```

## 注意事项

1. **文件编码**: 输入文件必须是 UTF-8 编码
2. **分隔符**: 学号和姓名之间使用 Tab 分隔
3. **密码安全**: 生成的密码为随机数字，建议首次登录后要求用户修改
4. **文件格式**: 生成的 TSV 文件严格遵循 DOMjudge 导入格式

## 故障排除

### 常见问题

**Q: 上传文件后没有反应？**
A: 检查文件编码是否为 UTF-8，确保使用 Tab 分隔符

**Q: 生成的密码可以自定义吗？**
A: 可以修改 `generate_password()` 函数来自定义密码规则

**Q: 支持批量处理多个文件吗？**
A: 当前版本支持单文件处理，可以将多个文件内容合并后处理

**Q: 如何修改队伍类别？**
A: 在 `generator.py` 的 `generate_teams_tsv()` 函数中修改默认的 `category` 参数

## 版本信息

- 当前版本: 1.0.0
- Python 兼容性: 3.6+
- 依赖: Flask 3.0.0

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
