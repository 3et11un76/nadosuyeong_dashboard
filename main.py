# ==============================================================================
# 🌱 극지식물(나도수영) 최적 EC 농도 연구 대시보드
# 4개 학교(송도고, 동산고, 하늘고, 아라고) 공동 실험 데이터 분석
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
# 0. 페이지 설정 및 한글 폰트
# ==============================================================================
st.set_page_config(
    page_title="🌱 극지식물 최적 EC 농도 연구",
    page_icon="🌱",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}
.highlight-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    margin: 10px 0;
}
.insight-box {
    background-color: #f0f9ff;
    border-left: 5px solid #0ea5e9;
    padding: 15px;
    margin: 10px 0;
    border-radius: 0 10px 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. 학교 정보 설정 (EC 오름차순 정렬)
# ==============================================================================
SCHOOL_INFO = {
    "송도고": {"ec_target": 1.0, "color": "#636EFA", "order": 1},
    "하늘고": {"ec_target": 2.0, "color": "#00CC96", "order": 2},  # 최적
    "아라고": {"ec_target": 4.0, "color": "#EF553B", "order": 3},
    "동산고": {"ec_target": 8.0, "color": "#AB63FA", "order": 4},
}

# EC 오름차순으로 정렬된 학교 리스트
SCHOOL_NAMES_BY_EC = sorted(SCHOOL_INFO.keys(), key=lambda x: SCHOOL_INFO[x]["ec_target"])
SCHOOL_NAMES = list(SCHOOL_INFO.keys())

# ==============================================================================
# 2. 한글 파일명 안전 인식 함수
# ==============================================================================
def normalize_match(target: str, candidate: str) -> bool:
    """NFC/NFD 양방향 비교로 한글 파일명 매칭"""
    target_nfc = unicodedata.normalize("NFC", target)
    target_nfd = unicodedata.normalize("NFD", target)
    candidate_nfc = unicodedata.normalize("NFC", candidate)
    candidate_nfd = unicodedata.normalize("NFD", candidate)
    return target_nfc == candidate_nfc or target_nfd == candidate_nfd


def find_file(directory: Path, keyword: str, extension: str) -> Path | None:
    """디렉토리에서 키워드를 포함하는 파일 찾기"""
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
    """학교별 환경 데이터 로딩"""
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
                            st.warning(f"{school} 환경 데이터 로딩 실패: {e}")
    
    return env_data


@st.cache_data
def load_growth_data() -> dict[str, pd.DataFrame]:
    """학교별 생육 결과 데이터 로딩"""
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
                            st.warning(f"{school} 생육 데이터 로딩 실패: {e}")
    
    return growth_data


def get_column_safe(df: pd.DataFrame, keywords: list[str]) -> str | None:
    """컬럼명을 유연하게 찾기"""
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
    st.title("🌱 극지식물(나도수영) 최적 EC 농도 연구")
    st.markdown("**4개 학교(송도고, 동산고, 하늘고, 아라고) 공동 실험 결과 분석** | 검수: 극지연구소")
    
    # -------------------------------------------------------------------------
    # 사이드바: 학교 선택
    # -------------------------------------------------------------------------
    st.sidebar.header("🔍 필터 옵션")
    school_options = ["전체"] + SCHOOL_NAMES_BY_EC
    selected_school = st.sidebar.selectbox("학교 선택", school_options)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📌 학교별 EC 조건")
    for school in SCHOOL_NAMES_BY_EC:
        info = SCHOOL_INFO[school]
        marker = "⭐ 최적" if school == "하늘고" else ""
        st.sidebar.markdown(f"- **{school}**: EC {info['ec_target']} dS/m {marker}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔬 연구 핵심 질문")
    st.sidebar.info("극지식물이 가장 잘 자라는 **최적 EC 농도**는 얼마인가?")
    
    # -------------------------------------------------------------------------
    # 데이터 로딩
    # -------------------------------------------------------------------------
    with st.spinner("📂 데이터를 불러오는 중..."):
        env_data = load_environment_data()
        growth_data = load_growth_data()
    
    if not env_data and not growth_data:
        st.error("❌ 데이터를 찾을 수 없습니다. `data/` 폴더에 CSV 파일이 있는지 확인해주세요.")
        st.info("📁 예상 파일 구조:\n- data/송도고_환경데이터.csv\n- data/송도고_생육결과데이터.csv\n- ...")
        return
    
    # 선택된 학교 필터링
    if selected_school == "전체":
        filtered_schools = SCHOOL_NAMES_BY_EC
    else:
        filtered_schools = [selected_school]
    
    # -------------------------------------------------------------------------
    # 탭 구성
    # -------------------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["📖 실험 개요", "🌡️ 환경 데이터", "📊 생육 결과"])
    
    # =========================================================================
    # TAB 1: 실험 개요
    # =========================================================================
    with tab1:
        st.header("📖 연구 배경 및 목적")
        
        col_intro1, col_intro2 = st.columns([2, 1])
        
        with col_intro1:
            st.markdown("""
            ### 🎯 연구 목적
            4개 학교에서 진행한 식물 생육 실험 데이터를 분석하여, **극지식물(나도수영)이 가장 잘 자랄 수 있는 
            최적 EC(전기전도도) 농도**를 찾기 위해 본 연구를 수행하였습니다.
            
            ### 🔬 연구 배경
            - **극지식물**: 극지방 및 고산지대와 같은 극한 환경에서 자생하는 식물
            - **EC(Electrical Conductivity)**: 식물에게 공급되는 양분의 농도를 나타내는 지표
            - **핵심 딜레마**: EC가 너무 낮으면 양분 부족, 너무 높으면 **염류 스트레스(삼투압 문제)** 발생
            
            ### 💡 핵심 발견
            > EC 농도가 너무 높으면 뿌리가 물을 흡수하는 데 어려움을 겪게 되고, 
            > 이것이 **탈수 증상**으로 이어져 식물 성장에 부정적인 영향을 미칩니다.
            > 특히 고농도 EC 환경에서는 **지상부 성장이 억제**되고 **지하부(뿌리)만 과도하게 길어지는** 현상이 관찰되었습니다.
            """)
        
        with col_intro2:
            st.markdown("""
            ### 📋 연구 정보
            | 항목 | 내용 |
            |------|------|
            | 교육기관 | 업스테이지 |
            | 검수기관 | 극지연구소 |
            | 검수자 | 이유경 박사 |
            | 참여학교 | 4개교 |
            """)
        
        st.markdown("---")
        
        # 학교별 EC 조건 표
        st.subheader("🏫 학교별 실험 조건 (EC 오름차순)")
        
        school_table_data = []
        for school in SCHOOL_NAMES_BY_EC:
            info = SCHOOL_INFO[school]
            count = len(growth_data.get(school, pd.DataFrame()))
            optimal = "⭐ 최적 조건" if school == "하늘고" else ""
            school_table_data.append({
                "학교명": school,
                "목표 EC (dS/m)": info["ec_target"],
                "개체수": count,
                "색상": "🟦" if school == "송도고" else ("🟩" if school == "하늘고" else ("🟥" if school == "아라고" else "🟪")),
                "비고": optimal
            })
        
        school_df = pd.DataFrame(school_table_data)
        st.dataframe(school_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 주요 지표 카드
        st.subheader("📈 주요 지표 요약")
        
        total_count = sum(len(growth_data.get(s, pd.DataFrame())) for s in SCHOOL_NAMES)
        
        # 평균 온도/습도 계산
        all_temps = []
        all_humid = []
        for school, df in env_data.items():
            temp_col = get_column_safe(df, ["temp", "온도"])
            humid_col = get_column_safe(df, ["humid", "습도"])
            if temp_col:
                all_temps.extend(df[temp_col].dropna().tolist())
            if humid_col:
                all_humid.extend(df[humid_col].dropna().tolist())
        
        avg_temp = sum(all_temps) / len(all_temps) if all_temps else 0
        avg_humid = sum(all_humid) / len(all_humid) if all_humid else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌿 총 개체수", f"{total_count}개")
        col2.metric("🌡️ 평균 온도", f"{avg_temp:.1f}°C")
        col3.metric("💧 평균 습도", f"{avg_humid:.1f}%")
        col4.metric("⭐ 최적 EC", "2.0 dS/m", delta="하늘고")
        
        # 연구 결론 미리보기
        st.markdown("---")
        st.subheader("🎯 핵심 결론 미리보기")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.success("""
            **✅ 최적 EC 농도: 1.0 ~ 2.0 dS/m**
            - EC 2.0 (하늘고)에서 가장 높은 생중량 기록
            - 지상부와 지하부의 균형 잡힌 성장
            """)
        with col_c2:
            st.warning("""
            **⚠️ 고농도 EC의 문제점 (4.0 이상)**
            - 염류 스트레스로 인한 수분 흡수 장애
            - 지상부 성장 억제, 뿌리만 과도하게 신장
            """)
    
    # =========================================================================
    # TAB 2: 환경 데이터
    # =========================================================================
    with tab2:
        st.header("🌡️ 환경 데이터 분석")
        
        if not env_data:
            st.error("❌ 환경 데이터를 찾을 수 없습니다.")
        else:
            # -----------------------------------------------------------------
            # 학교별 환경 평균 비교 (2x2 서브플롯)
            # -----------------------------------------------------------------
            st.subheader("📊 학교별 환경 요소 평균 비교")
            
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
                    subplot_titles=("평균 온도 (°C)", "평균 습도 (%)", "평균 pH", "목표 EC vs 실측 EC")
                )
                
                colors = [SCHOOL_INFO[s]["color"] for s in env_summary_df["학교"]]
                
                # 평균 온도
                fig.add_trace(
                    go.Bar(x=env_summary_df["학교"], y=env_summary_df["평균 온도"],
                           marker_color=colors, name="온도", showlegend=False),
                    row=1, col=1
                )
                
                # 평균 습도
                fig.add_trace(
                    go.Bar(x=env_summary_df["학교"], y=env_summary_df["평균 습도"],
                           marker_color=colors, name="습도", showlegend=False),
                    row=1, col=2
                )
                
                # 평균 pH
                fig.add_trace(
                    go.Bar(x=env_summary_df["학교"], y=env_summary_df["평균 pH"],
                           marker_color=colors, name="pH", showlegend=False),
                    row=2, col=1
                )
                
                # 목표 EC vs 실측 EC
                fig.add_trace(
                    go.Bar(x=env_summary_df["학교"], y=env_summary_df["목표 EC"],
                           name="목표 EC", marker_color="#1f77b4"),
                    row=2, col=2
                )
                fig.add_trace(
                    go.Bar(x=env_summary_df["학교"], y=env_summary_df["실측 EC"],
                           name="실측 EC", marker_color="#ff7f0e"),
                    row=2, col=2
                )
                
                fig.update_layout(
                    height=600,
                    font=dict(family="Malgun Gothic, Apple SD Gothic Neo, Noto Sans KR, sans-serif"),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # -----------------------------------------------------------------
            # 선택 학교 시계열 그래프
            # -----------------------------------------------------------------
            st.subheader("📈 시계열 환경 변화")
            
            display_school = filtered_schools[0] if len(filtered_schools) == 1 else st.selectbox(
                "학교 선택 (시계열)", SCHOOL_NAMES_BY_EC, key="timeseries_school"
            )
            
            if display_school in env_data:
                df = env_data[display_school]
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
                        fig_temp = px.line(df, x=time_col, y=temp_col, title="🌡️ 온도 변화")
                        fig_temp.update_layout(
                            font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif"),
                            xaxis_title="시간", yaxis_title="온도 (°C)"
                        )
                        st.plotly_chart(fig_temp, use_container_width=True)
                
                with col2:
                    if humid_col and time_col:
                        fig_humid = px.line(df, x=time_col, y=humid_col, title="💧 습도 변화")
                        fig_humid.update_layout(
                            font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif"),
                            xaxis_title="시간", yaxis_title="습도 (%)"
                        )
                        st.plotly_chart(fig_humid, use_container_width=True)
                
                if ec_col and time_col:
                    fig_ec = px.line(df, x=time_col, y=ec_col, title="⚡ EC 변화")
                    fig_ec.add_hline(
                        y=SCHOOL_INFO[display_school]["ec_target"],
                        line_dash="dash", line_color="red",
                        annotation_text=f"목표 EC: {SCHOOL_INFO[display_school]['ec_target']}"
                    )
                    fig_ec.update_layout(
                        font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif"),
                        xaxis_title="시간", yaxis_title="EC (dS/m)"
                    )
                    st.plotly_chart(fig_ec, use_container_width=True)
            
            # -----------------------------------------------------------------
            # 원본 데이터 다운로드
            # -----------------------------------------------------------------
            with st.expander("📥 환경 데이터 원본 보기 및 다운로드"):
                for school in filtered_schools:
                    if school in env_data:
                        st.markdown(f"**{school}**")
                        st.dataframe(env_data[school], use_container_width=True, height=200)
                        
                        csv_buffer = env_data[school].to_csv(index=False).encode("utf-8-sig")
                        st.download_button(
                            label=f"📥 {school} 환경데이터 CSV 다운로드",
                            data=csv_buffer,
                            file_name=f"{school}_환경데이터.csv",
                            mime="text/csv",
                            key=f"env_download_{school}"
                        )
    
    # =========================================================================
    # TAB 3: 생육 결과
    # =========================================================================
    with tab3:
        st.header("📊 생육 결과 분석")
        
        if not growth_data:
            st.error("❌ 생육 결과 데이터를 찾을 수 없습니다.")
        else:
            # -----------------------------------------------------------------
            # 🆕 핵심 그래프 1: EC 농도별 생중량 막대그래프 + 추세선
            # -----------------------------------------------------------------
            st.subheader("🥇 핵심 분석: EC 농도별 평균 생중량 (추세선 포함)")
            
            ec_weight_data = []
            for school in SCHOOL_NAMES_BY_EC:
                if school in growth_data:
                    df = growth_data[school]
                    weight_col = get_column_safe(df, ["생중량", "weight", "중량"])
                    if weight_col:
                        avg_weight = df[weight_col].mean()
                        median_weight = df[weight_col].median()
                        ec_weight_data.append({
                            "학교": school,
                            "EC": SCHOOL_INFO[school]["ec_target"],
                            "평균 생중량": avg_weight,
                            "중앙값 생중량": median_weight,
                            "색상": SCHOOL_INFO[school]["color"]
                        })
            
            if ec_weight_data:
                ec_weight_df = pd.DataFrame(ec_weight_data)
                ec_weight_df = ec_weight_df.sort_values("EC")  # EC 오름차순 정렬
                
                max_weight_idx = ec_weight_df["평균 생중량"].idxmax()
                max_weight_school = ec_weight_df.loc[max_weight_idx, "학교"]
                
                # 막대그래프 + 추세선
                fig_ec_weight = go.Figure()
                
                # 막대그래프
                colors = [SCHOOL_INFO[s]["color"] for s in ec_weight_df["학교"]]
                fig_ec_weight.add_trace(go.Bar(
                    x=ec_weight_df["EC"],
                    y=ec_weight_df["평균 생중량"],
                    text=ec_weight_df["학교"],
                    textposition="outside",
                    marker_color=colors,
                    name="평균 생중량",
                    hovertemplate="EC: %{x} dS/m<br>생중량: %{y:.2f}g<br>학교: %{text}<extra></extra>"
                ))
                
                # 추세선 (2차 다항식)
                x_vals = ec_weight_df["EC"].values
                y_vals = ec_weight_df["평균 생중량"].values
                
                if len(x_vals) >= 3:
                    # 2차 다항 회귀
                    z = np.polyfit(x_vals, y_vals, 2)
                    p = np.poly1d(z)
                    x_trend = np.linspace(x_vals.min(), x_vals.max(), 50)
                    y_trend = p(x_trend)
                    
                    fig_ec_weight.add_trace(go.Scatter(
                        x=x_trend,
                        y=y_trend,
                        mode="lines",
                        name="추세선 (2차 다항식)",
                        line=dict(color="red", width=3, dash="dash")
                    ))
                
                # 최적값 표시
                fig_ec_weight.add_vline(
                    x=2.0, line_dash="dot", line_color="green",
                    annotation_text="⭐ 최적 EC", annotation_position="top"
                )
                
                fig_ec_weight.update_layout(
                    title="EC 농도에 따른 평균 생중량 변화",
                    xaxis_title="EC 농도 (dS/m)",
                    yaxis_title="평균 생중량 (g)",
                    font=dict(family="Malgun Gothic, Apple SD Gothic Neo, Noto Sans KR, sans-serif"),
                    showlegend=True,
                    height=500
                )
                
                st.plotly_chart(fig_ec_weight, use_container_width=True)
                
                # 인사이트 박스
                st.info(f"""
                📊 **분석 결과**: EC 농도가 증가함에 따라 생중량이 **역U자형(산 모양)** 패턴을 보입니다.
                - **최적 조건**: EC {ec_weight_df.loc[max_weight_idx, 'EC']} dS/m ({max_weight_school})에서 최대 생중량 **{ec_weight_df.loc[max_weight_idx, '평균 생중량']:.2f}g** 기록
                - **고농도 위험**: EC 4.0 이상에서는 염류 스트레스로 인해 생장이 급격히 감소
                """)
            
            st.markdown("---")
            
            # -----------------------------------------------------------------
            # 🆕 핵심 그래프 2: EC 농도별 지상부/지하부 누적 막대 그래프
            # -----------------------------------------------------------------
            st.subheader("🌿 EC 농도별 지상부 vs 지하부 길이 비교 (T/R율 분석)")
            
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
                        "지상부 길이": shoot_avg,
                        "지하부 길이": root_avg,
                        "T/R율": shoot_avg / root_avg if root_avg > 0 else 0
                    })
            
            if length_data:
                length_df = pd.DataFrame(length_data)
                length_df = length_df.sort_values("EC")  # EC 오름차순 정렬
                
                # 누적 막대그래프
                fig_stacked = go.Figure()
                
                fig_stacked.add_trace(go.Bar(
                    x=length_df["EC"],
                    y=length_df["지상부 길이"],
                    name="🌿 지상부 (잎)",
                    marker_color="#77DD77",
                    text=length_df["학교"],
                    hovertemplate="EC: %{x} dS/m<br>지상부: %{y:.1f}mm<br>학교: %{text}<extra></extra>"
                ))
                
                fig_stacked.add_trace(go.Bar(
                    x=length_df["EC"],
                    y=length_df["지하부 길이"],
                    name="🟤 지하부 (뿌리)",
                    marker_color="#C4A484",
                    text=length_df["학교"],
                    hovertemplate="EC: %{x} dS/m<br>지하부: %{y:.1f}mm<br>학교: %{text}<extra></extra>"
                ))
                
                fig_stacked.update_layout(
                    barmode="stack",
                    title="EC 농도에 따른 지상부/지하부 길이 누적 비교",
                    xaxis_title="EC 농도 (dS/m)",
                    yaxis_title="길이 (mm)",
                    font=dict(family="Malgun Gothic, Apple SD Gothic Neo, Noto Sans KR, sans-serif"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    height=500
                )
                
                st.plotly_chart(fig_stacked, use_container_width=True)
                
                # T/R율 분석 표
                col_tr1, col_tr2 = st.columns([1, 1])
                
                with col_tr1:
                    st.markdown("**📐 T/R율 (지상부/지하부 비율) 분석**")
                    tr_display = length_df[["학교", "EC", "지상부 길이", "지하부 길이", "T/R율"]].copy()
                    tr_display["지상부 길이"] = tr_display["지상부 길이"].round(1).astype(str) + " mm"
                    tr_display["지하부 길이"] = tr_display["지하부 길이"].round(1).astype(str) + " mm"
                    tr_display["T/R율"] = tr_display["T/R율"].round(2)
                    st.dataframe(tr_display, use_container_width=True, hide_index=True)
                
                with col_tr2:
                    st.warning("""
                    **🔍 T/R율 해석**
                    - **T/R율 > 1**: 지상부가 지하부보다 큼 (정상적 성장)
                    - **T/R율 < 1**: 지하부가 과도하게 발달 (스트레스 반응)
                    
                    **⚠️ 고농도 EC 환경의 문제점**
                    > 염류 스트레스로 인해 물 흡수가 어려워지면, 
                    > 식물은 생존을 위해 **뿌리를 더 깊게 뻗어** 물을 찾으려 합니다.
                    > 이것이 T/R율이 낮아지는 원인입니다.
                    """)
            
            st.markdown("---")
            
            # -----------------------------------------------------------------
            # EC별 생육 비교 (2x2 서브플롯)
            # -----------------------------------------------------------------
            st.subheader("📊 EC별 생육 지표 종합 비교")
            
            growth_summary = []
            for school in SCHOOL_NAMES_BY_EC:
                if school in growth_data:
                    df = growth_data[school]
                    weight_col = get_column_safe(df, ["생중량", "weight"])
                    leaf_col = get_column_safe(df, ["잎", "leaf", "장"])
                    shoot_col = get_column_safe(df, ["지상부", "shoot"])
                    root_col = get_column_safe(df, ["지하부", "root"])
                    
                    growth_summary.append({
                        "학교": school,
                        "EC": SCHOOL_INFO[school]["ec_target"],
                        "평균 생중량(g)": df[weight_col].mean() if weight_col else 0,
                        "평균 잎 수(장)": df[leaf_col].mean() if leaf_col else 0,
                        "평균 지상부(mm)": df[shoot_col].mean() if shoot_col else 0,
                        "개체수": len(df),
                        "색상": SCHOOL_INFO[school]["color"]
                    })
            
            growth_summary_df = pd.DataFrame(growth_summary)
            growth_summary_df = growth_summary_df.sort_values("EC")
            
            if not growth_summary_df.empty:
                fig2 = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=("⭐ 평균 생중량 (g)", "평균 잎 수 (장)", "평균 지상부 길이 (mm)", "개체수 비교")
                )
                
                colors = [SCHOOL_INFO[s]["color"] for s in growth_summary_df["학교"]]
                x_labels = [f"EC {ec}" for ec in growth_summary_df["EC"]]
                
                # 평균 생중량
                fig2.add_trace(
                    go.Bar(x=x_labels, y=growth_summary_df["평균 생중량(g)"],
                           marker_color=colors, name="생중량", showlegend=False,
                           text=growth_summary_df["학교"], textposition="outside"),
                    row=1, col=1
                )
                
                # 평균 잎 수
                fig2.add_trace(
                    go.Bar(x=x_labels, y=growth_summary_df["평균 잎 수(장)"],
                           marker_color=colors, name="잎 수", showlegend=False,
                           text=growth_summary_df["학교"], textposition="outside"),
                    row=1, col=2
                )
                
                # 평균 지상부 길이
                fig2.add_trace(
                    go.Bar(x=x_labels, y=growth_summary_df["평균 지상부(mm)"],
                           marker_color=colors, name="지상부", showlegend=False,
                           text=growth_summary_df["학교"], textposition="outside"),
                    row=2, col=1
                )
                
                # 개체수
                fig2.add_trace(
                    go.Bar(x=x_labels, y=growth_summary_df["개체수"],
                           marker_color=colors, name="개체수", showlegend=False,
                           text=growth_summary_df["학교"], textposition="outside"),
                    row=2, col=2
                )
                
                fig2.update_layout(
                    height=600,
                    font=dict(family="Malgun Gothic, Apple SD Gothic Neo, Noto Sans KR, sans-serif")
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown("---")
            
            # -----------------------------------------------------------------
            # 학교별 생중량 분포 (박스플롯)
            # -----------------------------------------------------------------
            st.subheader("📦 학교별 생중량 분포 (이상치 확인)")
            
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
                    # EC 순서로 정렬
                    combined_df["EC_order"] = combined_df["EC"]
                    combined_df = combined_df.sort_values("EC_order")
                    combined_df["학교_EC"] = combined_df.apply(lambda x: f"{x['학교']} (EC {x['EC']})", axis=1)
                    
                    fig_box = px.box(
                        combined_df, x="학교_EC", y=weight_col, color="학교",
                        color_discrete_map={s: SCHOOL_INFO[s]["color"] for s in SCHOOL_NAMES},
                        title="학교별 생중량 분포 (Box Plot) - EC 오름차순"
                    )
                    fig_box.update_layout(
                        font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif"),
                        showlegend=False,
                        xaxis_title="학교 (EC 농도)",
                        yaxis_title="생중량 (g)"
                    )
                    st.plotly_chart(fig_box, use_container_width=True)
            
            st.markdown("---")
            
            # -----------------------------------------------------------------
            # 상관관계 분석 (산점도)
            # -----------------------------------------------------------------
            st.subheader("🔗 상관관계 분석")
            
            if all_growth:
                combined_df = pd.concat(all_growth, ignore_index=True)
                weight_col = get_column_safe(combined_df, ["생중량", "weight"])
                leaf_col = get_column_safe(combined_df, ["잎", "leaf"])
                shoot_col = get_column_safe(combined_df, ["지상부", "shoot"])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if leaf_col and weight_col:
                        fig_scatter1 = px.scatter(
                            combined_df, x=leaf_col, y=weight_col, color="학교",
                            color_discrete_map={s: SCHOOL_INFO[s]["color"] for s in SCHOOL_NAMES},
                            title="🌿 잎 수 vs 생중량",
                            trendline="ols"
                        )
                        fig_scatter1.update_layout(
                            font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif")
                        )
                        st.plotly_chart(fig_scatter1, use_container_width=True)
                
                with col2:
                    if shoot_col and weight_col:
                        fig_scatter2 = px.scatter(
                            combined_df, x=shoot_col, y=weight_col, color="학교",
                            color_discrete_map={s: SCHOOL_INFO[s]["color"] for s in SCHOOL_NAMES},
                            title="📏 지상부 길이 vs 생중량",
                            trendline="ols"
                        )
                        fig_scatter2.update_layout(
                            font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif")
                        )
                        st.plotly_chart(fig_scatter2, use_container_width=True)
            
            # -----------------------------------------------------------------
            # 최종 결론
            # -----------------------------------------------------------------
            st.markdown("---")
            st.subheader("🎯 최종 결론 및 제언")
            
            col_final1, col_final2 = st.columns(2)
            
            with col_final1:
                st.success("""
                ### ✅ 최적 생육 조건
                
                **EC 농도: 1.0 ~ 2.0 dS/m**
                - 특히 **EC 2.0 (하늘고)**에서 최고 생중량 기록
                - 지상부와 지하부의 균형 잡힌 성장
                - 염류 스트레스 없이 안정적인 양분 흡수
                """)
            
            with col_final2:
                st.error("""
                ### ⚠️ 고농도 EC의 문제점
                
                **EC 4.0 이상에서 발생하는 현상:**
                - 삼투압 현상으로 수분 흡수 장애
                - 지상부 성장 억제 (잎이 작아짐)
                - 지하부(뿌리) 과도 신장 (물 찾기 위한 생존 반응)
                - T/R율 불균형 → 비정상적 성장
                """)
            
            st.info("""
            **💡 실용적 제안**: 나도수영 재배 시 EC를 **1.0~2.0 dS/m** 범위로 유지하고, 
            pH 조절이 필요할 경우 비료 양을 늘리지 말고 **별도의 산도 조절제**를 사용하여 
            EC 상승 없이 pH만 조절하는 정밀 농업 기술을 적용해야 합니다.
            """)
            
            # -----------------------------------------------------------------
            # 원본 데이터 다운로드
            # -----------------------------------------------------------------
            with st.expander("📥 생육 데이터 원본 보기 및 다운로드"):
                for school in filtered_schools:
                    if school in growth_data:
                        st.markdown(f"**{school}** ({len(growth_data[school])}개체)")
                        st.dataframe(growth_data[school], use_container_width=True, height=200)
                
                # XLSX 다운로드 (전체)
                if growth_data:
                    xlsx_buffer = io.BytesIO()
                    with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
                        for school in SCHOOL_NAMES_BY_EC:
                            if school in growth_data:
                                growth_data[school].to_excel(writer, sheet_name=school, index=False)
                    xlsx_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 전체 생육 데이터 XLSX 다운로드",
                        data=xlsx_buffer,
                        file_name="전체_생육결과데이터.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

# ==============================================================================
# 실행
# ==============================================================================
if __name__ == "__main__":
    main()
