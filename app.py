"""
5G 信号可视化看板 — "Code with AI" 挑战赛参赛作品
使用 Streamlit + pydeck + Altair 构建交互式 Web 数据看板
"""
import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import altair as alt

st.set_page_config(
    page_title="5G 信号可视化看板",
    page_icon="📡",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    """从 CSV 文件加载并缓存 5G 路测数据。"""
    return pd.read_csv("data/signal_samples.csv")


def get_signal_color(rsrp: float) -> list[int]:
    """
    将 RSRP (dBm) 映射为 RGBA 颜色列表，供 pydeck 使用。

    绿色 (> -90 dBm) → 黄橙渐变 (-90 ~ -110 dBm) → 红色 (< -110 dBm)
    """
    if rsrp > -90:
        return [0, 200, 0, 210]
    elif rsrp < -110:
        return [255, 50, 50, 210]
    else:
        # 线性插值：-110dBm 时 ratio=0（红），-90dBm 时 ratio=1（绿）
        ratio = (rsrp - (-110)) / 20.0
        r = int(255 * (1 - ratio))
        g = int(200 * ratio)
        return [r, g, 0, 210]


def add_color_columns(df: pd.DataFrame) -> pd.DataFrame:
    """根据 RSRP 信号强度为 DataFrame 添加 r/g/b/a 四列颜色数据。"""
    df = df.copy()
    colors = df["RSRP_dBm"].apply(get_signal_color)
    df["r"] = colors.apply(lambda c: c[0])
    df["g"] = colors.apply(lambda c: c[1])
    df["b"] = colors.apply(lambda c: c[2])
    df["a"] = colors.apply(lambda c: c[3])
    return df


def normalize_elevation(
    df: pd.DataFrame, min_height: float = 50, max_height: float = 600
) -> pd.DataFrame:
    """将 Download_Mbps 归一化为 pydeck ColumnLayer 的高度值（米）。"""
    df = df.copy()
    dl_range = df["Download_Mbps"].max() - df["Download_Mbps"].min()
    if dl_range > 0:
        df["elevation"] = (
            (df["Download_Mbps"] - df["Download_Mbps"].min()) / dl_range
        ) * (max_height - min_height) + min_height
    else:
        df["elevation"] = min_height
    return df


def build_3d_map(df: pd.DataFrame) -> pdk.Deck:
    """构建 pydeck 3D 柱状地图：柱高=下载速率，颜色=信号强度。"""
    map_df = add_color_columns(df)
    map_df = normalize_elevation(map_df)

    layer = pdk.Layer(
        "ColumnLayer",
        data=map_df,
        get_position=["Longitude", "Latitude"],
        get_elevation="elevation",
        elevation_scale=1,
        radius=65,
        get_fill_color=["r", "g", "b", "a"],
        pickable=True,
        auto_highlight=True,
    )

    view = pdk.ViewState(
        latitude=map_df["Latitude"].mean(),
        longitude=map_df["Longitude"].mean(),
        zoom=12,
        pitch=55,
        bearing=-10,
    )

    tooltip = {
        "html": (
            "<b>🏗 小区 ID:</b> {CellID}<br/>"
            "<b>📶 频段:</b> {Band}<br/>"
            "<b>📉 RSRP:</b> {RSRP_dBm} dBm<br/>"
            "<b>📊 SINR:</b> {SINR_dB} dB<br/>"
            "<b>⬇ 下载速率:</b> {Download_Mbps} Mbps<br/>"
            "<b>📱 终端类型:</b> {TerminalType}"
        ),
        "style": {
            "backgroundColor": "#1a1a2e",
            "color": "#e0e0ff",
            "padding": "10px",
            "borderRadius": "6px",
        },
    }

    return pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    )


def render_band_chart(df: pd.DataFrame) -> alt.Chart:
    """生成各频段基站数量柱状图。"""
    band_df = df["Band"].value_counts().reset_index()
    band_df.columns = ["频段", "数量"]
    return (
        alt.Chart(band_df)
        .mark_bar(color="#4fc3f7", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("频段:N", sort="-y", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("数量:Q", title="基站数量"),
            tooltip=["频段", "数量"],
        )
        .properties(height=280)
    )


def render_terminal_chart(df: pd.DataFrame) -> alt.Chart:
    """生成各终端类型占比环形图。"""
    term_df = df["TerminalType"].value_counts().reset_index()
    term_df.columns = ["终端类型", "数量"]
    return (
        alt.Chart(term_df)
        .mark_arc(innerRadius=55, outerRadius=100)
        .encode(
            theta=alt.Theta("数量:Q"),
            color=alt.Color(
                "终端类型:N",
                scale=alt.Scale(scheme="tableau10"),
                legend=alt.Legend(title="终端类型"),
            ),
            tooltip=["终端类型", "数量"],
        )
        .properties(height=280)
    )


def main():
    st.title("📡 5G 信号可视化看板")
    st.markdown("**'Code with AI' 挑战赛** — 5G 路测数据实时交互分析平台")

    df = load_data()

    # ── 侧边栏筛选器 ─────────────────────────────────────────
    st.sidebar.title("🔍 数据筛选器")

    bands = ["全部"] + sorted(df["Band"].unique().tolist())
    selected_band = st.sidebar.selectbox("频段 (Band)", bands)

    terminals = ["全部"] + sorted(df["TerminalType"].unique().tolist())
    selected_terminal = st.sidebar.selectbox("终端类型", terminals)

    rsrp_range = st.sidebar.slider(
        "RSRP 范围 (dBm)",
        float(df["RSRP_dBm"].min()),
        float(df["RSRP_dBm"].max()),
        (float(df["RSRP_dBm"].min()), float(df["RSRP_dBm"].max())),
        step=1.0,
    )

    sinr_range = st.sidebar.slider(
        "SINR 范围 (dB)",
        float(df["SINR_dB"].min()),
        float(df["SINR_dB"].max()),
        (float(df["SINR_dB"].min()), float(df["SINR_dB"].max())),
        step=1.0,
    )

    # 应用筛选条件
    mask = (
        (df["RSRP_dBm"] >= rsrp_range[0])
        & (df["RSRP_dBm"] <= rsrp_range[1])
        & (df["SINR_dB"] >= sinr_range[0])
        & (df["SINR_dB"] <= sinr_range[1])
    )
    if selected_band != "全部":
        mask &= df["Band"] == selected_band
    if selected_terminal != "全部":
        mask &= df["TerminalType"] == selected_terminal
    fdf = df[mask].copy()

    st.sidebar.markdown("---")
    st.sidebar.metric("当前显示数据点", len(fdf))
    if len(fdf) > 0:
        strong = (fdf["RSRP_dBm"] > -90).sum()
        weak = (fdf["RSRP_dBm"] < -110).sum()
        st.sidebar.metric("强信号点 (>-90dBm)", strong)
        st.sidebar.metric("弱信号点 (<-110dBm)", weak)

    # ── KPI 指标行 ───────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("总测量点", len(fdf))
    c2.metric("平均 RSRP", f"{fdf['RSRP_dBm'].mean():.1f} dBm" if len(fdf) else "—")
    c3.metric("平均 SINR", f"{fdf['SINR_dB'].mean():.1f} dB" if len(fdf) else "—")
    c4.metric("平均下载速率", f"{fdf['Download_Mbps'].mean():.0f} Mbps" if len(fdf) else "—")

    # ── 3D 信号地图 ──────────────────────────────────────────
    st.subheader("🗺️ 5G 信号强度 3D 可视化地图")
    st.caption(
        "柱高代表下载速率 | 颜色：🟢 强信号 (>-90 dBm) → 🟡 中等 → 🔴 弱信号 (<-110 dBm)"
    )

    if len(fdf) == 0:
        st.warning("当前筛选条件下无数据，请在左侧调整筛选器。")
    else:
        st.pydeck_chart(build_3d_map(fdf))

    # ── 统计图表 ─────────────────────────────────────────────
    st.subheader("📊 数据统计图表")
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("**各频段基站数量**")
        if len(fdf) > 0:
            st.altair_chart(render_band_chart(fdf), use_container_width=True)
        else:
            st.info("无数据可显示")

    with ch2:
        st.markdown("**终端类型占比**")
        if len(fdf) > 0:
            st.altair_chart(render_terminal_chart(fdf), use_container_width=True)
        else:
            st.info("无数据可显示")

    # ── 原始数据表 ───────────────────────────────────────────
    with st.expander("📋 查看原始数据表格"):
        st.dataframe(fdf, use_container_width=True)


if __name__ == "__main__":
    main()
