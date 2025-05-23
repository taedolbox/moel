import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

def get_date_range(apply_date):
    start_date = apply_date.replace(month=4, day=1)
    return pd.date_range(start=start_date, end=apply_date)

def render_calendar(apply_date):
    start_date = apply_date.replace(month=4, day=1)
    end_date = apply_date
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=end_date)))

    selected_dates = set()

    for year, month in months:
        st.markdown(f"### {year}년 {month}월")
        cal = calendar.monthcalendar(year, month)
        days = ["일", "월", "화", "수", "목", "금", "토"]

        cols = st.columns(7)
        for i, day in enumerate(days):
            color = "red" if i == 0 else "blue" if i == 6 else "black"
            cols[i].markdown(f"<span style='color:{color}'><strong>{day}</strong></span>", unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown(" ")
                else:
                    date = datetime(year, month, day).date()
                    if date > apply_date:
                        cols[i].markdown(f"<span style='color:gray'>{day}</span>", unsafe_allow_html=True)
                        continue
                    checkbox_key = f"cb_{date}"
                    checked = st.session_state.get(checkbox_key, False)
                    if cols[i].checkbox(str(day), key=checkbox_key):
                        selected_dates.add(date)
                    elif checked:
                        selected_dates.add(date)

    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([date.strftime("%Y-%m-%d") for date in sorted(selected_dates)]))

    return selected_dates

def daily_worker_eligibility_app():
    st.header("수급자격 - 일용근로자 수급자격 요건 모의계산")

    worker_type = st.radio("근로자 유형을 선택하세요", ["일반일용근로자", "건설일용근로자"])

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.today())
    date_range = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_days = render_calendar(apply_date)
    st.markdown("---")

    total_days = len(date_range)
    worked_days = len(selected_days)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    if condition1:
        st.success("✅ 조건 1 충족: 근무일 수가 기준 미만입니다.")
    else:
        st.warning("❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.")

    condition2 = False
    if worker_type == "건설일용근로자":
        fourteen_days_prior = [apply_date - timedelta(days=i) for i in range(1, 15)]
        no_work_14_days = all(day not in selected_days for day in fourteen_days_prior)
        condition2 = no_work_14_days

        if no_work_14_days:
            st.success("✅ 조건 2 충족: 신청일 이전 14일간 근무내역이 없습니다.")
        else:
            st.warning("❌ 조건 2 불충족: 신청일 이전 14일 내 근무기록이 존재합니다.")

    st.markdown("---")
    st.subheader("📌 최종 판단")
    if worker_type == "일반일용근로자":
        if condition1:
            st.success("✅ 일반일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지(2025-04-01 ~ 신청일) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만임을 확인합니다.**")
        else:
            st.error("❌ 일반일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되어 요건을 충족하지 못합니다.**")
    else:
        if condition1 or condition2:
            st.success("✅ 건설일용근로자 요건 충족\n\n**조건 1 또는 조건 2 중 하나를 충족하므로 요건을 만족합니다.**")
        else:
            st.error("❌ 건설일용근로자 요건 미충족\n\n**조건 1 및 조건 2를 모두 충족하지 못하였으므로 요건을 만족하지 않습니다.**")

if __name__ == "__main__":
    daily_worker_eligibility_app()
