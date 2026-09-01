import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 데이터(최근 1년, 10위권)를 시간 축으로 살펴보는 그래프 모음입니다.")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


# ----------------------------------------------------------------------------
# 데이터 로드 & 전처리
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # 날짜 열(하이픈 없는 8자리 숫자, 예: 20240101) -> 실제 날짜 타입으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")

    # 숫자 열들 타입 정리 (혹시 문자열로 섞여 들어오는 경우 대비)
    numeric_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("날짜").reset_index(drop=True)
    return df


with st.spinner("데이터를 불러오는 중입니다..."):
    df = load_data(DATA_URL)

st.success(f"데이터 로드 완료! 총 {len(df):,}행, 기간: {df['날짜'].min().date()} ~ {df['날짜'].max().date()}")

st.divider()

# ----------------------------------------------------------------------------
# 구역 1. 영화별 일관객 추이
# ----------------------------------------------------------------------------
st.header("구역 1. 영화별 일관객 추이")

movie_list = sorted(df["영화명"].dropna().unique())
selected_movie = st.selectbox("영화를 선택하세요", movie_list, key="movie_select_1")

movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"'{selected_movie}' 일별 관객수 변화",
    labels={"날짜": "날짜", "일관객": "일일 관객수"},
)
fig1.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일일 관객수: %{y:,}명<extra></extra>"
)
fig1.update_layout(hovermode="x unified")

st.plotly_chart(fig1, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽어낼 수 있는 내용을 한 문장으로 적어주세요.)")

st.divider()

# ----------------------------------------------------------------------------
# 구역 2. 일관객 합계 상위 5편 비교
# ----------------------------------------------------------------------------
st.header("구역 2. 일관객 합계 상위 5편 비교")

top5_movies = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 상위 5편의 날짜별 관객수 변화",
    labels={"날짜": "날짜", "일관객": "일일 관객수", "영화명": "영화"},
)
fig2.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일일 관객수: %{y:,}명<extra>%{fullData.name}</extra>"
)
fig2.update_layout(hovermode="x unified", legend_title_text="영화 (클릭하여 켜기/끄기)")

st.plotly_chart(fig2, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽어낼 수 있는 내용을 한 문장으로 적어주세요.)")

st.divider()

# ----------------------------------------------------------------------------
# 구역 3. 날짜별 10위권 일관객 합계 추이
# ----------------------------------------------------------------------------
st.header("구역 3. 날짜별 10위권 일관객 합계 추이")

daily_total = (
    df.groupby("날짜")["일관객"]
    .sum()
    .reset_index()
    .sort_values("날짜")
)

top3_days = daily_total.sort_values("일관객", ascending=False).head(3)

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 박스오피스 10위권 일관객 합계",
    labels={"날짜": "날짜", "일관객": "일일 관객수 합계"},
)
fig3.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계 관객수: %{y:,}명<extra></extra>"
)

# 상위 3일을 점으로 강조 표시
fig3.add_scatter(
    x=top3_days["날짜"],
    y=top3_days["일관객"],
    mode="markers",
    marker=dict(size=10, color="red"),
    name="상위 3일",
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계 관객수: %{y:,}명<extra>상위 3일</extra>",
)

# 상위 3일 날짜 라벨 표시
for _, row in top3_days.iterrows():
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=row["날짜"].strftime("%Y-%m-%d"),
        showarrow=True,
        arrowhead=2,
        yshift=15,
    )

fig3.update_layout(hovermode="x unified")

st.plotly_chart(fig3, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽어낼 수 있는 내용을 한 문장으로 적어주세요.)")

st.divider()

# ----------------------------------------------------------------------------
# 구역 4. (다음 그래프를 추가할 자리)
# ----------------------------------------------------------------------------
st.header("구역 4. 추가 예정")
st.caption("다음 그래프가 이 구역에 추가될 예정입니다.")
