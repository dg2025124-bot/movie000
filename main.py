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
# 구역 4. 일관객 합계 TOP 10 영화
# ----------------------------------------------------------------------------
st.header("구역 4. 일관객 합계 TOP 10 영화")

movie_summary = (
    df.groupby("영화명")
    .agg(일관객합계=("일관객", "sum"), 순위진입일수=("영화명", "count"))
    .reset_index()
)

top10_summary = movie_summary.sort_values("일관객합계", ascending=False).head(10)
# 가로 막대그래프에서 위쪽에 큰 값이 오도록 오름차순으로 정렬해 전달
top10_summary = top10_summary.sort_values("일관객합계", ascending=True)

fig4 = px.bar(
    top10_summary,
    x="일관객합계",
    y="영화명",
    orientation="h",
    title="일관객 합계 TOP 10 영화",
    labels={"일관객합계": "일관객 합계", "영화명": "영화", "순위진입일수": "10위권 진입 일수"},
    custom_data=["순위진입일수"],
)
fig4.update_traces(
    hovertemplate="영화: %{y}<br>일관객 합계: %{x:,}명<br>10위권 진입 일수: %{customdata[0]}일<extra></extra>"
)
fig4.update_layout(yaxis=dict(categoryorder="total ascending"))

st.plotly_chart(fig4, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽어낼 수 있는 내용을 한 문장으로 적어주세요.)")

st.divider()

# ----------------------------------------------------------------------------
# 구역 5. 월 × 요일별 일관객 합계 히트맵
# ----------------------------------------------------------------------------
st.header("구역 5. 월 × 요일별 일관객 평균 히트맵")

heatmap_df = df.copy()
heatmap_df["월"] = heatmap_df["날짜"].dt.month
heatmap_df["요일"] = heatmap_df["날짜"].dt.dayofweek  # 0=월요일 ... 6=일요일

weekday_names = ["월", "화", "수", "목", "금", "토", "일"]

pivot = (
    heatmap_df.groupby(["월", "요일"])["일관객"]
    .mean()
    .reset_index()
    .pivot(index="요일", columns="월", values="일관객")
    .reindex(index=range(7))  # 월요일(0)~일요일(6) 순서 고정
)
pivot.index = weekday_names
pivot.columns = [f"{m}월" for m in pivot.columns]

fig5 = px.imshow(
    pivot,
    color_continuous_scale="Reds",
    aspect="auto",
    labels=dict(x="월", y="요일", color="일관객 평균"),
    title="월 × 요일별 일관객 평균 히트맵",
)
fig5.update_traces(
    hovertemplate="%{x} · %{y}요일<br>일관객 평균: %{z:,.0f}명<extra></extra>"
)
fig5.update_xaxes(side="top")

st.plotly_chart(fig5, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽어낼 수 있는 내용을 한 문장으로 적어주세요.)")

st.divider()

# ----------------------------------------------------------------------------
# 구역 6. '오디세이' 흥행 시점
# ----------------------------------------------------------------------------
st.header("구역 6. '오디세이' 흥행 시점")

odyssey_df = df[df["영화명"].str.contains("오디세이", na=False)].sort_values("날짜")

if odyssey_df.empty:
    st.warning("데이터에서 영화명에 '오디세이'가 포함된 영화를 찾을 수 없습니다.")
else:
    odyssey_title = odyssey_df["영화명"].mode().iloc[0]  # 가장 흔한 표기 사용
    peak_row = odyssey_df.loc[odyssey_df["일관객"].idxmax()]

    # 가장 많이 본 날을 다른 색으로 강조하기 위한 구분 열
    odyssey_df = odyssey_df.copy()
    odyssey_df["구분"] = "그 외 날짜"
    odyssey_df.loc[odyssey_df["날짜"] == peak_row["날짜"], "구분"] = "가장 많이 본 날"

    fig6 = px.bar(
        odyssey_df,
        x="날짜",
        y="일관객",
        color="구분",
        color_discrete_map={"그 외 날짜": "#8ab4f8", "가장 많이 본 날": "#e63946"},
        title=f"'{odyssey_title}' 날짜별 관객수",
        labels={"날짜": "날짜", "일관객": "일일 관객수"},
    )
    fig6.update_traces(
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>일일 관객수: %{y:,}명<extra></extra>"
    )
    fig6.add_annotation(
        x=peak_row["날짜"],
        y=peak_row["일관객"],
        text=f"최고: {peak_row['날짜'].strftime('%Y-%m-%d')} ({peak_row['일관객']:,.0f}명)",
        showarrow=True,
        arrowhead=2,
        yshift=15,
    )
    fig6.update_layout(legend_title_text="")

    st.plotly_chart(fig6, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("가장 많이 본 날", peak_row["날짜"].strftime("%Y-%m-%d"))
    col2.metric("그날 관객수", f"{peak_row['일관객']:,.0f}명")
    col3.metric("기간 내 총 관객수", f"{odyssey_df['일관객'].sum():,.0f}명")

st.info("**이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽어낼 수 있는 내용을 한 문장으로 적어주세요.)")

st.divider()

# ----------------------------------------------------------------------------
# 구역 7. (다음 그래프를 추가할 자리)
# ----------------------------------------------------------------------------
st.header("구역 7. 추가 예정")
st.caption("다음 그래프가 이 구역에 추가될 예정입니다.")
