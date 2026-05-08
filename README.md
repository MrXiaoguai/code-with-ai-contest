# 📡 5G 信号可视化看板

> **"Code with AI" 挑战赛** 参赛作品 — 5G 路测数据实时交互分析平台

## 功能亮点

### 基础关卡 ✅
- **数据加载**：使用 pandas 读取 `data/signal_samples.csv`，并通过 `@st.cache_data` 缓存加速
- **3D 信号地图**：pydeck ColumnLayer 将每个测量点以 3D 柱体呈现在交互地图上，颜色按信号强度分级：
  - 🟢 绿色：RSRP > -90 dBm（强信号）
  - 🟡 黄橙渐变：-110 dBm ≤ RSRP ≤ -90 dBm（中等信号）
  - 🔴 红色：RSRP < -110 dBm（弱信号）
- **统计图表**：各频段基站数量柱状图 + 终端类型占比环形图（使用 Altair）

### 进阶关卡 ✅
- **侧边栏联动筛选**：提供频段下拉、终端类型下拉、RSRP 范围滑块、SINR 范围滑块，全部实时联动地图和图表
- **3D 极客视觉**：柱体高度随下载速率（Download_Mbps）动态变化，俯仰视角 55° 呈现立体感
- **工程化素养**：核心函数均有规范注释，`tests/` 目录包含完整单元测试套件

## 截图预览

> 截图存放于仓库根目录 `screenshots/` 文件夹，包含：
> - `screenshot_map_overview.png` — 3D 地图全貌
> - `screenshot_sidebar_filter.png` — 侧边栏筛选联动效果
> - `screenshot_charts.png` — 统计图表区域

## 快速运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`。

### 3. 运行单元测试

```bash
pytest tests/ -v
```

## 目录结构

```
code-with-ai-contest/
├── app.py                  # 主应用（Streamlit）
├── requirements.txt        # Python 依赖
├── data/
│   └── signal_samples.csv  # 5G 路测模拟数据集
├── tests/
│   └── test_signal_utils.py  # 单元测试
└── AI_PROMPTS.md           # AI Agent 交互日志
```

## 数据说明

| 字段 | 含义 |
|------|------|
| Latitude / Longitude | 测量点经纬度 |
| CellID | 小区唯一标识 |
| Band | 5G 频段（n28 / n41 / n78）|
| RSRP_dBm | 参考信号接收功率（信号强度，dBm）|
| SINR_dB | 信号与干扰加噪声比（信噪比，dB）|
| TerminalType | 终端类型（Smartphone / CPE / IoT）|
| Download_Mbps | 下载速率（Mbps）|

## 技术栈

- [Streamlit](https://streamlit.io/) — Web 应用框架
- [pydeck](https://deckgl.readthedocs.io/) — 基于 deck.gl 的 3D 地图渲染
- [Altair](https://altair-viz.github.io/) — 声明式统计图表库
- [pandas](https://pandas.pydata.org/) — 数据处理
- [pytest](https://docs.pytest.org/) — 单元测试框架
