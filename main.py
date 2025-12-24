# ==============================================================================
# 🌱 극지식물 최적 EC 농도 연구 대시보드
# 4개 학교(송도고, 동산고, 하늘고, 아라고) 공동 실험 데이터 분석
# ==============================================================================

import streamlit as st
import pandas as pd
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
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. 학교 정보 설정
# ==============================================================================
SCHOOL_INFO = {
    "송도고": {"ec_target": 1.0, "color": "#636EFA"},
    "하늘고": {"ec_target": 2.0, "color": "#00CC96"},  # 최적
    "아라고": {"ec_target": 4.0, "color": "#EF553B"},
    "동산고": {"ec_target": 8.0, "color": "#AB63FA"},
}

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
    
    for school in SCHOOL_NAMES:
        file_path = find_file(data_dir, school, ".csv")
        if file_path and "환경" in unicodedata.normalize("NFC", file_path.stem):
            try:
                df = pd.read_csv(file_path, encoding="utf-8-sig")
                # 컬럼명 정규화
                df.columns = [unicodedata.normalize("NFC", col.strip().lower()) for col in df.columns]
                env_data[school] = df
            except Exception as e:
                st.warning(f"{school} 환경 데이터 로딩 실패: {e}")
    
    # 파일을 못 찾은 경우 다시 시도 (환경데이터 키워드 포함)
    if len(env_data) < len(SCHOOL_NAMES):
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
    st.title("🌱 극지식물 최적 EC 농도 연구")
    st.markdown("**4개 학교(송도고, 동산고, 하늘고, 아라고) 공동 실험 결과 분석**")
    
    # -------------------------------------------------------------------------
    # 사이드바: 학교 선택
    # -------------------------------------------------------------------------
    st.sidebar.header("🔍 필터 옵션")
    school_options = ["전체"] + SCHOOL_NAMES
    selected_school = st.sidebar.selectbox("학교 선택", school_options)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📌 학교별 EC 조건")
    for school, info in SCHOOL_INFO.items():
        marker = "⭐" if school == "하늘고" else ""
        st.sidebar.markdown(f"- **{school}**: EC {info['ec_target']} {marker}")
    
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
        filtered_schools = SCHOOL_NAMES
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
        
        st.markdown("""
        ### 🎯 연구 목적
        극지식물(나도수영)의 생육에 가장 적합한 **최적 EC(전기전도도) 농도**를 규명하기 위해, 
        4개 학교에서 서로 다른 EC 조건으로 재배 실험을 진행하고 그 결과를 비교 분석합니다.
        
        ### 🔬 연구 배경
        - **EC(Electrical Conductivity)**: 식물에게 공급되는 양분의 농도를 나타내는 지표
        - EC가 너무 낮으면 양분 부족, 너무 높으면 염류 스트레스(삼투압 문제) 발생
        - 극지식물은 척박한 환경에 적응해 비료 요구도가 낮은 특성을 가짐
        """)
        
        st.markdown("---")
        
        # 학교별 EC 조건 표
        st.subheader("🏫 학교별 실험 조건")
        
        school_table_data = []
        for school in SCHOOL_NAMES:
            info = SCHOOL_INFO[school]
            count = len(growth_data.get(school, pd.DataFrame()))
            optimal = "⭐ 최적" if school == "하늘고" else ""
            school_table_data.append({
                "학교명": school,
                "목표 EC (dS/m)": info["ec_target"],
                "개체수": count,
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
            for school in SCHOOL_NAMES:
                if school in env_data:
                    df = env_data[school]
                    temp_col = get_column_safe(df, ["temp", "온도"])
                    humid_col = get_column_safe(df, ["humid", "습도"])
                    ph_col = get_column_safe(df, ["ph"])
                    ec_col = get_column_safe(df, ["ec"])
                    
                    env_summary.append({
                        "학교": school,
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
                "학교 선택 (시계열)", SCHOOL_NAMES, key="timeseries_school"
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
            # 핵심 결과 카드: EC별 평균 생중량
            # -----------------------------------------------------------------
            st.subheader("🥇 핵심 결과: EC별 평균 생중량")
            
            ec_weight_data = []
            for school in SCHOOL_NAMES:
                if school in growth_data:
                    df = growth_data[school]
                    weight_col = get_column_safe(df, ["생중량", "weight", "중량"])
                    if weight_col:
                        avg_weight = df[weight_col].mean()
                        ec_weight_data.append({
                            "학교": school,
                            "EC": SCHOOL_INFO[school]["ec_target"],
                            "평균 생중량": avg_weight
                        })
            
            if ec_weight_data:
                ec_weight_df = pd.DataFrame(ec_weight_data)
                max_weight_school = ec_weight_df.loc[ec_weight_df["평균 생중량"].idxmax(), "학교"]
                
                cols = st.columns(len(ec_weight_data))
                for i, row in ec_weight_df.iterrows():
                    is_best = row["학교"] == max_weight_school
                    with cols[i]:
                        if is_best:
                            st.success(f"⭐ **{row['학교']}** (EC {row['EC']})")
                            st.metric("평균 생중량", f"{row['평균 생중량']:.2f}g", delta="최적!")
                        else:
                            st.info(f"**{row['학교']}** (EC {row['EC']})")
                            st.metric("평균 생중량", f"{row['평균 생중량']:.2f}g")
            
            st.markdown("---")
            
            # -----------------------------------------------------------------
            # EC별 생육 비교 (2x2 서브플롯)
            # -----------------------------------------------------------------
            st.subheader("📊 EC별 생육 지표 비교")
            
            growth_summary = []
            for school in SCHOOL_NAMES:
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
            
            if not growth_summary_df.empty:
                fig2 = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=("⭐ 평균 생중량 (g)", "평균 잎 수 (장)", "평균 지상부 길이 (mm)", "개체수 비교")
                )
                
                colors = [SCHOOL_INFO[s]["color"] for s in growth_summary_df["학교"]]
                
                # 평균 생중량
                fig2.add_trace(
                    go.Bar(x=growth_summary_df["학교"], y=growth_summary_df["평균 생중량(g)"],
                           marker_color=colors, name="생중량", showlegend=False),
                    row=1, col=1
                )
                
                # 평균 잎 수
                fig2.add_trace(
                    go.Bar(x=growth_summary_df["학교"], y=growth_summary_df["평균 잎 수(장)"],
                           marker_color=colors, name="잎 수", showlegend=False),
                    row=1, col=2
                )
                
                # 평균 지상부 길이
                fig2.add_trace(
                    go.Bar(x=growth_summary_df["학교"], y=growth_summary_df["평균 지상부(mm)"],
                           marker_color=colors, name="지상부", showlegend=False),
                    row=2, col=1
                )
                
                # 개체수
                fig2.add_trace(
                    go.Bar(x=growth_summary_df["학교"], y=growth_summary_df["개체수"],
                           marker_color=colors, name="개체수", showlegend=False),
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
            st.subheader("📦 학교별 생중량 분포")
            
            all_growth = []
            for school in SCHOOL_NAMES:
                if school in growth_data:
                    df = growth_data[school].copy()
                    df["학교"] = school
                    df["EC"] = SCHOOL_INFO[school]["ec_target"]
                    all_growth.append(df)
            
            if all_growth:
                combined_df = pd.concat(all_growth, ignore_index=True)
                weight_col = get_column_safe(combined_df, ["생중량", "weight"])
                
                if weight_col:
                    fig_box = px.box(
                        combined_df, x="학교", y=weight_col, color="학교",
                        color_discrete_map={s: SCHOOL_INFO[s]["color"] for s in SCHOOL_NAMES},
                        title="학교별 생중량 분포 (Box Plot)"
                    )
                    fig_box.update_layout(
                        font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif"),
                        showlegend=False
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
                        for school, df in growth_data.items():
                            df.to_excel(writer, sheet_name=school, index=False)
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
