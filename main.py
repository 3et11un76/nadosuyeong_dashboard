# ==============================================================================
# 🌱 극지식물(나도수영) 최적 EC 농도 연구 대시보드
# ✨ Premium Design Edition
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import unicodedata
import io

# ==============================================================================
# 0. 페이지 설정 및 프리미엄 CSS
# ==============================================================================
st.set_page_config(
    page_title="🌱 극지식물 최적 EC 농도 연구",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 프리미엄 CSS 스타일
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');

/* 기본 폰트 설정 */
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 배경 그라데이션 */
.stApp {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
}

/* 히어로 섹션 */
.hero-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    border-radius: 20px;
    padding: 40px;
    margin-bottom: 30px;
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
    position: relative;
    overflow: hidden;
}

.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 900;
    color: white;
    text-shadow: 2px 2px 20px rgba(0,0,0,0.3);
    margin-bottom: 10px;
    position: relative;
    z-index: 1;
}

.hero-subtitle {
    font-size: 1.3rem;
    color: rgba(255,255,255,0.9);
    font-weight: 300;
    position: relative;
    z-index: 1;
}

/* 글래스모피즘 카드 */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 25px;
    margin: 15px 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}

.glass-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
    border-color: rgba(102, 126, 234, 0.5);
}

/* 네온 글로우 효과 */
.neon-text {
    color: #00ff88;
    text-shadow: 0 0 10px #00ff88, 0 0 20px #00ff88, 0 0 40px #00ff88;
}

.neon-blue {
    color: #00d4ff;
    text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff;
}

.neon-purple {
    color: #bf00ff;
    text-shadow: 0 0 10px #bf00ff, 0 0 20px #bf00ff;
}

/* 메트릭 카드 */
.metric-card {
    background: linear-gradient(145deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: scale(1.05);
    box-shadow: 0 15px 50px rgba(102, 126, 234, 0.4);
}

.metric-value {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #00ff88, #00d4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.metric-label {
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 10px;
    font-weight: 500;
}

/* EC 뱃지 */
.ec-badge {
    display: inline-block;
    padding: 8px 20px;
    border-radius: 30px;
    font-weight: 700;
    font-size: 1.1rem;
    margin: 5px;
    transition: all 0.3s ease;
}

.ec-badge:hover {
    transform: scale(1.1);
}

.ec-1 { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
.ec-2 { background: linear-gradient(135deg, #00b894, #00cec9); color: white; box-shadow: 0 0 20px rgba(0, 184, 148, 0.5); }
.ec-4 { background: linear-gradient(135deg, #fd79a8, #e84393); color: white; }
.ec-8 { background: linear-gradient(135deg, #a29bfe, #6c5ce7); color: white; }

/* 섹션 타이틀 */
.section-title {
    font-size: 2rem;
    font-weight: 700;
    color: white;
    margin: 40px 0 20px 0;
    padding-bottom: 15px;
    border-bottom: 3px solid;
    border-image: linear-gradient(90deg, #667eea, #764ba2, transparent) 1;
}

/* 인사이트 박스 */
.insight-box {
    background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.1));
    border-left: 4px solid #00ff88;
    border-radius: 0 15px 15px 0;
    padding: 20px 25px;
    margin: 20px 0;
    color: rgba(255, 255, 255, 0.9);
}

.warning-box {
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(254, 202, 87, 0.1));
    border-left: 4px solid #ff6b6b;
    border-radius: 0 15px 15px 0;
    padding: 20px 25px;
    margin: 20px 0;
    color: rgba(255, 255, 255, 0.9);
}

/* 결론 카드 */
.conclusion-card {
    background: linear-gradient(135deg, rgba(0, 255, 136, 0.15), rgba(0, 184, 148, 0.15));
    border: 2px solid rgba(0, 255, 136, 0.3);
    border-radius: 20px;
    padding: 30px;
    margin: 20px 0;
}

.danger-card {
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.15), rgba(238, 82, 83, 0.15));
    border: 2px solid rgba(255, 107, 107, 0.3);
    border-radius: 20px;
    padding: 30px;
    margin: 20px 0;
}

/* 테이블 스타일 */
.styled-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    overflow: hidden;
}

.styled-table th {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 15px;
    font-weight: 600;
}

.styled-table td {
    padding: 15px;
    color: rgba(255, 255, 255, 0.9);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.styled-table tr:hover td {
    background: rgba(102, 126, 234, 0.1);
}

/* 애니메이션 */
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.floating {
    animation: float 3s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

.pulse {
    animation: pulse 2s ease-in-out infinite;
}

/* 사이드바 스타일 */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}

section[data-testid="stSidebar"] .stMarkdown {
    color: rgba(255, 255, 255, 0.9);
}

/* 탭 스타일 */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 10px;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 10px;
    color: rgba(255, 255, 255, 0.7);
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
}

/* Expander 스타일 */
.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    color: white;
}

/* 스크롤바 */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. 학교 정보 설정 (EC 오름차순 정렬)
# ==============================================================================
SCHOOL_INFO = {
    "송도고": {"ec_target": 1.0, "color": "#667eea", "order": 1, "emoji": "🔵"},
    "하늘고": {"ec_target": 2.0, "color": "#00b894", "order": 2, "emoji": "🟢"},  # 최적
    "아라고": {"ec_target": 4.0, "color": "#e84393", "order": 3, "emoji": "🔴"},
    "동산고": {"ec_target": 8.0, "color": "#6c5ce7", "order": 4, "emoji": "🟣"},
}

SCHOOL_NAMES_BY_EC = sorted(SCHOOL_INFO.keys(), key=lambda x: SCHOOL_INFO[x]["ec_target"])
SCHOOL_NAMES = list(SCHOOL_INFO.keys())

# ==============================================================================
# 2. 한글 파일명 안전 인식 함수
# ==============================================================================
def normalize_match(target: str, candidate: str) -> bool:
    target_nfc = unicodedata.normalize("NFC", target)
    target_nfd = unicodedata.normalize("NFD", target)
    candidate_nfc = unicodedata.normalize("NFC", candidate)
    candidate_nfd = unicodedata.normalize("NFD", candidate)
    return target_nfc == candidate_nfc or target_nfd == candidate_nfd


def find_file(directory: Path, keyword: str, extension: str) -> Path | None:
    if not directory.exists():
        return None
    for file_path in directory.iterdir():
        if file_path.suffix.lower() == extension:
            file_name = file_path.stem
            keyword_nfc = unicodedata.normalize("NFC", keyword)
            keyword_nfd = unicodedata.normalize("NFD", keyword)
            file_name_nfc = unicodedata.normalize("NFC", file_name)
            file_name_nfd = unicodedata.normalize("NFD", file_name)
            if keyword_nfc in file_name_nfc or keyword_nfd in file_name_nfd:
                return file_path
    return None

# ==============================================================================
# 3. 데이터 로딩 함수
# ==============================================================================
@st.cache_data
def load_environment_data() -> dict[str, pd.DataFrame]:
    data_dir = Path("data")
    env_data = {}
    
    if not data_dir.exists():
        return env_data
    
    for file_path in data_dir.iterdir():
        if file_path.suffix.lower() == ".csv":
            file_name_nfc = unicodedata.normalize("NFC", file_path.stem)
            if "환경" in file_name_nfc:
                for school in SCHOOL_NAMES:
                    school_nfc = unicodedata.normalize("NFC", school)
                    if school_nfc in file_name_nfc and school not in env_data:
                        try:
                            df = pd.read_csv(file_path, encoding="utf-8-sig")
                            df.columns = [unicodedata.normalize("NFC", col.strip().lower()) for col in df.columns]
                            env_data[school] = df
                        except Exception as e:
                            pass
    
    return env_data


@st.cache_data
def load_growth_data() -> dict[str, pd.DataFrame]:
    data_dir = Path("data")
    growth_data = {}
    
    if not data_dir.exists():
        return growth_data
    
    for file_path in data_dir.iterdir():
        if file_path.suffix.lower() == ".csv":
            file_name_nfc = unicodedata.normalize("NFC", file_path.stem)
            if "생육" in file_name_nfc:
                for school in SCHOOL_NAMES:
                    school_nfc = unicodedata.normalize("NFC", school)
                    if school_nfc in file_name_nfc and school not in growth_data:
                        try:
                            df = pd.read_csv(file_path, encoding="utf-8-sig")
                            df.columns = [unicodedata.normalize("NFC", col.strip()) for col in df.columns]
                            growth_data[school] = df
                        except Exception as e:
                            pass
    
    return growth_data


def get_column_safe(df: pd.DataFrame, keywords: list[str]) -> str | None:
    for col in df.columns:
        col_lower = col.lower()
        for kw in keywords:
            if kw in col_lower:
                return col
    return None

# ==============================================================================
# 4. 메인 앱
# ==============================================================================
def main():
    # =========================================================================
    # 히어로 섹션
    # =========================================================================
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🌱 극지식물 최적 EC 농도 연구</div>
        <div class="hero-subtitle">4개 학교 공동 실험 · 나도수영(Oxyria digyna) 생육 최적화 분석</div>
    </div>
    """, unsafe_allow_html=True)
    
    # -------------------------------------------------------------------------
    # 사이드바
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.markdown("## 🎛️ 컨트롤 패널")
        st.markdown("---")
        
        school_options = ["전체"] + SCHOOL_NAMES_BY_EC
        selected_school = st.selectbox("🏫 학교 선택", school_options)
        
        st.markdown("---")
        st.markdown("### 🧪 EC 실험 조건")
        
        for school in SCHOOL_NAMES_BY_EC:
            info = SCHOOL_INFO[school]
            if school == "하늘고":
                st.markdown(f"""
                <div class="ec-badge ec-2" style="display: block; text-align: center;">
                    ⭐ {school} · EC {info['ec_target']}
                </div>
                """, unsafe_allow_html=True)
            else:
                ec_class = f"ec-{int(info['ec_target'])}"
                st.markdown(f"""
                <div class="ec-badge {ec_class}" style="display: block; text-align: center;">
                    {info['emoji']} {school} · EC {info['ec_target']}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 💡 핵심 질문")
        st.info("극지식물이 가장 잘 자라는 **최적 EC 농도**는?")
    
    # -------------------------------------------------------------------------
    # 데이터 로딩
    # -------------------------------------------------------------------------
    with st.spinner(""):
        env_data = load_environment_data()
        growth_data = load_growth_data()
    
    if not env_data and not growth_data:
        st.error("❌ 데이터를 찾을 수 없습니다. `data/` 폴더를 확인해주세요.")
        return
    
    filtered_schools = SCHOOL_NAMES_BY_EC if selected_school == "전체" else [selected_school]
    
    # -------------------------------------------------------------------------
    # 탭 구성
    # -------------------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["📖 연구 개요", "🌡️ 환경 분석", "📊 생육 결과"])
    
    # =========================================================================
    # TAB 1: 연구 개요
    # =========================================================================
    with tab1:
        st.markdown('<div class="section-title">🎯 연구 목적</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="glass-card">
                <h3 style="color: #00ff88; margin-bottom: 15px;">왜 이 연구를 시작했나요?</h3>
                <p style="color: rgba(255,255,255,0.85); line-height: 1.8; font-size: 1.1rem;">
                    극지식물 <strong style="color: #00d4ff;">나도수영(Oxyria digyna)</strong>은 극지방 및 고산지대에서 자생하는 
                    귀중한 식물입니다. 기후 변화 연구의 중요한 지표 식물로서, 이들의 <strong style="color: #00ff88;">최적 생육 조건</strong>을 
                    규명하는 것은 매우 중요합니다.
                </p>
                <br>
                <p style="color: rgba(255,255,255,0.85); line-height: 1.8; font-size: 1.1rem;">
                    본 연구에서는 <strong style="color: #bf00ff;">EC(전기전도도)</strong> 농도가 식물 생육에 미치는 영향을 
                    4개 학교 공동 실험을 통해 분석하고, <strong style="color: #00ff88;">최적의 양분 농도</strong>를 도출하고자 합니다.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 4rem; margin-bottom: 10px;">🔬</div>
                <h4 style="color: #00d4ff;">핵심 변수</h4>
                <p style="color: rgba(255,255,255,0.7);">EC · pH · 온도 · 습도</p>
                <div style="margin-top: 20px; font-size: 3rem;">🌿</div>
                <h4 style="color: #00ff88;">대상 식물</h4>
                <p style="color: rgba(255,255,255,0.7);">나도수영 (Oxyria digyna)</p>
            </div>
            """, unsafe_allow_html=True)
        
        # EC란 무엇인가?
        st.markdown('<div class="section-title">⚡ EC(전기전도도)란?</div>', unsafe_allow_html=True)
        
        col_ec1, col_ec2, col_ec3 = st.columns(3)
        
        with col_ec1:
            st.markdown("""
            <div class="glass-card" style="text-align: center; border-top: 3px solid #00ff88;">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">💧</div>
                <h4 style="color: #00ff88;">양분 농도 지표</h4>
                <p style="color: rgba(255,255,255,0.7); font-size: 0.95rem;">
                    물 속에 녹아있는 비료(양분)의 농도를 전기 전도율로 측정한 값
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_ec2:
            st.markdown("""
            <div class="glass-card" style="text-align: center; border-top: 3px solid #00d4ff;">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">⚠️</div>
                <h4 style="color: #00d4ff;">너무 높으면?</h4>
                <p style="color: rgba(255,255,255,0.7); font-size: 0.95rem;">
                    삼투압 현상으로 뿌리가 물을 흡수하지 못해 <strong>탈수 증상</strong> 발생
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_ec3:
            st.markdown("""
            <div class="glass-card" style="text-align: center; border-top: 3px solid #bf00ff;">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">📉</div>
                <h4 style="color: #bf00ff;">너무 낮으면?</h4>
                <p style="color: rgba(255,255,255,0.7); font-size: 0.95rem;">
                    양분 부족으로 성장 저하 및 생산성 감소
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # 학교별 실험 조건
        st.markdown('<div class="section-title">🏫 학교별 실험 조건</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card">
            <table class="styled-table">
                <thead>
                    <tr>
                        <th style="text-align: center;">학교</th>
                        <th style="text-align: center;">EC 농도 (dS/m)</th>
                        <th style="text-align: center;">조건 특성</th>
                        <th style="text-align: center;">비고</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="text-align: center;"><span class="ec-badge ec-1">🔵 송도고</span></td>
                        <td style="text-align: center; font-size: 1.3rem; font-weight: 700;">1.0</td>
                        <td style="text-align: center;">저농도 · 고온(22~23°C)</td>
                        <td style="text-align: center;">일반 재배 환경</td>
                    </tr>
                    <tr style="background: rgba(0, 184, 148, 0.1);">
                        <td style="text-align: center;"><span class="ec-badge ec-2">🟢 하늘고</span></td>
                        <td style="text-align: center; font-size: 1.3rem; font-weight: 700; color: #00ff88;">2.0</td>
                        <td style="text-align: center;">적정농도 · 저온(14.7°C)</td>
                        <td style="text-align: center;"><strong style="color: #00ff88;">⭐ 최적 조건</strong></td>
                    </tr>
                    <tr>
                        <td style="text-align: center;"><span class="ec-badge ec-4">🔴 아라고</span></td>
                        <td style="text-align: center; font-size: 1.3rem; font-weight: 700;">4.0</td>
                        <td style="text-align: center;">고농도 · 고습도(66%)</td>
                        <td style="text-align: center;">염류 스트레스 구간</td>
                    </tr>
                    <tr>
                        <td style="text-align: center;"><span class="ec-badge ec-8">🟣 동산고</span></td>
                        <td style="text-align: center; font-size: 1.3rem; font-weight: 700;">8.0</td>
                        <td style="text-align: center;">초고농도</td>
                        <td style="text-align: center;">극한 스트레스 구간</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # 주요 지표 카드
        st.markdown('<div class="section-title">📈 핵심 지표</div>', unsafe_allow_html=True)
        
        total_count = sum(len(growth_data.get(s, pd.DataFrame())) for s in SCHOOL_NAMES)
        
        all_temps, all_humid = [], []
        for school, df in env_data.items():
            temp_col = get_column_safe(df, ["temp", "온도"])
            humid_col = get_column_safe(df, ["humid", "습도"])
            if temp_col:
                all_temps.extend(df[temp_col].dropna().tolist())
            if humid_col:
                all_humid.extend(df[humid_col].dropna().tolist())
        
        avg_temp = sum(all_temps) / len(all_temps) if all_temps else 0
        avg_humid = sum(all_humid) / len(all_humid) if all_humid else 0
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">🌿</div>
                <div class="metric-value">{total_count}</div>
                <div class="metric-label">총 실험 개체수</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">🌡️</div>
                <div class="metric-value">{avg_temp:.1f}°C</div>
                <div class="metric-label">평균 온도</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">💧</div>
                <div class="metric-value">{avg_humid:.1f}%</div>
                <div class="metric-label">평균 습도</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m4:
            st.markdown("""
            <div class="metric-card" style="border: 2px solid rgba(0, 255, 136, 0.5);">
                <div style="font-size: 2rem;">⭐</div>
                <div class="metric-value" style="color: #00ff88;">2.0</div>
                <div class="metric-label">최적 EC (dS/m)</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 핵심 결론 미리보기
        st.markdown('<div class="section-title">🎯 핵심 발견</div>', unsafe_allow_html=True)
        
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            st.markdown("""
            <div class="conclusion-card">
                <h3 style="color: #00ff88; margin-bottom: 15px;">✅ 최적 조건 발견</h3>
                <ul style="color: rgba(255,255,255,0.85); line-height: 2;">
                    <li><strong>EC 2.0 dS/m</strong>에서 최고 생중량 기록</li>
                    <li>지상부와 지하부의 <strong>균형 잡힌 성장</strong></li>
                    <li>염류 스트레스 없이 안정적인 양분 흡수</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col_f2:
            st.markdown("""
            <div class="danger-card">
                <h3 style="color: #ff6b6b; margin-bottom: 15px;">⚠️ 고농도 EC의 위험</h3>
                <ul style="color: rgba(255,255,255,0.85); line-height: 2;">
                    <li>EC 4.0 이상: <strong>삼투압으로 수분 흡수 장애</strong></li>
                    <li>지상부 성장 억제, <strong>뿌리만 과도 신장</strong></li>
                    <li>T/R율 불균형 → 비정상적 생존 반응</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # =========================================================================
    # TAB 2: 환경 데이터
    # =========================================================================
    with tab2:
        st.markdown('<div class="section-title">🌡️ 환경 데이터 분석</div>', unsafe_allow_html=True)
        
        if not env_data:
            st.error("❌ 환경 데이터를 찾을 수 없습니다.")
        else:
            # 학교별 환경 평균 비교
            env_summary = []
            for school in SCHOOL_NAMES_BY_EC:
                if school in env_data:
                    df = env_data[school]
                    temp_col = get_column_safe(df, ["temp", "온도"])
                    humid_col = get_column_safe(df, ["humid", "습도"])
                    ph_col = get_column_safe(df, ["ph"])
                    ec_col = get_column_safe(df, ["ec"])
                    
                    env_summary.append({
                        "학교": school,
                        "EC": SCHOOL_INFO[school]["ec_target"],
                        "평균 온도": df[temp_col].mean() if temp_col else 0,
                        "평균 습도": df[humid_col].mean() if humid_col else 0,
                        "평균 pH": df[ph_col].mean() if ph_col else 0,
                        "실측 EC": df[ec_col].mean() if ec_col else 0,
                        "목표 EC": SCHOOL_INFO[school]["ec_target"],
                        "색상": SCHOOL_INFO[school]["color"]
                    })
            
            env_summary_df = pd.DataFrame(env_summary)
            
            if not env_summary_df.empty:
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=("🌡️ 평균 온도 (°C)", "💧 평균 습도 (%)", "🧪 평균 pH", "⚡ 목표 vs 실측 EC"),
                    vertical_spacing=0.15,
                    horizontal_spacing=0.1
                )
                
                colors = [SCHOOL_INFO[s]["color"] for s in env_summary_df["학교"]]
                
                for i, (row, col, y_col) in enumerate([
                    (1, 1, "평균 온도"),
                    (1, 2, "평균 습도"),
                    (2, 1, "평균 pH")
                ]):
                    fig.add_trace(
                        go.Bar(x=env_summary_df["학교"], y=env_summary_df[y_col],
                               marker_color=colors, showlegend=False,
                               text=env_summary_df[y_col].round(1),
                               textposition="outside",
                               textfont=dict(color="white")),
                        row=row, col=col
                    )
                
                fig.add_trace(
                    go.Bar(x=env_summary_df["학교"], y=env_summary_df["목표 EC"],
                           name="목표 EC", marker_color="#667eea",
                           text=env_summary_df["목표 EC"], textposition="outside"),
                    row=2, col=2
                )
                fig.add_trace(
                    go.Bar(x=env_summary_df["학교"], y=env_summary_df["실측 EC"],
                           name="실측 EC", marker_color="#00b894",
                           text=env_summary_df["실측 EC"].round(1), textposition="outside"),
                    row=2, col=2
                )
                
                fig.update_layout(
                    height=650,
                    font=dict(family="Malgun Gothic, Noto Sans KR", color="white"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=True,
                    legend=dict(
                        orientation="h", yanchor="bottom", y=-0.12,
                        xanchor="center", x=0.5,
                        font=dict(color="white")
                    )
                )
                
                fig.update_xaxes(showgrid=False, color="rgba(255,255,255,0.7)")
                fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.7)")
                
                st.plotly_chart(fig, use_container_width=True)
            
            # 시계열 그래프
            st.markdown('<div class="section-title">📈 시계열 환경 변화</div>', unsafe_allow_html=True)
            
            display_school = filtered_schools[0] if len(filtered_schools) == 1 else st.selectbox(
                "학교 선택", SCHOOL_NAMES_BY_EC, key="ts_school"
            )
            
            if display_school in env_data:
                df = env_data[display_school].copy()
                time_col = get_column_safe(df, ["time", "시간", "날짜"])
                temp_col = get_column_safe(df, ["temp", "온도"])
                humid_col = get_column_safe(df, ["humid", "습도"])
                ec_col = get_column_safe(df, ["ec"])
                
                if time_col:
                    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
                    df = df.sort_values(time_col)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if temp_col and time_col:
                        fig_temp = px.line(df, x=time_col, y=temp_col)
                        fig_temp.update_traces(line=dict(color="#ff6b6b", width=2))
                        fig_temp.update_layout(
                            title="🌡️ 온도 변화",
                            font=dict(family="Malgun Gothic", color="white"),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(showgrid=False, color="rgba(255,255,255,0.7)"),
                            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.7)")
                        )
                        st.plotly_chart(fig_temp, use_container_width=True)
                
                with col2:
                    if humid_col and time_col:
                        fig_humid = px.line(df, x=time_col, y=humid_col)
                        fig_humid.update_traces(line=dict(color="#00d4ff", width=2))
                        fig_humid.update_layout(
                            title="💧 습도 변화",
                            font=dict(family="Malgun Gothic", color="white"),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(showgrid=False, color="rgba(255,255,255,0.7)"),
                            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.7)")
                        )
                        st.plotly_chart(fig_humid, use_container_width=True)
                
                if ec_col and time_col:
                    fig_ec = px.line(df, x=time_col, y=ec_col)
                    fig_ec.update_traces(line=dict(color="#00ff88", width=2))
                    fig_ec.add_hline(
                        y=SCHOOL_INFO[display_school]["ec_target"],
                        line_dash="dash", line_color="#bf00ff",
                        annotation_text=f"목표 EC: {SCHOOL_INFO[display_school]['ec_target']}",
                        annotation_font_color="white"
                    )
                    fig_ec.update_layout(
                        title="⚡ EC 변화",
                        font=dict(family="Malgun Gothic", color="white"),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(showgrid=False, color="rgba(255,255,255,0.7)"),
                        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.7)")
                    )
                    st.plotly_chart(fig_ec, use_container_width=True)
            
            with st.expander("📥 환경 데이터 다운로드"):
                for school in filtered_schools:
                    if school in env_data:
                        st.markdown(f"**{school}**")
                        st.dataframe(env_data[school], height=200)
                        csv = env_data[school].to_csv(index=False).encode("utf-8-sig")
                        st.download_button(f"📥 {school} CSV", csv, f"{school}_환경.csv", "text/csv", key=f"env_{school}")
    
    # =========================================================================
    # TAB 3: 생육 결과
    # =========================================================================
    with tab3:
        st.markdown('<div class="section-title">📊 생육 결과 분석</div>', unsafe_allow_html=True)
        
        if not growth_data:
            st.error("❌ 생육 결과 데이터를 찾을 수 없습니다.")
        else:
            # EC별 생중량 + 추세선
            st.markdown('<div class="section-title">🥇 EC 농도별 평균 생중량</div>', unsafe_allow_html=True)
            
            ec_weight_data = []
            for school in SCHOOL_NAMES_BY_EC:
                if school in growth_data:
                    df = growth_data[school]
                    weight_col = get_column_safe(df, ["생중량", "weight", "중량"])
                    if weight_col:
                        ec_weight_data.append({
                            "학교": school,
                            "EC": SCHOOL_INFO[school]["ec_target"],
                            "평균 생중량": df[weight_col].mean(),
                            "색상": SCHOOL_INFO[school]["color"]
                        })
            
            if ec_weight_data:
                ec_weight_df = pd.DataFrame(ec_weight_data).sort_values("EC")
                max_idx = ec_weight_df["평균 생중량"].idxmax()
                
                fig_main = go.Figure()
                
                colors = [SCHOOL_INFO[s]["color"] for s in ec_weight_df["학교"]]
                
                fig_main.add_trace(go.Bar(
                    x=ec_weight_df["EC"],
                    y=ec_weight_df["평균 생중량"],
                    text=[f"{s}<br>{w:.1f}g" for s, w in zip(ec_weight_df["학교"], ec_weight_df["평균 생중량"])],
                    textposition="outside",
                    textfont=dict(color="white", size=12),
                    marker=dict(
                        color=colors,
                        line=dict(color="rgba(255,255,255,0.3)", width=2)
                    ),
                    name="평균 생중량"
                ))
                
                # 추세선
                x_vals = ec_weight_df["EC"].values
                y_vals = ec_weight_df["평균 생중량"].values
                if len(x_vals) >= 3:
                    z = np.polyfit(x_vals, y_vals, 2)
                    p = np.poly1d(z)
                    x_trend = np.linspace(x_vals.min(), x_vals.max(), 50)
                    y_trend = p(x_trend)
                    
                    fig_main.add_trace(go.Scatter(
                        x=x_trend, y=y_trend,
                        mode="lines",
                        name="추세선",
                        line=dict(color="#ff6b6b", width=4, dash="dash")
                    ))
                
                fig_main.add_vline(x=2.0, line_dash="dot", line_color="#00ff88", line_width=3,
                                   annotation_text="⭐ 최적", annotation_font_color="#00ff88",
                                   annotation_font_size=14)
                
                fig_main.update_layout(
                    title=dict(text="EC 농도에 따른 평균 생중량 변화", font=dict(size=20, color="white")),
                    xaxis_title="EC 농도 (dS/m)",
                    yaxis_title="평균 생중량 (g)",
                    font=dict(family="Malgun Gothic, Noto Sans KR", color="white"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, color="rgba(255,255,255,0.7)", dtick=1),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.7)"),
                    height=500,
                    showlegend=True,
                    legend=dict(font=dict(color="white"))
                )
                
                st.plotly_chart(fig_main, use_container_width=True)
                
                st.markdown(f"""
                <div class="insight-box">
                    <strong style="color: #00ff88; font-size: 1.2rem;">📊 분석 결과</strong><br><br>
                    EC 농도가 증가함에 따라 생중량이 <strong>역U자형(산 모양)</strong> 패턴을 보입니다.<br>
                    <strong style="color: #00d4ff;">EC {ec_weight_df.loc[max_idx, 'EC']} dS/m ({ec_weight_df.loc[max_idx, '학교']})</strong>에서 
                    최대 생중량 <strong style="color: #00ff88;">{ec_weight_df.loc[max_idx, '평균 생중량']:.2f}g</strong>을 기록했습니다.
                </div>
                """, unsafe_allow_html=True)
            
            # 지상부/지하부 누적 막대
            st.markdown('<div class="section-title">🌿 지상부 vs 지하부 길이 (T/R율)</div>', unsafe_allow_html=True)
            
            length_data = []
            for school in SCHOOL_NAMES_BY_EC:
                if school in growth_data:
                    df = growth_data[school]
                    shoot_col = get_column_safe(df, ["지상부", "shoot"])
                    root_col = get_column_safe(df, ["지하부", "root"])
                    
                    shoot_avg = df[shoot_col].mean() if shoot_col else 0
                    root_avg = df[root_col].mean() if root_col else 0
                    
                    length_data.append({
                        "학교": school,
                        "EC": SCHOOL_INFO[school]["ec_target"],
                        "지상부": shoot_avg,
                        "지하부": root_avg,
                        "T/R율": shoot_avg / root_avg if root_avg > 0 else 0
                    })
            
            if length_data:
                length_df = pd.DataFrame(length_data).sort_values("EC")
                
                fig_stack = go.Figure()
                
                fig_stack.add_trace(go.Bar(
                    x=[f"EC {ec}" for ec in length_df["EC"]],
                    y=length_df["지상부"],
                    name="🌿 지상부 (잎)",
                    marker_color="#00ff88",
                    text=length_df["학교"],
                    textposition="inside",
                    textfont=dict(color="white")
                ))
                
                fig_stack.add_trace(go.Bar(
                    x=[f"EC {ec}" for ec in length_df["EC"]],
                    y=length_df["지하부"],
                    name="🟤 지하부 (뿌리)",
                    marker_color="#c4a484",
                    text=[f"{v:.0f}mm" for v in length_df["지하부"]],
                    textposition="inside",
                    textfont=dict(color="white")
                ))
                
                fig_stack.update_layout(
                    barmode="stack",
                    title=dict(text="EC 농도에 따른 지상부/지하부 누적 비교", font=dict(size=20, color="white")),
                    xaxis_title="EC 농도",
                    yaxis_title="길이 (mm)",
                    font=dict(family="Malgun Gothic", color="white"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, color="rgba(255,255,255,0.7)"),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.7)"),
                    height=500,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(color="white"))
                )
                
                st.plotly_chart(fig_stack, use_container_width=True)
                
                st.markdown("""
                <div class="warning-box">
                    <strong style="color: #ff6b6b; font-size: 1.2rem;">⚠️ T/R율 해석</strong><br><br>
                    고농도 EC 환경에서는 <strong>삼투압 현상</strong>으로 수분 흡수가 어려워집니다.<br>
                    식물은 생존을 위해 <strong>뿌리를 더 깊게 뻗어</strong> 물을 찾으려 하며,<br>
                    이로 인해 <strong style="color: #feca57;">지상부는 작아지고 지하부만 비대해지는</strong> 현상이 발생합니다.
                </div>
                """, unsafe_allow_html=True)
            
            # 박스플롯
            st.markdown('<div class="section-title">📦 학교별 생중량 분포</div>', unsafe_allow_html=True)
            
            all_growth = []
            for school in SCHOOL_NAMES_BY_EC:
                if school in growth_data:
                    df = growth_data[school].copy()
                    df["학교"] = school
                    df["EC"] = SCHOOL_INFO[school]["ec_target"]
                    all_growth.append(df)
            
            if all_growth:
                combined_df = pd.concat(all_growth, ignore_index=True)
                weight_col = get_column_safe(combined_df, ["생중량", "weight"])
                
                if weight_col:
                    combined_df = combined_df.sort_values("EC")
                    combined_df["label"] = combined_df.apply(lambda x: f"{x['학교']}\n(EC {x['EC']})", axis=1)
                    
                    fig_box = px.box(
                        combined_df, x="label", y=weight_col, color="학교",
                        color_discrete_map={s: SCHOOL_INFO[s]["color"] for s in SCHOOL_NAMES}
                    )
                    
                    fig_box.update_layout(
                        title=dict(text="학교별 생중량 분포 (이상치 확인)", font=dict(size=20, color="white")),
                        font=dict(family="Malgun Gothic", color="white"),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(showgrid=False, color="rgba(255,255,255,0.7)", title=""),
                        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.7)", title="생중량 (g)"),
                        showlegend=False,
                        height=450
                    )
                    
                    st.plotly_chart(fig_box, use_container_width=True)
            
            # 최종 결론
            st.markdown('<div class="section-title">🎯 최종 결론</div>', unsafe_allow_html=True)
            
            col_c1, col_c2 = st.columns(2)
            
            with col_c1:
                st.markdown("""
                <div class="conclusion-card">
                    <h2 style="color: #00ff88; margin-bottom: 20px;">✅ 최적 생육 조건</h2>
                    <div style="font-size: 3rem; text-align: center; margin: 20px 0;">
                        <span style="background: linear-gradient(135deg, #00ff88, #00d4ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">
                            EC 1.0 ~ 2.0 dS/m
                        </span>
                    </div>
                    <ul style="color: rgba(255,255,255,0.9); line-height: 2.2; font-size: 1.1rem;">
                        <li><strong>EC 2.0 (하늘고)</strong>에서 최고 생중량</li>
                        <li>지상부/지하부 <strong>균형 성장</strong></li>
                        <li>염류 스트레스 <strong>없음</strong></li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col_c2:
                st.markdown("""
                <div class="danger-card">
                    <h2 style="color: #ff6b6b; margin-bottom: 20px;">⚠️ 피해야 할 조건</h2>
                    <div style="font-size: 3rem; text-align: center; margin: 20px 0;">
                        <span style="color: #ff6b6b; font-weight: 900;">
                            EC 4.0+ dS/m
                        </span>
                    </div>
                    <ul style="color: rgba(255,255,255,0.9); line-height: 2.2; font-size: 1.1rem;">
                        <li>삼투압으로 <strong>수분 흡수 장애</strong></li>
                        <li>지상부 억제, <strong>뿌리 과신장</strong></li>
                        <li>비정상적 <strong>T/R율 불균형</strong></li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="glass-card" style="text-align: center; margin-top: 30px; border: 2px solid rgba(0, 212, 255, 0.3);">
                <h3 style="color: #00d4ff; margin-bottom: 15px;">💡 실용적 제안</h3>
                <p style="color: rgba(255,255,255,0.9); font-size: 1.15rem; line-height: 1.8;">
                    나도수영 재배 시 EC를 <strong style="color: #00ff88;">1.0~2.0 dS/m</strong> 범위로 유지하고,<br>
                    pH 조절이 필요할 경우 비료 양을 늘리지 말고<br>
                    <strong style="color: #bf00ff;">별도의 산도 조절제</strong>를 사용하여 EC 상승 없이 pH만 조절하세요.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📥 생육 데이터 다운로드"):
                for school in filtered_schools:
                    if school in growth_data:
                        st.markdown(f"**{school}** ({len(growth_data[school])}개체)")
                        st.dataframe(growth_data[school], height=200)
                
                if growth_data:
                    xlsx_buffer = io.BytesIO()
                    with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
                        for school in SCHOOL_NAMES_BY_EC:
                            if school in growth_data:
                                growth_data[school].to_excel(writer, sheet_name=school, index=False)
                    xlsx_buffer.seek(0)
                    
                    st.download_button("📥 전체 XLSX 다운로드", xlsx_buffer, "생육결과.xlsx",
                                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ==============================================================================
# 실행
# ==============================================================================
if __name__ == "__main__":
    main()
