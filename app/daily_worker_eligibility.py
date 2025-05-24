import streamlit as st
import pandas as pd
import datetime
import calendar

# Streamlit 설정
st.set_page_config(page_title="일용근로자 수급자격 모의계산", layout="wide")
st.title("✅ 근무일 선택 달력")

# 날짜 입력 받기
apply_date = st.date_input("수급자격 신청일을 선택하세요", datetime.date.today())

# 날짜 범위 계산 (신청일이 포함된 달과 그 전 달)
start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
end_date_for_calendar = apply_date

# 달력 표시 대상 월 리스트 생성
months_to_display = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar).date))

# 날짜 선택 상태 저장
selected_dates = st.session_state.get("selected_dates", set())

# 달력 UI 생성 함수
def render_calendar(year, month):
    cal = calendar.Calendar(firstweekday=0)  # 월요일 시작
    month_days = cal.monthdatescalendar(year, month)
    st.markdown(f"### {year}년 {month}월")

    # 달력 형태로 표 만들기
    day_labels = ["월", "화", "수", "목", "금", "토", "일"]
    cols = st.columns(7)
    for col, label in zip(cols, day_labels):
        col.markdown(f"**{label}**")

    for week in month_days:
        cols = st.columns(7)
        for idx, day in enumerate(week):
            if day.month != month:
                cols[idx].markdown(" ")
            else:
                disabled = day > apply_date
                key = f"{day}"
                checked = key in selected_dates
                if cols[idx].checkbox(f"{day.day}", value=checked, key=key, disabled=disabled):
                    selected_dates.add(key)
                else:
                    selected_dates.discard(key)

# 달력 렌더링
for year, month in months_to_display:
    render_calendar(year, month)

# 선택된 날짜 결과 출력
if selected_dates:
    st.markdown("### ✅ 선택된 근무일")
    for date_str in sorted(selected_dates):
        st.write(date_str)

# 상태 저장
st.session_state["selected_dates"] = selected_dates

