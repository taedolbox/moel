import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import pytz
import time

calendar.setfirstweekday(calendar.SUNDAY)
KST = pytz.timezone("Asia/Seoul")

timestamp = time.time()
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_date_range(apply_date):
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar(apply_date):
    if "selected_dates" not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = datetime.now(KST).date()
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=apply_date)))

    for year, month in months:
        st.markdown(f"### {year}년 {month}월", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        day_headers = ["일", "월", "화", "수", "목", "금", "토"]
        cols = st.columns(7, gap="small")
        for i, day_name in enumerate(day_headers):
            with cols[i]:
                class_name = "day-header"
                if i == 0:
                    class_name += " sunday"
                elif i == 6:
                    class_name += " saturday"
                st.markdown(f'<div class="{class_name}">{day_name}</div>', unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7, gap="small")
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.markdown('<div class="day empty"></div>', unsafe_allow_html=True)
                        continue
                    date_obj = date(year, month, day)
                    is_selected = date_obj in selected_dates
                    is_disabled = date_obj > apply_date
                    is_current = date_obj == current_date

                    class_name = "day"
                    if i == 0:
                        class_name += " sunday"
                    elif i == 6:
                        class_name += " saturday"
                    if is_selected:
                        class_name += " selected"
                    if is_disabled:
                        class_name += " disabled"
                    if is_current:
                        class_name += " current"

                    button_label = f"{day}"
                    if st.button(button_label, key=str(date_obj)):
                        if date_obj in selected_dates:
                            selected_dates.remove(date_obj)
                        else:
                            selected_dates.add(date_obj)
                        st.session_state.selected_dates = selected_dates
                        st.rerun()

                    st.markdown(
                        f'<div class="{class_name}">{day}</div>',
                        unsafe_allow_html=True
                    )

    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%m/%d") for d in sorted(selected_dates)]))

    return st.session_state.selected_dates

def daily_worker_eligibility_app():
    st.set_page_config(page_title="일용근로자 수급자격 요건 모의계산", layout="centered")
    st.header("일용근로자 수급자격 요건 모의계산")

    current_datetime = datetime.now(KST)
    current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %I:%M KST')
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 신청일 직전달 1일부터 신청일까지 근무일 수가 총일수의 1/3 미만이어야 함")
    st.markdown("- **조건 2 (건설일용만)**: 신청일 직전 14일간 근무 기록이 없어야 함")
    st.markdown("---")

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date())
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("#### 근무일 선택 달력")
    selected_dates = render_calendar(apply_date)
    st.markdown("---")

    total_days = len(date_range_objects)
    worked_days = len(selected_dates)
    threshold = total_days / 3
    condition1 = worked_days < threshold

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")
    st.markdown(
        f'<div class="result-text"><p>{"✅ 조건 1 충족" if condition1 else "❌ 조건 1 불충족"}</p></div>',
        unsafe_allow_html=True
    )

    fourteen_end = apply_date - timedelta(days=1)
    fourteen_start = fourteen_end - timedelta(days=13)
    fourteen_days = [d.date() for d in pd.date_range(start=fourteen_start, end=fourteen_end)]
    condition2 = all(day not in selected_dates for day in fourteen_days)

    st.markdown(
        f'<div class="result-text"><p>{"✅ 조건 2 충족" if condition2 else "❌ 조건 2 불충족"}</p></div>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    if not condition1:
        for i in range(1, 31):
            future_date = apply_date + timedelta(days=i)
            future_range, _ = get_date_range(future_date)
            future_threshold = len(future_range) / 3
            worked_until_future = sum(1 for d in selected_dates if d <= future_date)
            if worked_until_future < future_threshold:
                st.markdown(f"📅 조건 1 충족 예상 신청일: **{future_date.strftime('%Y-%m-%d')}**")
                break
        else:
            st.markdown("❗ 30일 이내 조건 1 충족일이 없습니다.")

    if not condition2:
        last_work = max((d for d in selected_dates if d < apply_date), default=None)
        if last_work:
            suggested = last_work + timedelta(days=15)
            st.markdown(f"📅 조건 2 충족 예상 신청일: **{suggested.strftime('%Y-%m-%d')}**")

    st.subheader("📌 최종 판단")
    if condition1:
        st.markdown("✅ 일반일용근로자: 신청 가능")
    else:
        st.markdown("❌ 일반일용근로자: 신청 불가")

    if condition1 and condition2:
        st.markdown("✅ 건설일용근로자: 신청 가능")
    else:
        st.markdown("❌ 건설일용근로자: 신청 불가")

if __name__ == "__main__":
    daily_worker_eligibility_app()
