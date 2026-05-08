"""
5G 信号看板核心功能单元测试
测试信号颜色映射、颜色列添加、高度归一化等纯函数逻辑
"""
import sys
import os
import pytest
import pandas as pd
import numpy as np

# 让测试模块能够导入 app.py 中的函数
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 在导入 app 之前，先 mock 掉 streamlit，避免 @st.cache_data 等装饰器报错
import unittest.mock as mock
sys.modules.setdefault("streamlit", mock.MagicMock())

from app import get_signal_color, add_color_columns, normalize_elevation


class TestGetSignalColor:
    """测试 RSRP → RGBA 颜色映射逻辑。"""

    def test_strong_signal_above_minus90_is_green(self):
        """RSRP > -90 dBm 应返回绿色（R≈0, G>0）。"""
        color = get_signal_color(-80)
        assert color[0] == 0, "强信号红色通道应为 0"
        assert color[1] == 200, "强信号绿色通道应为 200"
        assert color[2] == 0, "强信号蓝色通道应为 0"

    def test_weak_signal_below_minus110_is_red(self):
        """RSRP < -110 dBm 应返回红色（R>0, G≈0）。"""
        color = get_signal_color(-120)
        assert color[0] == 255, "弱信号红色通道应为 255"
        assert color[1] == 50, "弱信号绿色通道应为 50"

    def test_medium_signal_returns_four_channels(self):
        """中等信号 (-90 ~ -110 dBm) 应返回包含 4 个元素的列表。"""
        color = get_signal_color(-100)
        assert len(color) == 4

    def test_boundary_at_minus90_treated_as_medium(self):
        """恰好 -90 dBm 不满足 > -90，走渐变分支，结果应接近绿色。"""
        color = get_signal_color(-90)
        assert color[0] == 0   # ratio=1 → r=0
        assert color[1] == 200  # ratio=1 → g=200

    def test_boundary_at_minus110_treated_as_medium(self):
        """恰好 -110 dBm 不满足 < -110，走渐变分支，结果应接近红色。"""
        color = get_signal_color(-110)
        assert color[0] == 255  # ratio=0 → r=255
        assert color[1] == 0    # ratio=0 → g=0

    def test_alpha_channel_is_nonzero(self):
        """所有信号强度下 alpha 通道应大于 0（可见）。"""
        for rsrp in [-80, -100, -120]:
            color = get_signal_color(rsrp)
            assert color[3] > 0, f"RSRP={rsrp} 时 alpha 通道不应为 0"

    def test_color_values_are_in_valid_range(self):
        """所有 RGBA 值应在 0~255 范围内。"""
        for rsrp in [-70, -90, -100, -110, -130]:
            color = get_signal_color(rsrp)
            for v in color:
                assert 0 <= v <= 255, f"颜色值 {v} 超出 0-255 范围 (rsrp={rsrp})"


class TestAddColorColumns:
    """测试 add_color_columns 函数的 DataFrame 操作。"""

    def _sample_df(self):
        return pd.DataFrame({"RSRP_dBm": [-80.0, -100.0, -120.0]})

    def test_adds_r_g_b_a_columns(self):
        """函数应向 DataFrame 中添加 r, g, b, a 四列。"""
        result = add_color_columns(self._sample_df())
        for col in ["r", "g", "b", "a"]:
            assert col in result.columns, f"缺少颜色列: {col}"

    def test_does_not_mutate_original_dataframe(self):
        """原始 DataFrame 不应被修改（函数应返回副本）。"""
        df = self._sample_df()
        original_columns = list(df.columns)
        add_color_columns(df)
        assert list(df.columns) == original_columns

    def test_strong_signal_row_has_green_color(self):
        """-80 dBm 行的 r 应为 0，g 应为 200。"""
        result = add_color_columns(self._sample_df())
        row = result[result["RSRP_dBm"] == -80.0].iloc[0]
        assert row["r"] == 0
        assert row["g"] == 200

    def test_weak_signal_row_has_red_color(self):
        """-120 dBm 行的 r 应为 255。"""
        result = add_color_columns(self._sample_df())
        row = result[result["RSRP_dBm"] == -120.0].iloc[0]
        assert row["r"] == 255

    def test_preserves_original_columns(self):
        """结果应同时保留原始列和新增的颜色列。"""
        result = add_color_columns(self._sample_df())
        assert "RSRP_dBm" in result.columns


class TestNormalizeElevation:
    """测试 normalize_elevation 函数的高度归一化逻辑。"""

    def test_elevation_within_specified_bounds(self):
        """归一化后的高度应在 [min_height, max_height] 范围内。"""
        df = pd.DataFrame({"Download_Mbps": [100.0, 500.0, 1000.0]})
        result = normalize_elevation(df, min_height=50, max_height=600)
        assert result["elevation"].min() >= 50
        assert result["elevation"].max() <= 600

    def test_max_download_gets_max_height(self):
        """下载速率最高的点应获得最大高度。"""
        df = pd.DataFrame({"Download_Mbps": [100.0, 500.0, 1000.0]})
        result = normalize_elevation(df, min_height=50, max_height=600)
        max_idx = df["Download_Mbps"].idxmax()
        assert result.loc[max_idx, "elevation"] == pytest.approx(600)

    def test_min_download_gets_min_height(self):
        """下载速率最低的点应获得最小高度。"""
        df = pd.DataFrame({"Download_Mbps": [100.0, 500.0, 1000.0]})
        result = normalize_elevation(df, min_height=50, max_height=600)
        min_idx = df["Download_Mbps"].idxmin()
        assert result.loc[min_idx, "elevation"] == pytest.approx(50)

    def test_uniform_speed_gets_min_height(self):
        """所有点速率相同时，全部应使用 min_height。"""
        df = pd.DataFrame({"Download_Mbps": [500.0, 500.0, 500.0]})
        result = normalize_elevation(df, min_height=50, max_height=600)
        assert (result["elevation"] == 50).all()

    def test_does_not_mutate_original_dataframe(self):
        """原始 DataFrame 不应被修改。"""
        df = pd.DataFrame({"Download_Mbps": [100.0, 500.0]})
        original_columns = list(df.columns)
        normalize_elevation(df)
        assert list(df.columns) == original_columns

    def test_elevation_column_added(self):
        """结果 DataFrame 中应包含 elevation 列。"""
        df = pd.DataFrame({"Download_Mbps": [100.0, 500.0]})
        result = normalize_elevation(df)
        assert "elevation" in result.columns
