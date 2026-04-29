# Usage

## 安装依赖

```bash
uv sync
```

## 使用说明

### 1. 运行爬虫

```bash
# 使用默认关键词 python，爬取所有页面
python main.py --spider keyword

# 使用自定义关键词 python
python main.py --spider keyword --keyword python

# 使用其他关键词
python main.py --spider keyword --keyword 数据分析

# 限制爬取页数（只爬前3页）
python main.py --spider keyword --max-pages 3

# 组合使用
python main.py --spider keyword --keyword python --max-pages 5
```

### 2. 画统计图

```bash
# 使用默认数据文件
python showdata.py

# 指定数据文件路径
python showdata.py --csv data/origin/data.csv
```
