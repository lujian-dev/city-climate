# 城市气候舒适度看板

用 2025 年全年逐日气象数据，比较 13 座中国城市的气候舒适程度。

## 它回答什么问题

「哪座城市的气候最舒服」——答案取决于你怎么定义「舒服」。

本项目把「舒适日」定义为：日均温在 12–28℃ 之间，且当天降水量不足 1 毫米。

## 数据来源

Open-Meteo 历史气象 API，逐日气温与降水，无需 API Key。
<img width="2557" height="1376" alt="6615a01eda9f8ab28639b4a8177496d6" src="https://github.com/user-attachments/assets/228926d1-e5a8-4cc7-9732-712307a58c88" />
<img width="2557" height="1375" alt="image" src="https://github.com/user-attachments/assets/d7febc78-e0b1-4788-ab7e-8d8a639ce934" />


## 主要功能

- 计算每座城市的舒适天数、舒适占比、年均温、年降水、极端高温与严寒天数
- 舒适天数排行榜
- 多城市月均气温对比
- 完整指标表格

## 运行方式

    pip install -r requirements.txt
    streamlit run climate.py

## 一个发现

把舒适区间从 15–25℃ 放宽到 12–28℃ 后，三亚仍然第一（132 → 163 天），
但昆明从第 6 掉到并列第 11——它的舒适天数明明从 74 涨到了 102，
只是别的城市涨得更多。

**绝对值上涨，不等于相对位置改善。**
