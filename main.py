import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------
# 기본 설정
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 1 - 시간")

st.markdown(
    """
    최근 **1년(365일)** 동안의 일별 박스오피스 10위권 기록을 활용합니다.
    """
)

DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_daily.csv"


# -----------------------------------------------------------------------
# 데이터 불러오기 & 전처리
# -----------------------------------------------------------------------
@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # 날짜(하이픈 없는 여덟 자리 숫자) 열을 진짜 날짜 타입으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")

    return df


with st.spinner("데이터를 불러오는 중입니다..."):
    df = load_data(DATA_URL)

with st.expander("원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.divider()


# -----------------------------------------------------------------------
# 그래프 1. 영화 선택 -> 날짜별 일관객 변화 (선 그래프)
# -----------------------------------------------------------------------
st.header("1. 영화별 날짜에 따른 일관객 변화")

movie_list = sorted(df["영화명"].unique())
selected_movie = st.selectbox("영화를 선택하세요", movie_list)

df_movie = df[df["영화명"] == selected_movie].sort_values("날짜")

fig_line = px.line(
    df_movie,
    x="날짜",
    y="일관객",
    markers=True,
)
fig_line.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>",
)
fig_line.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객 수",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_line, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="영화별 일관객 변화 해석",
    value="",
    placeholder="예: 개봉 직후 일관객이 가장 높고, 시간이 지날수록 점차 줄어드는 경향을 보인다.",
    label_visibility="collapsed",
    key="insight_movie_daily_audi_line",
)

st.divider()


# -----------------------------------------------------------------------
# 그래프 2. 일관객 합계 상위 5편의 날짜별 일관객 변화 (다중 선 그래프)
# -----------------------------------------------------------------------
st.header("2. 일관객 합계 상위 5편의 날짜별 변화")

top5_movies = (
    df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).head(5).index
)
df_top5 = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig_top5_line = px.line(
    df_top5,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
)
fig_top5_line.update_traces(
    hovertemplate="영화명: %{fullData.name}<br>날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>",
)
fig_top5_line.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객 수",
    legend_title_text="영화명 (클릭해서 켜고 끄기)",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_top5_line, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="상위 5편 일관객 변화 해석",
    value="",
    placeholder="예: 상위 5편 모두 개봉 초반에 관객이 몰리며, 영화마다 흥행이 오래 유지되는 기간에 차이가 있다.",
    label_visibility="collapsed",
    key="insight_top5_daily_audi_line",
)

st.divider()


# -----------------------------------------------------------------------
# 그래프 3. 날짜별 10위권 일관객 합계 (영역 그래프 + 최고 3일 표시)
# -----------------------------------------------------------------------
st.header("3. 날짜별 10위권 일관객 합계")

daily_total = df.groupby("날짜")["일관객"].sum().reset_index()
daily_total.columns = ["날짜", "합계"]

fig_area = px.area(
    daily_total,
    x="날짜",
    y="합계",
)
fig_area.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계: %{y:,}명<extra></extra>",
)
fig_area.update_layout(
    xaxis_title="날짜",
    yaxis_title="10위권 일관객 합계",
    margin=dict(t=30, b=30, l=10, r=10),
)

# 합계가 가장 컸던 날 3일을 찾아 그래프 위에 표시
top3_days = daily_total.nlargest(3, "합계")

fig_area.add_scatter(
    x=top3_days["날짜"],
    y=top3_days["합계"],
    mode="markers+text",
    text=top3_days["날짜"].dt.strftime("%Y-%m-%d"),
    textposition="top center",
    marker=dict(size=10, color="red"),
    name="합계 상위 3일",
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계: %{y:,}명<extra></extra>",
)

st.plotly_chart(fig_area, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="날짜별 10위권 합계 해석",
    value="",
    placeholder="예: 특정 날짜(연휴, 신작 개봉일 등)에 전체 관객 합계가 크게 튀어 오른다.",
    label_visibility="collapsed",
    key="insight_daily_total_area",
)

st.divider()


# -----------------------------------------------------------------------
# 그래프 4. 일관객 합계 TOP 10 (가로 막대그래프)
# -----------------------------------------------------------------------
st.header("4. 일관객 합계 TOP 10 영화")

movie_summary = (
    df.groupby("영화명")
    .agg(합계=("일관객", "sum"), 순위권_일수=("영화명", "size"))
    .reset_index()
)
top10_movies = movie_summary.sort_values("합계", ascending=False).head(10)

fig_top10_bar = px.bar(
    top10_movies,
    x="합계",
    y="영화명",
    orientation="h",
    hover_data={"순위권_일수": True, "합계": False, "영화명": False},
)
fig_top10_bar.update_traces(
    hovertemplate="영화명: %{y}<br>총 일관객 합계: %{x:,}명<br>10위권에 든 날수: %{customdata[0]}일<extra></extra>",
)
fig_top10_bar.update_layout(
    xaxis_title="총 일관객 합계",
    yaxis_title="영화명",
    yaxis=dict(autorange="reversed"),  # 관객이 많은 영화가 위로 오게
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_top10_bar, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="일관객 합계 TOP 10 해석",
    value="",
    placeholder="예: 1위 영화는 2위 영화보다 총 관객이 훨씬 많고, 10위권에 머문 날수도 더 길다.",
    label_visibility="collapsed",
    key="insight_top10_total_audi_bar",
)

st.divider()


# -----------------------------------------------------------------------
# 그래프 5. 월 x 요일별 일관객 합계 히트맵
# -----------------------------------------------------------------------
st.header("5. 월 x 요일별 일관객 합계 히트맵")

WEEKDAY_ORDER = ["월", "화", "수", "목", "금", "토", "일"]
WEEKDAY_MAP = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}

df_heat = df.copy()
df_heat["월"] = df_heat["날짜"].dt.month
df_heat["요일"] = df_heat["날짜"].dt.weekday.map(WEEKDAY_MAP)

heat_pivot = (
    df_heat.groupby(["요일", "월"])["일관객"]
    .sum()
    .reset_index()
    .pivot(index="요일", columns="월", values="일관객")
    .reindex(WEEKDAY_ORDER)
)

fig_heatmap = px.imshow(
    heat_pivot,
    color_continuous_scale="Reds",
    aspect="auto",
    labels=dict(x="월", y="요일", color="일관객 합계"),
)
fig_heatmap.update_traces(
    hovertemplate="%{y}요일 %{x}월<br>일관객 합계: %{z:,}명<extra></extra>",
)
fig_heatmap.update_layout(
    xaxis_title="월",
    yaxis_title="요일",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="월x요일 히트맵 해석",
    value="",
    placeholder="예: 요일별로는 주말(금~일)에, 월별로는 ○월에 관객이 특히 많이 몰린다.",
    label_visibility="collapsed",
    key="insight_month_weekday_heatmap",
)

st.divider()

st.caption(
    "※ 이후 시간에 관련된 그래프를 "
    "이 아래에 같은 형식(그래프 + '이 그래프로 알 수 있는 것')으로 계속 추가할 수 있습니다."
)
