import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. 페이지 기본 설정
st.set_page_config(layout="wide", page_title="극지식물 연구 보고서")
st.title("🌱 극지식물(나도수영) 최적 EC 농도 연구 분석")
st.markdown("4개 학교(송도고, 동산고, 하늘고, 아라고) 공동 실험 데이터 대시보드")

# 2. 가상 데이터 생성 (실제 사용 시에는 pd.read_csv('파일명.csv')로 변경하세요)
data = {
    'School': ['Songdo']*20 + ['Dongsan']*20 + ['Haneul']*20 + ['Arago']*20,
    'EC_Type': ['Low']*20 + ['Low']*20 + ['High']*20 + ['High']*20,
    'EC_Value': [0.9, 1.0, 1.2, 0.95]*5 + [1.0, 1.1, 0.9, 1.0]*5 + [4.0, 4.2, 4.1, 4.0]*5 + [4.5, 4.8, 4.9, 4.6]*5,
    'Weight(g)': [10, 12, 27, 11]*5 + [12, 13, 11, 12]*5 + [15, 18, 14, 16]*5 + [5, 6, 4, 5]*5, # 아라고는 무게 낮음
    'Shoot_Length': [80, 90, 85, 82]*5 + [85, 88, 86, 84]*5 + [120, 125, 118, 122]*5 + [50, 55, 45, 52]*5, # 아라고 지상부 짧음
    'Root_Length': [100, 110, 105, 102]*5 + [100, 102, 98, 101]*5 + [200, 210, 195, 205]*5 + [300, 310, 290, 305]*5 # 아라고 지하부 매우 긺
}
df = pd.DataFrame(data)

# 3. 사이드바 (옵션 선택)
st.sidebar.header("검색 옵션")
selected_school = st.sidebar.multiselect("학교 선택", df['School'].unique(), default=df['School'].unique())
filtered_df = df[df['School'].isin(selected_school)]

# 4. 메인 탭 구성
tab1, tab2, tab3 = st.tabs(["📊 데이터 요약", "📈 그래프 분석", "📝 결론 및 제언"])

with tab1:
    st.subheader("실험 데이터 미리보기")
    col1, col2, col3 = st.columns(3)
    col1.metric("총 데이터 개수", f"{len(filtered_df)}개")
    col2.metric("평균 생중량", f"{filtered_df['Weight(g)'].mean():.2f}g")
    col3.metric("평균 EC 농도", f"{filtered_df['EC_Value'].mean():.2f}dS/m")
    
    st.dataframe(filtered_df, use_container_width=True)

with tab2:
    st.subheader("학교별 생육 특성 비교")
    
    col_chart1, col_chart2 = st.columns(2)
    
    # 그래프 1: 상자 수염 그림 (이상치 및 분포 확인)
    with col_chart1:
        st.markdown("**1. 학교별 생중량 분포 (Box Plot)**")
        st.caption("송도고의 이상치와 학교별 데이터 편차를 확인하세요.")
        fig1, ax1 = plt.subplots()
        sns.boxplot(data=filtered_df, x='School', y='Weight(g)', ax=ax1, palette="Set2")
        st.pyplot(fig1)

    # 그래프 2: 산점도 (EC와 생장의 관계)
    with col_chart2:
        st.markdown("**2. EC 농도에 따른 무게 변화 (Scatter Plot)**")
        st.caption("EC가 1.0~1.5 구간일 때 무게가 높은 '산 모양' 분포를 확인하세요.")
        fig2, ax2 = plt.subplots()
        sns.scatterplot(data=filtered_df, x='EC_Value', y='Weight(g)', hue='School', s=100, ax=ax2)
        st.pyplot(fig2)

    st.divider()
    
    # 그래프 3: 누적 막대 (T/R율 시각화) - 간단하게 평균으로 표현
    st.markdown("**3. 지상부 vs 지하부 길이 비율 (Root Overgrowth)**")
    st.caption("아라고(Arago)와 하늘고(Haneul)에서 뿌리(주황색)가 비정상적으로 긴 것을 볼 수 있습니다.")
    
    avg_data = df.groupby('School')[['Shoot_Length', 'Root_Length']].mean().reset_index()
    # Streamlit 내장 차트 사용 (간편함)
    st.bar_chart(avg_data.set_index('School'), color=["#77DD77", "#FFB347"]) # 초록(잎), 주황(뿌리)

with tab3:
    st.subheader("💡 최종 결론")
    st.success("최적 EC 농도는 1.0 ~ 1.5 dS/m 구간으로 확인됨")
    st.markdown("""
    - **딜레마 발견:** EC를 높이면 pH는 맞지만 **염류 스트레스**로 뿌리만 비대해짐 (아라고 사례).
    - **해결 방안:** 비료 양(EC)을 늘리지 않고 **별도의 산도 조절제**를 사용하여 pH만 6.0으로 낮추는 정밀 제어가 필요함.
    - **제언:** 향후 온도와 EC를 교차한 추가 실험이 요구됨.
    """)
