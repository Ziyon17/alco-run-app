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

# Custom CSS for better styling
st.markdown("""
<style>
    .bar-card {
        background: linear-gradient(145deg, #f0f0f0, #ffffff);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #ff6b6b;
    }
    .route-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 20px;
    }
    .filter-button {
        margin: 2px;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 5px;
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
        string_columns = ['bar_style', 'music_type', 'vicinity', 'price_level_monetary']
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
    
    # 圖標映射
    style_icons = {
        '夜店型酒吧': 'music',
        '立飲酒吧': 'glass',
        '餐酒館': 'cutlery',
        '精緻酒吧': 'star',
        '啤酒專門店': 'tint',
        '威士忌酒吧': 'fire',
        '茶酒酒吧': 'leaf',
        '咖啡餐酒館': 'coffee'
    }
    
    # 添加酒吧標記
    for idx, bar in recommendations.iterrows():
        lat, lng = bar['geometry_location_lat'], bar['geometry_location_lng']
        
        # 確定酒吧風格
        bar_style = str(bar['bar_style']).split(',')[0].strip() if bar['bar_style'] != 'N/A' else '其他'
        color = style_colors.get(bar_style, style_colors['其他'])
        icon = style_icons.get(bar_style, 'info-sign')
        
        # 風格篩選
        if show_styles and bar_style not in show_styles:
            continue
        
        # 創建詳細彈出窗口
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 280px; padding: 10px;">
            <div style="background: linear-gradient(135deg, {color}, {color}aa); color: white; padding: 10px; margin: -10px -10px 10px -10px; border-radius: 5px 5px 0 0;">
                <h3 style="margin: 0; font-size: 16px;">{idx+1}. {bar['final_name']}</h3>
            </div>
            
            <div style="margin: 8px 0;">
                <strong>🏪 風格:</strong> {bar['bar_style']}<br>
                <strong>🎵 音樂:</strong> {bar['music_type']}<br>
                <strong>⭐ 評分:</strong> {bar['rating']:.1f}/5.0 ({bar['user_ratings_total']} 評論)<br>
                <strong>💰 價位:</strong> {bar['price_level_monetary']}<br>
                <strong>📍 地址:</strong> {bar['vicinity']}<br>
            </div>
            
            {'<div style="margin-top: 10px;"><strong>📞 電話:</strong> ' + str(bar['formatted_phone_number']) + '</div>' if pd.notna(bar.get('formatted_phone_number')) else ''}
        </div>
        """
        
        # 添加主要標記
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{idx+1}. {bar['final_name']} ({bar_style})",
            icon=folium.Icon(
                color='white',
                icon_color=color,
                icon=icon,
                prefix='fa'
            )
        ).add_to(m)
        
        # 添加順序標記
        folium.Marker(
            location=[lat, lng],
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
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**🏪 風格:** {bar['bar_style']}")
            st.write(f"**🎵 音樂:** {bar['music_type']}")
            st.write(f"**📍 地址:** {bar['vicinity']}")
            
        with col2:
            st.metric("⭐ 評分", f"{bar['rating']:.1f}", f"{bar['user_ratings_total']} 評論")
            if bar['price_level_monetary'] != 'N/A':
                st.metric("💰 價位", bar['price_level_monetary'])
        
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
            
            st.info(f"🚶‍♂️ 步行到下一間: {walking_time} 分鐘 ({distance:.0f}m)")
        
        st.markdown("---")
    
    # 總計信息
    st.markdown(f"""
    <div class="metric-card">
        <h3>📊 路線總計</h3>
        <p><strong>🚶‍♂️ 總步行時間:</strong> {total_walking_time} 分鐘</p>
        <p><strong>📏 總步行距離:</strong> {total_distance/1000:.1f} 公里</p>
        <p><strong>⏱️ 預估總時長:</strong> {total_walking_time + len(recommendations) * 45} 分鐘</p>
    </div>
    """, unsafe_allow_html=True)

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
            bar_styles = ['夜店型酒吧', '立飲酒吧', '餐酒館', '精緻酒吧', '啤酒專門店', 
                         '威士忌酒吧', '茶酒酒吧', '咖啡餐酒館']
            bar_style_selections = {}
            for style in bar_styles:
                bar_style_selections[style] = st.checkbox(style, key=f"bar_{style}")
        
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
            
            # 額外統計信息
            with st.expander("📈 路線分析"):
                # 風格分布圖
                style_counts = st.session_state.recommendations['bar_style'].value_counts()
                fig_pie = px.pie(
                    values=style_counts.values,
                    names=style_counts.index,
                    title="酒吧風格分布"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # 評分分布
                fig_bar = px.bar(
                    x=st.session_state.recommendations['final_name'],
                    y=st.session_state.recommendations['rating'],
                    title="各酒吧評分",
                    color=st.session_state.recommendations['rating'],
                    color_continuous_scale='viridis'
                )
                fig_bar.update_xaxis(tickangle=45)
                st.plotly_chart(fig_bar, use_container_width=True)
    
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