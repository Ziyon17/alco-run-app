import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster, MiniMap, Fullscreen
import numpy as np
from geopy.distance import geodesic
import json
from streamlit_folium import st_folium, folium_static
import math
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="🍺 酒精路跑推薦系統",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling - Dark Theme
st.markdown("""
<style>
    /* 全局暗色主題設定 */
    .stApp {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* 側邊欄暗色主題 */
    .css-1d391kg, .css-1lcbmhc, .css-17lntkn, .css-1avcm0n {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* 主要內容區域 */
    .main .block-container {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* 標題顏色 */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* 文字顏色 */
    p, span, div, label {
        color: #e0e0e0 !important;
    }
    
    .bar-card {
        background: linear-gradient(145deg, #2a2a2a, #3a3a3a) !important;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 3px 8px rgba(255, 255, 255, 0.1);
        border-left: 4px solid #ff6b6b;
        font-size: 14px;
        color: #ffffff !important;
    }
    .bar-card h3 {
        font-size: 16px;
        margin: 0 0 8px 0;
        line-height: 1.2;
        color: #ffffff !important;
    }
    
    .route-header {
        background: linear-gradient(90deg, #4a5568 0%, #553c9a 100%) !important;
        color: white !important;
        padding: 8px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 15px;
        font-size: 14px;
    }
    .route-header h2 {
        font-size: 18px;
        margin: 0 0 5px 0;
        color: #ffffff !important;
    }
    .route-header p {
        font-size: 12px;
        margin: 0;
        color: #ffffff !important;
    }
    
    .filter-button {
        margin: 2px;
    }
    
    .metric-card {
        background: #2d3748 !important;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        margin: 5px;
        font-size: 13px;
        color: #ffffff !important;
        border: 1px solid #4a5568;
    }
    .metric-card h3 {
        font-size: 16px;
        margin: 0 0 8px 0;
        color: #ffffff !important;
    }
    .metric-card p {
        margin: 3px 0;
        font-size: 13px;
        color: #e0e0e0 !important;
    }
    
    /* 調整Streamlit內建組件的字體大小和顏色 */
    .stMetric {
        font-size: 12px !important;
        background-color: #2d3748 !important;
        padding: 10px !important;
        border-radius: 8px !important;
        border: 1px solid #4a5568 !important;
    }
    .stMetric > div > div > div {
        font-size: 14px !important;
        color: #ffffff !important;
    }
    .stMetric label {
        font-size: 12px !important;
        color: #a0a0a0 !important;
    }
    
    /* 調整文字內容 */
    .stMarkdown p {
        font-size: 13px;
        line-height: 1.4;
        margin-bottom: 8px;
        color: #e0e0e0 !important;
    }
    
    /* 調整info框 */
    .stInfo {
        font-size: 12px !important;
        padding: 8px !important;
        background-color: #1a365d !important;
        color: #ffffff !important;
        border: 1px solid #2c5282 !important;
    }
    
    /* 按鈕樣式 */
    .stButton > button {
        background-color: #4299e1 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
    }
    .stButton > button:hover {
        background-color: #3182ce !important;
        color: #ffffff !important;
    }
    
    /* 主要按鈕 */
    .stButton > button[kind="primary"] {
        background-color: #e53e3e !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #c53030 !important;
    }
    
    /* 選擇框和輸入框 */
    .stSelectbox > div > div {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        border: 1px solid #4a5568 !important;
    }
    
    .stSlider > div > div > div {
        color: #ffffff !important;
    }
    
    /* Checkbox樣式 */
    .stCheckbox > label {
        color: #e0e0e0 !important;
    }
    
    /* Radio按鈕樣式 */
    .stRadio > label {
        color: #e0e0e0 !important;
    }
    
    /* 展開器樣式 */
    .streamlit-expanderHeader {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        border: 1px solid #4a5568 !important;
    }
    .streamlit-expanderContent {
        background-color: #1a202c !important;
        border: 1px solid #4a5568 !important;
    }
    
    /* 警告和成功訊息 */
    .stWarning {
        background-color: #744210 !important;
        color: #ffffff !important;
        border: 1px solid #d69e2e !important;
    }
    .stSuccess {
        background-color: #22543d !important;
        color: #ffffff !important;
        border: 1px solid #38a169 !important;
    }
    
    /* 步行信息框樣式調整 */
    .walk-info {
        background: #1e3a8a !important;
        color: #ffffff !important;
        padding: 6px 10px;
        border-radius: 5px;
        margin: 8px 0;
        border-left: 3px solid #3b82f6 !important;
    }
    
    /* 分隔線樣式 */
    hr {
        border-color: #4a5568 !important;
    }
    
    /* 信息圖標樣式 */
    .info-icon {
        display: inline-block;
        width: 16px;
        height: 16px;
        background-color: #3182ce !important;
        color: white;
        border-radius: 50%;
        text-align: center;
        font-size: 12px;
        line-height: 16px;
        margin-left: 8px;
        cursor: help;
        position: relative;
        font-weight: bold;
    }
    
    /* 懸停提示框樣式 */
    .info-icon .tooltip {
        visibility: hidden;
        width: 220px;
        background-color: #1a202c !important;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -110px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
        line-height: 1.4;
        box-shadow: 0 2px 8px rgba(255,255,255,0.1);
        border: 1px solid #4a5568 !important;
    }
    
    .info-icon .tooltip::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #1a202c transparent transparent transparent;
    }
    
    .info-icon:hover .tooltip {
        visibility: visible;
        opacity: 1;
    }
    
    /* 調整checkbox容器樣式 */
    .checkbox-with-info {
        display: flex;
        align-items: center;
        margin-bottom: 4px;
    }
    
    /* 表格樣式 */
    .dataframe {
        background-color: #2d3748 !important;
        color: #ffffff !important;
    }
    
    /* Plotly圖表背景 */
    .plotly {
        background-color: #1a202c !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """載入並預處理酒吧數據"""
    try:
        df = pd.read_csv("all_info_0522.csv")
        # 數據清理
        df = df.dropna(subset=['final_name', 'geometry_location_lat', 'geometry_location_lng'])
        df['price_level'] = df['price_level'].fillna(2)
        df['rating'] = df['rating'].fillna(3.5)
        
        # 處理字符串字段中的NaN
        string_columns = ['bar_style', 'music_type', 'vicinity', 'price_level_monetary', 'top_3_selection']
        for col in string_columns:
            df[col] = df[col].fillna('N/A')
            
        return df
    except FileNotFoundError:
        st.error("❌ 找不到 all_info_0522.csv 文件")
        return pd.DataFrame()

def calculate_advanced_score(bar, preferences):
    """進階推薦算法"""
    score = 0
    max_score = 1.0
    
    # 價格匹配 (35% 權重)
    price_target = preferences.get('price_point', 500)
    if pd.notna(bar['price_level']) and bar['price_level'] > 0:
        estimated_price = bar['price_level'] * 400  # 估算實際價格
        price_diff = abs(estimated_price - price_target)
        price_score = max(0, 1 - (price_diff / 600))  # 600元內差異可接受
        score += price_score * 0.35
    
    # 風格匹配 (25% 權重)
    selected_styles = [k for k, v in preferences.get('bar_styles', {}).items() if v]
    if selected_styles and bar['bar_style'] != 'N/A':
        bar_styles = str(bar['bar_style']).split(', ')
        style_matches = sum(1 for style in selected_styles if any(s.strip() == style for s in bar_styles))
        if style_matches > 0:
            score += (style_matches / len(selected_styles)) * 0.25
    
    # 音樂匹配 (20% 權重)
    selected_music = [k for k, v in preferences.get('music_types', {}).items() if v]
    if selected_music and bar['music_type'] != 'N/A':
        music_types = str(bar['music_type']).split(', ')
        music_matches = sum(1 for music in selected_music if any(m.strip() == music for m in music_types))
        if music_matches > 0:
            score += (music_matches / len(selected_music)) * 0.20
    
    # 評分加成 (15% 權重)
    if pd.notna(bar['rating']) and bar['rating'] > 0:
        rating_normalized = (bar['rating'] - 1) / 4  # 1-5 標準化到 0-1
        score += rating_normalized * 0.15
    
    # 熱門度加成 (5% 權重)
    if pd.notna(bar['user_ratings_total']) and bar['user_ratings_total'] > 0:
        popularity_score = min(1.0, math.log(bar['user_ratings_total'] + 1) / 10)
        score += popularity_score * 0.05
    
    return min(score, max_score)

def optimize_route(recommendations):
    """簡單的路線優化 - 最近鄰居法"""
    if len(recommendations) <= 2:
        return recommendations
    
    # 起點選擇評分最高的
    optimized = [recommendations.iloc[0]]
    remaining = list(range(1, len(recommendations)))
    current_idx = 0
    
    while remaining:
        current_bar = recommendations.iloc[current_idx]
        min_distance = float('inf')
        next_idx = None
        
        for idx in remaining:
            candidate = recommendations.iloc[idx]
            distance = geodesic(
                (current_bar['geometry_location_lat'], current_bar['geometry_location_lng']),
                (candidate['geometry_location_lat'], candidate['geometry_location_lng'])
            ).meters
            
            if distance < min_distance:
                min_distance = distance
                next_idx = idx
        
        optimized.append(recommendations.iloc[next_idx])
        remaining.remove(next_idx)
        current_idx = next_idx
    
    return pd.DataFrame(optimized).reset_index(drop=True)

def get_smart_recommendations(df, preferences, top_n=6):
    """智能推薦系統"""
    # 計算推薦分數
    df['recommendation_score'] = df.apply(
        lambda x: calculate_advanced_score(x, preferences), axis=1
    )
    
    # 選擇前N個候選
    candidates = df.nlargest(top_n * 2, 'recommendation_score')
    
    # 地理分散性考慮 - 避免所有酒吧都在同一區域
    final_recommendations = []
    used_locations = []
    min_distance = 300  # 最少300米間距
    
    for _, bar in candidates.iterrows():
        if len(final_recommendations) >= top_n:
            break
            
        current_loc = (bar['geometry_location_lat'], bar['geometry_location_lng'])
        
        # 檢查與已選酒吧的距離
        too_close = False
        for used_loc in used_locations:
            if geodesic(current_loc, used_loc).meters < min_distance:
                too_close = True
                break
        
        if not too_close:
            final_recommendations.append(bar)
            used_locations.append(current_loc)
    
    # 如果地理分散後數量不足，補充剩餘的高分酒吧
    if len(final_recommendations) < top_n:
        remaining_need = top_n - len(final_recommendations)
        remaining_bars = candidates[~candidates.index.isin([bar.name for bar in final_recommendations])]
        final_recommendations.extend(remaining_bars.head(remaining_need).to_dict('records'))
    
    result_df = pd.DataFrame(final_recommendations)
    
    # 路線優化
    if len(result_df) > 2:
        result_df = optimize_route(result_df)
    
    return result_df

def calculate_walking_time(lat1, lon1, lat2, lon2, speed_kmh=4.5):
    """計算步行時間，考慮不同步行速度"""
    distance = geodesic((lat1, lon1), (lat2, lon2)).meters
    speed_ms = (speed_kmh * 1000) / 60  # 轉換為 m/min
    walking_time = distance / speed_ms
    return math.ceil(walking_time)

def create_interactive_map(recommendations, show_styles=None):
    """創建進階互動地圖"""
    if recommendations.empty:
        return None
    
    # 地圖中心點
    center_lat = recommendations['geometry_location_lat'].mean()
    center_lng = recommendations['geometry_location_lng'].mean()
    
    # 創建地圖
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=14,
        tiles='OpenStreetMap'
    )
    
    # 酒吧風格顏色映射
    style_colors = {
        '夜店型酒吧': '#ff4757',      # 紅色
        '立飲酒吧': '#3742fa',        # 藍色  
        '餐酒館': '#2ed573',          # 綠色
        '精緻酒吧': '#8b4aa3',        # 紫色
        '啤酒專門店': '#ffa502',      # 橙色
        '威士忌酒吧': '#8b0000',      # 深紅
        '茶酒酒吧': '#90EE90',        # 淺綠
        '咖啡餐酒館': '#d2691e',      # 棕色
        '其他': '#747d8c'             # 灰色
    }
    
    # 添加酒吧標記
    for idx, bar in recommendations.iterrows():
        lat, lng = bar['geometry_location_lat'], bar['geometry_location_lng']
        
        # 確定酒吧風格
        bar_style = str(bar['bar_style']).split(',')[0].strip() if bar['bar_style'] != 'N/A' else '其他'
        color = style_colors.get(bar_style, style_colors['其他'])
        
        # 風格篩選
        if show_styles and bar_style not in show_styles:
            continue
        
        # 創建詳細彈出窗口
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 350px; padding: 10px;">
            <div style="background: linear-gradient(135deg, {color}, {color}aa); color: white; padding: 10px; margin: -10px -10px 10px -10px; border-radius: 5px 5px 0 0;">
                <h3 style="margin: 0; font-size: 16px;">{idx+1}. {bar['final_name']}</h3>
            </div>
            
            <div style="margin: 8px 0;">
                <strong>🏪 風格:</strong> {bar['bar_style']}<br>
                <strong>🎵 音樂:</strong> {bar['music_type']}<br>
                <strong>⭐ 評分:</strong> {bar['rating']:.1f}/5.0 ({bar['user_ratings_total']} 評論)<br>
                <strong>💰 價位:</strong> {bar['price_level_monetary']}<br>
                <strong>📍 地址:</strong> {bar['vicinity']}<br>
        """
        
        # 新增人氣酒單到彈出窗口
        if pd.notna(bar.get('top_3_selection')) and bar['top_3_selection'] != 'N/A':
            drinks = str(bar['top_3_selection']).split(', ')
            drinks_html = '<br>'.join([f"• {drink.strip()}" for drink in drinks[:3]])  # 顯示所有酒單，但限制格式
            popup_html += f"""
                <div style='margin: 8px 0; padding: 8px; background: #f5f5f5; border-radius: 5px; border-left: 3px solid {color};'>
                    <strong>🍹 人氣酒單:</strong><br>
                    <div style='font-size: 11px; color: #333; margin-top: 4px; line-height: 1.3;'>{drinks_html}</div>
                </div>
            """
        
        popup_html += "</div>"
        
        # 電話資訊
        if pd.notna(bar.get('formatted_phone_number')):
            popup_html += f'<div style="margin-top: 10px;"><strong>📞 電話:</strong> {str(bar["formatted_phone_number"])}</div>'
        
        popup_html += "</div>"
        
        # 只添加順序標記（移除主要圖標標記）
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{idx+1}. {bar['final_name']} ({bar_style})",
            icon=folium.DivIcon(
                html=f'''
                <div style="
                    font-size: 12px; 
                    color: white; 
                    font-weight: bold; 
                    text-align: center; 
                    background-color: {color}; 
                    border: 2px solid white;
                    border-radius: 50%; 
                    width: 25px; 
                    height: 25px; 
                    line-height: 21px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                ">{idx+1}</div>
                ''',
                icon_size=(25, 25),
                icon_anchor=(12, 12)
            )
        ).add_to(m)
    
    # 添加路線
    if len(recommendations) > 1:
        locations = [(row['geometry_location_lat'], row['geometry_location_lng']) 
                    for idx, row in recommendations.iterrows()]
        
        folium.PolyLine(
            locations=locations,
            weight=4,
            color='#3498db',
            opacity=0.8,
            dash_array='10, 5',
            tooltip="推薦路線"
        ).add_to(m)
    
    # 添加插件
    MiniMap().add_to(m)
    Fullscreen().add_to(m)
    
    return m

def display_route_panel(recommendations, preferences):
    """顯示左側路線面板"""
    if recommendations.empty:
        st.warning("⚠️ 暫無推薦結果")
        return
    
    # 路線標題
    st.markdown(f"""
    <div class="route-header">
        <h2>🍺 您的酒精路跑路線規劃</h2>
        <p>⏰ {preferences.get('time_start', '19:00')} - {preferences.get('time_end', '23:00')} | 🏪 {len(recommendations)} 間酒吧</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 計算總體統計
    total_walking_time = 0
    total_distance = 0
    
    for idx, bar in recommendations.iterrows():
        # 酒吧卡片
        st.markdown(f"""
        <div class="bar-card">
            <h3>🏅 {idx+1}. {bar['final_name']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 詳細信息
        col1, col2 = st.columns([3, 1])  # 調整比例讓酒單資訊有更多空間
        
        with col1:
            st.markdown(f"<p style='font-size: 12px; margin: 2px 0; color: #e0e0e0;'><strong style='color: #ffffff;'>🏪 風格:</strong> {bar['bar_style']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 12px; margin: 2px 0; color: #e0e0e0;'><strong style='color: #ffffff;'>🎵 音樂:</strong> {bar['music_type']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 12px; margin: 2px 0; color: #e0e0e0;'><strong style='color: #ffffff;'>📍 地址:</strong> {bar['vicinity']}</p>", unsafe_allow_html=True)
            
            # 新增人氣酒單資訊
            if pd.notna(bar.get('top_3_selection')) and bar['top_3_selection'] != 'N/A':
                # 處理酒單資訊，分割成個別項目
                drinks = str(bar['top_3_selection']).split(', ')
                drinks_text = '<br>'.join([f"• {drink.strip()}" for drink in drinks])
                st.markdown(f"""
                <div style='font-size: 12px; margin: 6px 0; padding: 8px; background: #2d3748; border-radius: 5px; border: 1px solid #4a5568;'>
                    <strong style='color: #ffffff;'>🍹 人氣酒單:</strong><br>
                    <div style='color: #e0e0e0; margin-top: 4px; line-height: 1.4;'>{drinks_text}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='font-size: 12px; margin: 2px 0; color: #e0e0e0;'><strong style='color: #ffffff;'>🍹 人氣酒單:</strong> 暫無資料</p>", unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div style='text-align: center; padding: 5px; background: #2d3748; border-radius: 5px; margin: 2px 0; border: 1px solid #4a5568;'>
                <div style='font-size: 11px; color: #a0a0a0;'>⭐ 評分</div>
                <div style='font-size: 16px; font-weight: bold; color: #ffffff;'>{bar['rating']:.1f}</div>
                <div style='font-size: 10px; color: #cbd5e0;'>{bar['user_ratings_total']} 評論</div>
            </div>
            """, unsafe_allow_html=True)
            
            if bar['price_level_monetary'] != 'N/A':
                st.markdown(f"""
                <div style='text-align: center; padding: 5px; background: #2d3748; border-radius: 5px; margin: 2px 0; border: 1px solid #4a5568;'>
                    <div style='font-size: 11px; color: #a0a0a0;'>💰 價位</div>
                    <div style='font-size: 14px; font-weight: bold; color: #ffffff;'>{bar['price_level_monetary']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 到下一間的路線信息
        if idx < len(recommendations) - 1:
            next_bar = recommendations.iloc[idx + 1]
            walking_time = calculate_walking_time(
                bar['geometry_location_lat'], bar['geometry_location_lng'],
                next_bar['geometry_location_lat'], next_bar['geometry_location_lng']
            )
            distance = geodesic(
                (bar['geometry_location_lat'], bar['geometry_location_lng']),
                (next_bar['geometry_location_lat'], next_bar['geometry_location_lng'])
            ).meters
            
            total_walking_time += walking_time
            total_distance += distance
            
            st.markdown(f"""
            <div style='background: #1e3a8a; padding: 6px 10px; border-radius: 5px; margin: 8px 0; border-left: 3px solid #3b82f6; color: #ffffff;'>
                <span style='font-size: 12px; color: #ffffff;'>🚶‍♂️ 步行到下一間: <strong>{walking_time} 分鐘</strong> ({distance:.0f}m)</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 10px 0; border: 1px solid #4a5568;'>", unsafe_allow_html=True)

def main():
    st.title("🍺 酒精路跑智能推薦系統")
    
    # 載入數據
    df = load_data()
    if df.empty:
        st.stop()
    
    # 初始化 session state
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {}
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = pd.DataFrame()
    
    # 側邊欄 - 偏好設定
    with st.sidebar:
        st.title("🎯 個人化設定")
        
        with st.expander("⏰ 時間設定", expanded=True):
            start_time = st.selectbox("開始時間", [f"{h:02d}:00" for h in range(18, 24)], index=1)
            end_time = st.selectbox("結束時間", [f"{h:02d}:00" for h in range(19, 25)], index=4)
        
        with st.expander("🍷 酒吧風格偏好", expanded=True):
            # 酒吧風格和定義
            bar_styles_info = {
                '夜店型酒吧': '結合舞池與DJ音樂及調酒的派對場地',
                '立飲酒吧': '無座位或少座位，站著飲酒',
                '餐酒館': '主打特色美食與酒搭配的餐廳酒吧',
                '精緻酒吧': '特色裝潢打造氛圍結合精緻調酒',
                '啤酒專門店': '主打各式精釀啤酒供應的場所',
                '威士忌酒吧': '主打威士忌相關酒品為主的特色酒吧',
                '茶酒酒吧': '結合茶飲與酒精創意調酒的酒吧',
                '咖啡餐酒館': '白天咖啡廳，夜晚供酒的複合式店家'
            }
            
            bar_style_selections = {}
            for style, definition in bar_styles_info.items():
                # 使用HTML創建checkbox和信息圖標的組合
                col1, col2 = st.columns([10, 1])
                with col1:
                    bar_style_selections[style] = st.checkbox(style, key=f"bar_{style}")
                with col2:
                    st.markdown(f"""
                    <div class="info-icon">
                        i
                        <span class="tooltip">{definition}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        with st.expander("🎵 音樂風格偏好", expanded=False):
            music_types = ['Hip-Hop', 'EDM', 'Jazz', 'Lo-fi', 'Rock', 'R&B', 'Pop', 'Electronic']
            music_selections = {}
            for music in music_types:
                music_selections[music] = st.checkbox(music, key=f"music_{music}")
        
        with st.expander("💰 預算設定", expanded=True):
            price_point = st.slider("單間預算 (NT$)", 200, 2000, 500, 50)
            
        with st.expander("🏠 環境偏好", expanded=False):
            venue_type = st.radio("場地偏好", ["室內", "室外", "兩者皆可"])
            ambiance = st.selectbox("氛圍偏好", ["熱鬧", "安靜", "適中"])
        
        # 更新推薦按鈕
        if st.button("🚀 生成推薦路線", use_container_width=True, type="primary"):
            preferences = {
                'time_start': start_time,
                'time_end': end_time,
                'bar_styles': bar_style_selections,
                'music_types': music_selections,
                'price_point': price_point,
                'venue_type': venue_type
            }
            
            st.session_state.preferences = preferences
            st.session_state.recommendations = get_smart_recommendations(df, preferences)
            st.success("✅ 推薦路線已生成！")
            st.rerun()
    
    # 主要內容區域
    if not st.session_state.recommendations.empty:
        # 創建主要布局
        col1, col2 = st.columns([1, 2])
        
        with col1:
            display_route_panel(st.session_state.recommendations, st.session_state.preferences)
        
        with col2:
            st.header("🗺️ 互動式路線地圖")
            
            # 風格篩選器
            st.subheader("🎛️ 地圖篩選器")
            filter_cols = st.columns(4)
            
            selected_filter = None
            with filter_cols[0]:
                if st.button("🌃 夜店型", use_container_width=True):
                    selected_filter = ['夜店型酒吧']
            with filter_cols[1]:
                if st.button("🍺 立飲", use_container_width=True):
                    selected_filter = ['立飲酒吧']
            with filter_cols[2]:
                if st.button("🍽️ 餐酒館", use_container_width=True):
                    selected_filter = ['餐酒館']
            with filter_cols[3]:
                if st.button("✨ 精緻", use_container_width=True):
                    selected_filter = ['精緻酒吧']
            
            # 創建並顯示地圖
            route_map = create_interactive_map(st.session_state.recommendations, selected_filter)
            if route_map:
                folium_static(route_map, width=700, height=500)
    
    else:
        # 歡迎頁面
        st.markdown("""
        ## 🎉 歡迎使用酒精路跑智能推薦系統！
        
        ### 🚀 系統特色：
        - **🎯 個人化推薦**: 根據您的偏好智能匹配酒吧
        - **🗺️ 路線優化**: 自動規劃最佳步行路線
        - **📊 數據驅動**: 基於真實評價和數據分析
        - **🎛️ 互動篩選**: 即時篩選不同風格的酒吧
        
        ### 📋 使用指南：
        1. **設定偏好**: 在左側面板選擇您的偏好
        2. **生成路線**: 點擊「生成推薦路線」按鈕
        3. **查看結果**: 左側查看詳細路線，右側查看地圖
        4. **互動篩選**: 使用地圖下方的按鈕篩選不同風格
        
        👈 **請先在左側設定您的偏好來開始！**
        """)
        
        # 顯示數據概覽
        st.subheader("📊 平台數據概覽")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏪 總酒吧數", len(df))
        with col2:
            st.metric("⭐ 平均評分", f"{df['rating'].mean():.1f}")
        with col3:
            unique_styles = len(df['bar_style'].str.split(', ').explode().unique())
            st.metric("🎭 風格種類", unique_styles)
        with col4:
            avg_price = df['price_level'].mean() * 400
            st.metric("💰 平均價位", f"NT${avg_price:.0f}")

if __name__ == "__main__":
    main()