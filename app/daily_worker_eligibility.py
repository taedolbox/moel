import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar


def get_date_range(apply_date):
    start_date = apply_date.replace(month=4, day=1)
    return pd.date_range(start=start_date, end=apply_date)


def render_calendar(apply_date, selected_dates):
    start_date = apply_date.replace(month=4, day=1)
    end_date = apply_date
    current = start_date

    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=end_date)))

    for year, month in months:
        st.markdown(f"### {year}년 {month}월")
        cal = calendar.monthcalendar(year, month)
        days = ["월", "화", "수", "목", "금", "토", "일"]
        st.markdown("| " + " | ".join(days) + " |")
        st.markdown("|" + "---|" * 7)

        for week in cal:
            row = []
            for day in week:
                if day == 0:
                    row.append(" ")
                else:
                    date = datetime(year, month, day).date()
                    mark = "⭕" if date in selected_dates else f"{day}"
                    row.append(mark)
            st.markdown("| " + " | ".join(row) + " |")


def daily_worker_eligibility_app():
    st.header("수급자격 - 일용근로자 수급자격 요건 모의계산")

    worker_type = st.radio("근로자 유형을 선택하세요", ["일반일용근로자", "건설일용근로자"])

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.today())
    date_range = get_date_range(apply_date)
    date_labels = [d.strftime('%Y-%m-%d') for d in date_range]

    selected_day_labels = st.multiselect("근무일자 선택 (아래 달력에 표시됩니다)", options=date_labels)
    selected_days = set(pd.to_datetime(selected_day_labels).date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    render_calendar(apply_date, selected_days)
    st.markdown("---")

    # 조건 1: 직전달 1일부터 신청일까지 총일수 대비 근무일 비율
    total_days = len(date_range)
    worked_days = len(selected_days)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")

    condition1 = worked_days < threshold
    if condition1:
        st.success("✅ 조건 1 충족: 근무일 수가 기준 미만입니다.")
    else:
        st.warning("❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.")

    # 조건 2: 신청일 이전 14일간 근무 내역 없음
    condition2 = False
    if worker_type == "건설일용근로자":
        fourteen_days_prior = [apply_date.date() - timedelta(days=i) for i in range(1, 15)]
        no_work_14_days = all(day not in selected_days for day in fourteen_days_prior)
        condition2 = no_work_14_days

        if no_work_14_days:
            st.success("✅ 조건 2 충족: 신청일 이전 14일간 근무내역이 없습니다.")
        else:
            st.warning("❌ 조건 2 불충족: 신청일 이전 14일 내 근무기록이 존재합니다.")

    # 종합 판단
    st.markdown("---")
    st.subheader("📌 최종 판단")
    if worker_type == "일반일용근로자":
        if condition1:
            st.success("✅ 일반일용근로자 요건 충족")
        else:
            st.error("❌ 일반일용근로자 요건 미충족")
    else:
        if condition1 or condition2:
            st.success("✅ 건설일용근로자 요건 충족")
        else:
            st.error("❌ 건설일용근로자 요건 미충족")


if __name__ == "__main__":
    daily_worker_eligibility_app()

