import streamlit as st
import pandas as pd

# Set page title and basic configuration
st.set_page_config(
    page_title="酒精路跑 - 偏好調查",
    layout="wide"
)

# Load the cleaned CSV data
@st.cache_data
def load_cleaned_data():
    """載入清理後的 CSV 數據"""
    return pd.read_csv("all_info_0522.csv")

# Load data
try:
    df = load_cleaned_data()
    st.success("✅ 數據已成功加載！")
except FileNotFoundError:
    st.error("❌ 找不到 all_info_0522.csv 文件。請確認文件名稱正確。")
    st.stop()
except Exception as e:
    st.error(f"❌ 載入數據時發生錯誤: {e}")
    st.stop()

# App title
st.title("🍺 酒精路跑 - 偏好調查")
st.write("根據您的偏好，推薦適合的酒吧路線。")

# Create the survey form
st.header("📋 偏好調查表")

# 1. Time selection
st.subheader("⏰ 希望進行的時間段")
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
        options=[f"{hour}:00" for hour in range(19, 25)],
        index=4  # Default to 23:00
    )

# 2. Alcohol preferences
st.subheader("🍻 基酒偏好")
st.write("請選出今晚的酒精路跑，希望喝的是甚麼酒類！（可複選）")

col1, col2, col3 = st.columns(3)
with col1:
    gin = st.checkbox("琴酒")
    rum = st.checkbox("蘭姆酒") 
    vodka = st.checkbox("伏特加")
    tequila = st.checkbox("龍舌蘭")
    vermouth = st.checkbox("香艾酒")

with col2:
    brandy = st.checkbox("白蘭地")
    whiskey = st.checkbox("威士忌")
    liqueur = st.checkbox("利口酒")
    tea_liquor = st.checkbox("茶酒")
    beer = st.checkbox("啤酒")

with col3:
    plum_wine = st.checkbox("梅酒")
    wine = st.checkbox("紅白酒")
    kaoliang = st.checkbox("高粱")
    sake = st.checkbox("清酒")

# 3. Indoor/Outdoor preference
st.subheader("🏠 室內/室外")
venue_type = st.radio(
    "今晚的酒精路跑，希望在室內還是室外呢？",
    options=["室內", "室外", "兩者皆可"],
    horizontal=True
)

# 4. Bar style (from actual data)
st.subheader("🍷 酒吧風格")
st.write("請選出今晚的酒精路跑，希望在什麼風格的酒吧進行呢？（可複選）")

# Get unique bar styles from data
bar_styles_raw = df['bar_style'].dropna().str.split(', ').explode().unique()
bar_styles = sorted([style.strip() for style in bar_styles_raw if style.strip()])

# Create checkboxes for bar styles
bar_style_cols = st.columns(3)
bar_selections = {}
for i, style in enumerate(bar_styles):
    with bar_style_cols[i % 3]:
        bar_selections[style] = st.checkbox(style, key=f"bar_{i}")

# 5. Music preferences (from actual data with deduplication)
st.subheader("🎵 音樂風格")
st.write("請選出今晚的酒精路跑，希望搭配的是甚麼音樂風格呢？（可複選）")

# Get unique music types from data and clean duplicates
music_types_raw = df['music_type'].dropna().str.split(', ').explode()

# Clean and deduplicate music types (handle similar entries like EDM vs EDＭ)
def clean_music_type(music):
    music = music.strip()
    # 統一 EDM 的不同寫法
    if 'EDM' in music.upper() or 'EDＭ' in music:
        return 'EDM'
    # 統一 Lo-fi 的不同寫法
    if 'LO-FI' in music.upper() or 'LOFI' in music.upper():
        return 'Lo-fi'
    return music

cleaned_music_types = music_types_raw.apply(clean_music_type)
music_types = sorted(list(set(cleaned_music_types)))

# Create checkboxes for music types
music_cols = st.columns(3)
music_selections = {}
for i, music in enumerate(music_types):
    with music_cols[i % 3]:
        music_selections[music] = st.checkbox(music, key=f"music_{i}")

# 6. Price preference
st.subheader("💰 價位偏好")
price_point = st.number_input(
    "請填寫一個價位，我們幫你篩出正負300元區間",
    min_value=0,
    max_value=5000,
    value=500,
    step=100
)

# Submit button
if st.button("🚀 提交偏好調查", use_container_width=True):
    # Collect preferences
    preferences = {
        "time_start": start_time,
        "time_end": end_time,
        "alcohol_types": {
            "琴酒": gin, "蘭姆酒": rum, "伏特加": vodka, "龍舌蘭": tequila,
            "香艾酒": vermouth, "白蘭地": brandy, "威士忌": whiskey, "利口酒": liqueur,
            "茶酒": tea_liquor, "啤酒": beer, "梅酒": plum_wine, "紅白酒": wine,
            "高粱": kaoliang, "清酒": sake
        },
        "venue_type": venue_type,
        "bar_styles": bar_selections,
        "music_types": music_selections,
        "price_point": price_point
    }
    
    # Store in session state
    st.session_state.preferences = preferences
    
    st.success("✅ 您的偏好已提交！")
    
    # Show preferences summary
    with st.expander("📋 查看您的偏好設定"):
        st.write(f"**⏰ 時間段:** {start_time} 到 {end_time}")
        st.write(f"**🏠 場地類型:** {venue_type}")
        st.write(f"**💰 價位:** {price_point} 元 (±300元)")
        
        # Selected alcohol types
        selected_alcohol = [k for k, v in preferences["alcohol_types"].items() if v]
        if selected_alcohol:
            st.write(f"**🍻 選擇的酒類:** {', '.join(selected_alcohol)}")
        
        # Selected bar styles  
        selected_bars = [k for k, v in preferences["bar_styles"].items() if v]
        if selected_bars:
            st.write(f"**🍷 選擇的酒吧風格:** {', '.join(selected_bars)}")
        
        # Selected music types
        selected_music = [k for k, v in preferences["music_types"].items() if v]
        if selected_music:
            st.write(f"**🎵 選擇的音樂風格:** {', '.join(selected_music)}")
    
    # Show data info (this should work without errors now)
    st.subheader("📊 數據概況")
    st.write(f"總共有 {len(df)} 間酒吧可供選擇")
    
    # This should now work without Arrow conversion errors
    with st.expander("🔍 數據預覽"):
        st.dataframe(df.head(3))