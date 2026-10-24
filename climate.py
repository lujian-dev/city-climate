"""城市气候舒适度：用一年逐日气象数据，回答「哪座城市的气候最舒服」。"""

import json
import urllib.parse
import urllib.request

import pandas as pd
import streamlit as st

CITIES = {
    "北京": (39.90, 116.40),
    "上海": (31.23, 121.47),
    "广州": (23.13, 113.26),
    "成都": (30.57, 104.07),
    "武汉": (30.59, 114.31),
    "西安": (34.34, 108.94),
    "哈尔滨": (45.80, 126.53),
    "昆明": (25.04, 102.71),
    "乌鲁木齐": (43.83, 87.62),
    "拉萨": (29.65, 91.14),
    "三亚": (18.25, 109.51),
    "沈阳": (41.80, 123.43),
    "长沙": (28.23, 112.94),
}

START = "2025-01-01"
END = "2025-12-31"
COMFORT_LOW = 12
COMFORT_HIGH = 28


@st.cache_data(ttl="24h", show_spinner=False)
def fetch_city(name: str, lat: float, lon: float) -> pd.DataFrame:
    """拉一座城市一整年的逐日气温与降水。参数进缓存键，换城市会自动重新拉。"""
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": START,
        "end_date": END,
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum",
        "timezone": "auto",
    }
    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as resp:
        daily = json.load(resp)["daily"]

    df = pd.DataFrame(
        {
            "date": pd.to_datetime(daily["time"]),
            "tmax": daily["temperature_2m_max"],
            "tmin": daily["temperature_2m_min"],
            "tmean": daily["temperature_2m_mean"],
            "precip": daily["precipitation_sum"],
        }
    )
    df["city"] = name
    return df


def load_data() -> pd.DataFrame:
    """把各城市拼成一张长表，并算出「舒适日」。

    这里故意不加缓存：它依赖 CITIES、COMFORT_LOW、COMFORT_HIGH 三个全局变量，
    而缓存只认函数参数，改了这些变量缓存不会失效。真正贵的是网络请求，
    那部分交给 fetch_city 缓存，这段便宜的计算每次重跑就好。
    """
    frames = [fetch_city(name, lat, lon) for name, (lat, lon) in CITIES.items()]
    df = pd.concat(frames, ignore_index=True)
    df["month"] = df["date"].dt.month
    df["comfort"] = df["tmean"].between(COMFORT_LOW, COMFORT_HIGH) & (df["precip"] < 1)
    df["big_range"] = (df["tmax"] - df["tmin"]) > 10
    return df


st.set_page_config(page_title="城市气候舒适度", page_icon="🌤", layout="wide")

st.title("哪座城市的气候最舒服")
st.caption(f"{START} 至 {END} 逐日气温与降水 · 数据来源 Open-Meteo")

with st.spinner(f"正在拉取 {len(CITIES)} 座城市一年的逐日数据，第一次会慢一点…"):
    df = load_data()

summary = df.groupby("city").agg(
    舒适天数=("comfort", "sum"),
    年均温=("tmean", "mean"),
    年降水=("precip", "sum"),
    高温天数=("tmax", lambda s: int((s >= 35).sum())),
    严寒天数=("tmin", lambda s: int((s <= 0).sum())),
    温差天数=("big_range", "sum"),
)
summary["舒适占比"] = summary["舒适天数"] / df.groupby("city")["date"].count() * 100
summary = summary.round(1).sort_values("舒适天数", ascending=False)

best = summary.index[0]

with st.container(horizontal=True):
    st.metric("最舒适城市", best, border=True)
    st.metric("舒适天数", f"{int(summary.iloc[0]['舒适天数'])} 天", border=True)
    st.metric("舒适占比", f"{summary.iloc[0]['舒适占比']:.0f}%", border=True)
    st.metric("参与对比", f"{len(summary)} 座城市", border=True)

with st.sidebar:
    picked = st.multiselect(
        "对比哪几座城市的月均气温",
        list(summary.index),
        default=list(summary.index[:4]),
    )
    st.caption(f"舒适日 = 日均温 {COMFORT_LOW}–{COMFORT_HIGH}℃ 且当天降水不足 1 毫米。")
    if st.button("重新拉取数据", width="stretch"):
        st.cache_data.clear()
        st.rerun()

left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.subheader("全年舒适天数排行")
        st.bar_chart(summary[["舒适天数"]], alt="各城市全年舒适天数排行", height=420)

with right:
    with st.container(border=True):
        st.subheader("月均气温对比")
        if picked:
            monthly = (
                df[df["city"].isin(picked)]
                .pivot_table(index="month", columns="city", values="tmean", aggfunc="mean")
                .round(1)
            )
            st.line_chart(monthly, alt="所选城市月均气温对比", height=420)
        else:
            st.info("在左侧选至少一座城市。")

with st.container(border=True):
    st.subheader("全部城市指标")
    st.dataframe(summary, alt="各城市气候指标明细")

st.markdown(
    f"**一句话结论**：{best}全年有 {int(summary.iloc[0]['舒适天数'])} 天"
    f"处在 {COMFORT_LOW}–{COMFORT_HIGH}℃ 且日降水不足 1 毫米，"
    f"占了 {summary.iloc[0]['舒适占比']:.0f}%。"
)
