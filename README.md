# YsuInfo

> 燕山大学(YSU)教务系统自动化工具

## 📋 项目介绍

基于 Python 开发的燕山大学教务系统自动登录工具，支持成绩查询、绩点计算、课程表获取、考试安排查询等功能。自己完善，不要用于违法违规用途，不要提 PR。

## ✨ 主要功能

- 🔐 **自动登录**: 支持燕山大学统一身份认证系统自动登录
- 📊 **成绩查询**: 获取学期成绩、详细成绩信息
- 📈 **绩点计算**: 计算加权平均学分绩点(GPA)，支持学位课程权重
- 📅 **课程表查询**: 获取当前学期课程安排
- 📝 **考试安排**: 查询近期考试信息
- 🎯 **验证码识别**: 自动识别并处理登录验证码

## 📦 依赖库

- `requests` - HTTP 请求库
- `lxml` - XML/HTML 解析
- `ddddocr` - 验证码识别
- `pycryptodome` - 加密解密
- `pydantic` - 数据验证和配置管理

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置信息

修改 `config/config.py` 文件：

```python
class Config(BaseModel):
    username: str = "你的学号"      # 学号
    password: str = "你的密码"      # 统一身份认证密码
    pushkey: str = "推送密钥"       # 可选：用于成绩推送通知
```

### 基本使用

```python
from YsuInfo import YSUinfo

# 创建实例
ysu = YSUinfo("学号", "密码")

# 查询学期成绩
scores = ysu.get_term_score()

# 获取绩点信息
gpa_info = ysu.get_gpa("学号")

# 查询课程表
schedule = ysu.get_querySchedule()

# 查询考试安排
exams = ysu.get_recentExams()
```

### 快速测试

```bash
python YsuInfo.py
```

## 📊 功能详解

### 成绩查询

- `get_term_score()`: 获取当前学期成绩列表
- `get_score_detail(id)`: 获取指定课程详细成绩
- `get_score_list()`: 获取所有成绩记录

### 绩点计算

- `get_gpa(username)`: 在线查询官方绩点
- `calculateGPA()`: 本地计算加权平均学分绩点
- 支持学位课程 1.2 倍权重计算

### 课程安排

- `get_querySchedule()`: 获取课程表信息
- `get_recentExams()`: 查询近期考试安排

### 自动推送

- `pushScore()`: 监控新成绩发布并推送通知
- `pushGPA_online()`: 在线绩点查询推送
- `pushGPA_offline()`: 本地计算绩点推送

## 🔧 高级配置

### 缓存设置

```python
# 使用缓存登录（推荐）
ysu = YSUinfo("学号", "密码", useCache=True)

# 强制重新登录
ysu = YSUinfo("学号", "密码", useCache=False)
```

### 登录类型

```python
# 移动端登录（默认）
ysu = YSUinfo("学号", "密码", loginType=0)

# PC端登录
ysu = YSUinfo("学号", "密码", loginType=1)
```

## 📁 项目结构

```
ysu-info/
├── YsuInfo.py          # 主程序文件
├── Encrypt.py          # AES加密模块
├── requirements.txt    # 依赖配置
├── README.md          # 项目说明
├── config/            # 配置目录
│   ├── config.py      # 配置文件
│   ├── score.json     # 成绩缓存
│   ├── scoreList.json # 成绩列表缓存
│   └── session.json   # 会话缓存
└── __pycache__/       # Python缓存
```

## ⚠️ 注意事项

1. **账号安全**: 请妥善保管账号密码，建议使用环境变量配置
2. **使用频率**: 避免频繁请求，建议间隔使用以免对服务器造成压力，会导致 IP 和账号封禁

## 📜 开源协议

本项目仅供学习交流使用，使用者需遵守学校相关规定，不得用于违法违规用途。
