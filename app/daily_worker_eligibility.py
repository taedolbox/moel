import streamlit as st
import calendar
import datetime

# 스타일 커스터마이징
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("일용근로자 수급자격 요건 모의계산")

today = datetime.date.today()

# 수급자격 신청일 입력
application_date = st.date_input("수급자격 신청일", value=today)

# 선택된 날짜 저장용 세션 상태 초기화
if "selected_days" not in st.session_state:
    st.session_state.selected_days = []

# 캘린더 범위 설정 (수급자격 신청일 기준 18개월 이전 ~ 신청일)
start_date = application_date.replace(day=1) - datetime.timedelta(days=365 + 180)
end_date = application_date

def toggle_date(date):
    if date in st.session_state.selected_days:
        st.session_state.selected_days.remove(date)
    else:
        st.session_state.selected_days.append(date)

# 달력 렌더링
def render_calendar(year, month):
    cal = calendar.Calendar()
    month_days = cal.itermonthdates(year, month)

    st.markdown(f"### {year}년 {month}월")
    cols = st.columns(7)
    for i, day in enumerate(["월", "화", "수", "목", "금", "토", "일"]):
        cols[i].markdown(f"**{day}**")

    week_cols = st.columns(7)
    for idx, day in enumerate(month_days):
        if day.month != month:
            week_cols[idx % 7].markdown(" ")
            continue

        if day in st.session_state.selected_days:
            style = "selected"
        else:
            style = "default"

        if week_cols[idx % 7].button(f"{day.day}", key=f"{year}-{month}-{day.day}"):
            toggle_date(day)

        week_cols[idx % 7].markdown(
            f"<div class='{style}'>{day.day}</div>", unsafe_allow_html=True
        )
        if idx % 7 == 6:
            week_cols = st.columns(7)

# 달력 범위 렌더링
current = start_date
while current <= end_date:
    render_calendar(current.year, current.month)
    if current.month == 12:
        current = current.replace(year=current.year + 1, month=1)
    else:
        current = current.replace(month=current.month + 1)

# 선택된 날짜 출력
selected_days = sorted(st.session_state.selected_days)
st.markdown("### 선택된 근무일수")
st.write(f"{len(selected_days)}일")
