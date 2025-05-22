import streamlit as st
import pandas as pd

# Set page title and basic configuration
st.set_page_config(
    page_title="酒精路跑 - 偏好調查",
    layout="wide"
)

# Add a title and information about the app
st.title("酒精路跑 - 偏好調查")
st.write("根據您的偏好，推薦適合的酒吧路線。")

# Load the CSV data
@st.cache_data
def load_data():
    # Use index_col=0 to properly handle the unnamed first column
    return pd.read_csv("all_info.csv", index_col=0)

try:
    df = load_data()
    data_loaded = True
    st.success("數據已成功加載！")
except Exception as e:
    data_loaded = False
    st.error(f"無法加載數據: {e}")
    st.stop()  # Stop execution if data loading fails

# Create the survey form based on the PDF
st.header("偏好調查表")

# 1. Time selection section
st.subheader("希望進行的時間段")
col1, col2 = st.columns(2)
with col1:
    start_time = st.selectbox(
        "請選擇開始時間",
        options=[f"{hour}:00" for hour in range(18, 24)],
        index=1  # Default to 19:00
    )
with col2:
    end_time = st.selectbox(
        "請選擇結束時間",
        options=[f"{hour}:00" for hour in range(19, 25)],  # 25 means 01:00
        index=4  # Default to 23:00
    )

st.write(f"您選擇的時間段是: {start_time} 到 {end_time}")

# 2. Alcohol type preferences
st.subheader("基酒偏好")
st.write("請選出今晚的酒精路跑，希望喝的是甚麼酒類！（可複選）")

# Create 3 columns for better layout
col1, col2, col3 = st.columns(3)

with col1:
    gin = st.checkbox("琴酒")
    rum = st.checkbox("蘭姆酒")
    vodka = st.checkbox("伏特加")
    tequila = st.checkbox("龍舌蘭")

with col2:
    vermouth = st.checkbox("香艾酒")
    brandy = st.checkbox("白蘭地")
    whiskey = st.checkbox("威士忌")
    liqueur = st.checkbox("利口酒")

with col3:
    tea_liquor = st.checkbox("茶酒")
    beer = st.checkbox("啤酒")
    plum_wine = st.checkbox("梅酒")
    wine = st.checkbox("紅白酒")
    kaoliang = st.checkbox("高粱")
    sake = st.checkbox("清酒")

# 3. Indoor/Outdoor preferences
st.subheader("室內/室外")
st.write("今晚的酒精路跑，希望在室內還是室外呢? 請選出你「首選」的選項！")
venue_type = st.radio(
    "選擇場地類型",
    options=["室內", "室外", "兩者皆可"],
    horizontal=True
)

# 4. Bar style preferences
st.subheader("酒吧風格")
st.write("請選出今晚的酒精路跑，希望在什麼風格的酒吧進行呢？（可複選）")

# Create 3 columns for better layout
col1, col2, col3 = st.columns(3)

with col1:
    beer_bar = st.checkbox("啤酒專門酒吧")
    standing_bar = st.checkbox("立飲酒吧")
    nightclub = st.checkbox("夜店型酒吧")

with col2:
    restaurant_bar = st.checkbox("餐酒館")
    refined_bar = st.checkbox("精緻酒吧")
    english_pub = st.checkbox("英式酒館")
    whiskey_bar = st.checkbox("威士忌酒吧")

with col3:
    music_bar = st.checkbox("音樂酒吧")
    view_bar = st.checkbox("觀景酒吧")
    cafe_bar = st.checkbox("咖啡餐酒館")
    tea_bar = st.checkbox("茶酒酒吧")

# 5. Music preferences
st.subheader("音樂風格")
st.write("請選出今晚的酒精路跑，希望搭配的是甚麼音樂風格呢？（可複選）")

# Create 3 columns for better layout
col1, col2, col3 = st.columns(3)

with col1:
    edm = st.checkbox("EDM")
    hiphop = st.checkbox("Hip-Hop")
    pop = st.checkbox("Pop")
    jazz = st.checkbox("Jazz")

with col2:
    rnb = st.checkbox("R&B")
    lowkey_electronic = st.checkbox("Low-key Electronic")
    lofi = st.checkbox("Lo-fi / Chillhop")
    rock = st.checkbox("Rock")

with col3:
    live_music = st.checkbox("其他（現場駐唱）")
    tropical = st.checkbox("其他（熱帶音樂）")
    any_music = st.checkbox("都可以")

# 6. Price preferences
st.subheader("價位偏好")
st.write("請填寫出今晚的酒精路跑，你預計一間酒吧，會落在何種價位")
st.caption("請填寫一個價位，我們幫你篩出正負300元區間")

price_point = st.number_input(
    "價位（新台幣）",
    min_value=0,
    max_value=5000,
    value=500,  # Default value as shown in example
    step=100
)

st.write(f"您的預算為 {price_point} 元，我們將推薦價格在 {max(0, price_point-300)} 元到 {price_point+300} 元之間的酒吧。")

# Submit button
if st.button("提交偏好調查", use_container_width=True):
    st.success("您的偏好已提交！我們將根據您的選擇為您推薦酒吧路線。")
    
    # Here we'll add the filtering logic in the next step
    # For now, we'll just show a sample of the data
    if data_loaded:
        st.subheader("基於您的偏好，以下是可能的選擇：")
        # In the next step, we'll replace this with actual filtered results
        st.dataframe(df.head(3))