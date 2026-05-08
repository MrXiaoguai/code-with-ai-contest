# Agent 交互日志

**团队名称：** [填写你的团队名称]
**成员名单：** [填写成员1, 成员2, 成员3]
**使用的 AI Coding Agent 工具：** Claude Code (claude-sonnet-4-6)

---

## 🤖 交互记录（完整会话，2026-05-08）

---

### [1] 用户指令

> 根据项目中的readme，完成比赛

**Claude Code 行动：**
- 读取 `README.md`、`AI_PROMPTS.md`、`app.py`、`requirements.txt`、`data/signal_samples.csv`
- 理解赛题：用 Streamlit + pydeck 构建 5G 信号可视化看板，覆盖基础关卡和进阶关卡
- 数据字段：Latitude, Longitude, CellID, Band, RSRP_dBm, SINR_dB, TerminalType, Download_Mbps

---

### [2] 实现 app.py（基础 + 进阶关卡）

**Claude Code 设计决策：**
- 使用 pydeck `ColumnLayer` 实现 3D 地图，柱高映射 `Download_Mbps`，颜色映射 `RSRP_dBm`
- 颜色分级：绿（>-90dBm）→ 黄橙渐变（-90~-110dBm）→ 红（<-110dBm）
- 底图选用 Carto Dark Matter（无需 Mapbox API Key）
- 使用 Altair 绘制频段柱状图和终端类型环形图
- 侧边栏：频段下拉、终端类型下拉、RSRP 范围滑块、SINR 范围滑块，全部实时联动

**核心函数：**
```python
def get_signal_color(rsrp: float) -> list[int]:
    if rsrp > -90:
        return [0, 200, 0, 210]        # 绿色：强信号
    elif rsrp < -110:
        return [255, 50, 50, 210]      # 红色：弱信号
    else:
        ratio = (rsrp - (-110)) / 20.0 # 线性插值
        r = int(255 * (1 - ratio))
        g = int(200 * ratio)
        return [r, g, 0, 210]          # 黄橙渐变：中等信号

def normalize_elevation(df, min_height=50, max_height=600):
    dl_range = df["Download_Mbps"].max() - df["Download_Mbps"].min()
    if dl_range > 0:
        df["elevation"] = (
            (df["Download_Mbps"] - df["Download_Mbps"].min()) / dl_range
        ) * (max_height - min_height) + min_height
    else:
        df["elevation"] = min_height
    return df
```

---

### [3] 工程化：单元测试

**Claude Code 行动：**
- 创建 `tests/test_signal_utils.py`，含 18 个单元测试
- 使用 `unittest.mock` mock 掉 `streamlit`，避免 `@st.cache_data` 报错
- 覆盖：`get_signal_color`（强/弱/中等/边界值/颜色范围）、`add_color_columns`（列添加/不修改原 DF）、`normalize_elevation`（上下界/极值映射/均匀场景）

**运行结果：**
```
============================= 18 passed in 0.72s ==============================
```

---

### [4] 用户指令

> 先不提交，如果开发完成后，先进行测试，待我验收后再提交

**Claude Code 行动：**
- 启动 Streamlit：`python -m streamlit run app.py --server.headless true --browser.gatherUsageStats false`
- 服务运行在 `http://localhost:8501`，等待用户验收

---

### [5] 用户指令

> 怎么没有运行时截图，这个要我自己截图么

**Claude Code 行动：**
- 安装 Playwright，使用系统已有 Chrome（`C:\Program Files\Google\Chrome\Application\chrome.exe`）
- 编写 `take_screenshots.py` 自动截取 3 张截图

---

### [6] 用户指令

> 三张图都要完整的截图，前面两张不是完整页面

**Claude Code 行动：**
- 将视口高度从 900px 改为 1800px，确保地图和图表都在视口内一次性完整捕获
- 三张截图分别对应三种筛选状态：
  1. 默认状态（全部 500 个测量点）
  2. 筛选 n78 频段（161 点）
  3. 筛选 Smartphone 终端（148 点）

---

### [7] 用户指令

> AI_PROMPTS.md 更新后提交

**Claude Code 行动：**
- 更新本文件（AI_PROMPTS.md）为完整交互日志
- 执行 `git add` + `git commit` + `git tag basic-done` + `git tag advanced-done` + `git push`

---

## 完成的关卡清单

### 🟢 基础关卡

| 任务 | 实现 | 状态 |
|------|------|------|
| pandas 读取 CSV | `load_data()` + `@st.cache_data` | ✅ |
| 交互地图打点 | pydeck ColumnLayer，Carto 暗色底图 | ✅ |
| 信号强度变色 | RSRP>-90→绿，<-110→红，中间线性渐变 | ✅ |
| 数据概览图表 | Altair 柱状图（频段分布）+ 环形图（终端占比）| ✅ |

### 🟡 进阶关卡

| 任务 | 实现 | 状态 |
|------|------|------|
| 侧边栏联动筛选 | 频段/终端下拉 + RSRP/SINR 滑块，实时更新 | ✅ |
| 3D 地图极客视觉 | ColumnLayer 柱高=Download_Mbps，仰角 55° | ✅ |
| 规范注释 | 所有函数含类型注解和 docstring | ✅ |
| 单元测试 | 18 个测试全部通过 | ✅ |
