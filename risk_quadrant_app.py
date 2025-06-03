import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

# 设置页面配置
st.set_page_config(page_title="宏观风险象限图", layout="wide")
st.title("宏观风险象限图分析工具")

# 读取Excel文件
@st.cache_data
def load_data():
    try:
        # 尝试多个可能的路径
        possible_paths = [
            'index.xlsx',
            os.path.join(os.path.dirname(__file__), 'index.xlsx'),
            '/mount/src/macrorisk/index.xlsx'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                st.write(f"找到文件路径: {path}")
                df = pd.read_excel(path, sheet_name='comp')
                df['date'] = pd.to_datetime(df['date'])
                return df
        
        st.error("未能找到数据文件。尝试过的路径：" + "\n".join(possible_paths))
        return None
    except Exception as e:
        st.error(f"读取数据时出错：{str(e)}")
        st.write("当前工作目录：", os.getcwd())
        st.write("目录内容：", os.listdir())
        return None

df = load_data()

if df is None:
    st.stop()

# 侧边栏控件
st.sidebar.header("参数设置")
attention_threshold = st.sidebar.slider(
    "关注度阈值",
    min_value=0.0,
    max_value=1.0,
    value=0.3,  # 默认值改为0.3
    step=0.05
)

# 日期选择（使用下拉列表而不是日期输入）
available_dates = df['date'].dt.date.unique()
selected_date = st.sidebar.selectbox(
    "选择日期",
    options=available_dates,
    index=len(available_dates)-1  # 默认选择最新日期
)

# 获取选定日期的数据
selected_data = df[df['date'].dt.date == selected_date].iloc[0]

# 提取风险类别
risk_categories = ['利率', '地缘政治', '技术', '政策', '汇率', '环境', '社会', '衰退', '通胀']
sentiments = [selected_data[f'{cat}_情绪'] for cat in risk_categories]
attention = [selected_data[f'{cat}_关注度'] for cat in risk_categories]

# 创建图形
fig, ax = plt.subplots(figsize=(12, 8))
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 绘制散点图
colors = ['#7CB9E8'] * len(risk_categories)
scatter = plt.scatter(sentiments, attention, s=80, c=colors, alpha=0.6)

# 添加标签
for i, txt in enumerate(risk_categories):
    plt.annotate(txt, (sentiments[i], attention[i]),
                xytext=(5, 5), textcoords='offset points',
                fontsize=9)

# 绘制象限分隔线
plt.axhline(y=attention_threshold, color='gray', linestyle='--', alpha=0.5)
plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)

# 设置坐标轴
plt.xlim(-1.0, 1.0)
plt.ylim(0, 1.1)
plt.xlabel('情绪值')
plt.ylabel('关注度')

# 添加象限标注
plt.text(0.5, (1 + attention_threshold)/2, '市场强势信号\n(Ⅰ)', ha='center', va='center', alpha=0.7, fontsize=8)
plt.text(-0.5, (1 + attention_threshold)/2, '市场恐慌/风险警报\n(Ⅱ)', ha='center', va='center', alpha=0.7, fontsize=8)
plt.text(-0.5, attention_threshold/2, '潜在风险未爆发\n(Ⅲ)', ha='center', va='center', alpha=0.7, fontsize=8)
plt.text(0.5, attention_threshold/2, '冷门利好\n(Ⅳ)', ha='center', va='center', alpha=0.7, fontsize=8)

# 设置标题
plt.title(f'宏观风险象限图（日期: {selected_date.strftime("%Y-%m-%d")}）', pad=20, fontsize=14)

# 添加网格线
plt.grid(True, linestyle=':', alpha=0.3)

# 调整布局
plt.tight_layout()

# 显示图表
st.pyplot(fig)

# 显示数据表格
st.subheader("风险指标详情")
risk_data = pd.DataFrame({
    '风险类别': risk_categories,
    '情绪值': sentiments,
    '关注度': attention
}).sort_values(by=['关注度', '情绪值'], ascending=[False, False])

# 格式化数值显示
formatted_risk_data = risk_data.copy()
formatted_risk_data['情绪值'] = formatted_risk_data['情绪值'].round(3)
formatted_risk_data['关注度'] = formatted_risk_data['关注度'].round(3)

# 添加象限列
def get_quadrant(row):
    if row['情绪值'] >= 0 and row['关注度'] >= attention_threshold:
        return 'Ⅰ - 市场强势信号'
    elif row['情绪值'] < 0 and row['关注度'] >= attention_threshold:
        return 'Ⅱ - 市场恐慌/风险警报'
    elif row['情绪值'] < 0 and row['关注度'] < attention_threshold:
        return 'Ⅲ - 潜在风险未爆发'
    else:
        return 'Ⅳ - 冷门利好'

formatted_risk_data['所属象限'] = formatted_risk_data.apply(get_quadrant, axis=1)
st.dataframe(formatted_risk_data, hide_index=True) 
