# Civitas 数据分析工具

这个项目是为Civitas游戏设计的数据收集和可视化工具。它能够自动收集游戏中的用户状态、技能以及详细信息，并提供直观的数据可视化界面。同时，提供食谱分析功能，帮助玩家找到最优的食材组合和烹饪方式。

## 功能特点

- 自动收集并存储用户状态数据
- 自动收集并存储用户技能数据
- 自动收集并存储用户详细信息
- 提供直观的表格格式数据可视化
- 支持用户名搜索和数据筛选
- 实时数据更新和刷新
- **食谱分析**：分析不同食材组合的效果，找出最佳配方
- **口味幸福度分析**：研究口味参数与幸福度的关系，优化食谱

## 项目结构

- `civitas_status_skill.user.js` - Tampermonkey脚本，用于从游戏中收集数据
- `consolidated_data_server.py` - 主服务器，用于接收和存储数据并提供Web界面
- `visualization.js` - 前端可视化脚本
- `visualization.css` - 前端样式表
- `visualization.html` - 前端HTML页面
- `recipe_analyzer.py` - 食谱分析工具，可以分析不同食材组合的效果
- `simple_taste_test.py` - 简化版测试脚本，用于测试口味参数与幸福度的关系
- `show_taste_table.py` - 展示配方口味数值的工具
- `display_taste_values.py` - 详细分析配方口味特性的工具

## 安装与使用

### 服务器端

1. 安装Python依赖：
```
pip install -r requirements.txt
```

2. 启动服务器：
```
python consolidated_data_server.py
```

服务器默认运行在 `http://localhost:5000`

### 客户端

1. 安装Tampermonkey浏览器扩展
2. 导入`civitas_status_skill.user.js`脚本
3. 访问Civitas游戏页面，脚本将自动运行并收集数据

### 可视化界面

访问 `http://localhost:5000/visualization/` 查看数据可视化页面。

### 食谱分析工具

1. 运行食谱分析：
```
python recipe_analyzer.py
```

2. 测试口味参数与幸福度的关系：
```
python simple_taste_test.py
```

3. 展示配方口味数值：
```
python show_taste_table.py
```

## API接口

- `/api/record_status` - 记录用户状态数据
- `/api/record_skill` - 记录用户技能数据
- `/api/record_userdetail` - 记录用户详细信息
- `/api/data` - 获取整合的数据
- `/api/stats` - 获取数据统计信息
- `/api/user_detail` - 获取用户详细信息

## 食谱分析功能

### 口味参数与幸福度关系分析

研究表明，口味参数与食谱的幸福度有以下关系：

1. **甜味**：甜味高的配方通常具有较高的幸福度
2. **酸味**：适量的酸味有助于提高幸福度，但过高会降低幸福度
3. **苦味**：低到中等苦度可接受，高苦度会极大降低幸福度
4. **辣味**：辣味对幸福度影响相对较小
5. **咸味**：适量的咸味可提供较好的幸福度，但高咸度会极大降低幸福度

### 最佳口味组合

最高幸福度的配方通常具有以下特点：
- 高甜度 (约45.0)
- 中等酸度 (约15.0)
- 低苦度 (约15.0)
- 最小化辣度和咸度

## 项目目的

该项目旨在分析Civitas2游戏数据，提供数据洞察和可视化，帮助玩家更好地了解游戏进程和优化游戏策略。

## 开发与贡献

欢迎提出问题和建议，也欢迎贡献代码。

## 更新日志

### 2025.02.28
- 添加了口味参数与幸福度关系分析功能
- 添加了简化版测试脚本
- 添加了配方口味数值展示工具
- 完善了食谱分析功能
