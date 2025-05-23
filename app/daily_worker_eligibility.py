import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

def get_date_range(apply_date):
    start_date = apply_date.replace(month=4, day=1)
    return pd.date_range(start=start_date, end=apply_date)

def render_calendar(apply_date):
    # Inject custom CSS for table layout and button styling
    st.markdown("""
    <style>
    /* Table styling */
    .calendar-table {
        width: 100%;
        border-collapse: collapse;
        margin: 0 auto;
        background-color: #1e1e1e; /* Dark background to match image */
    }
    .calendar-table th, .calendar-table td {
        border: 1px solid #444; /* Subtle border for table cells */
        padding: 5px;
        text-align: center; /* Center align text and buttons */
        vertical-align: middle;
        min-width: 40px;
    }
    /* Day header styling */
    .calendar-table th {
        font-size: 0.9rem;
        color: white;
        background-color: #2e2e2e; /* Slightly lighter header background */
    }
    .calendar-table th:first-child {
        color: red; /* Sunday */
    }
    .calendar-table th:last-child {
        color: blue; /* Saturday */
    }
    /* Style for calendar day buttons */
    .calendar-table button {
        width: 40px;
        height: 40px;
        border-radius: 50%; /* Circular buttons */
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        padding: 0;
        margin: 0 auto;
        border: 2px solid transparent;
        background-color: transparent;
        color: white;
    }
    /* Hover and selected effect */
    .calendar-table button[kind="secondary"]:hover {
        border: 2px solid #00ff00; /* Green border on hover */
        background-color: rgba(0, 255, 0, 0.3); /* Light green background */
    }
    /* Selected button style */
    .calendar-table button.selected {
        border: 2px solid #00ff00; /* Green border for selected days */
        background-color: rgba(0, 255, 0, 0.3); /* Light green background */
    }
    /* Disabled (future) day style */
    .calendar-table button[disabled] {
        color: gray;
        background-color: transparent;
        border: 2px solid transparent;
    }
    /* Force horizontal layout on mobile */
    @media (max-width: 600px) {
        .calendar-table {
            width: 100%;
            table-layout: fixed; /* Ensure equal column widths */
        }
        .calendar-table th, .calendar-table td {
            min-width: 35px;
            padding: 3px;
        }
        .calendar-table button {
            font-size: 0.8rem;
            width: 35px;
            height: 35px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    start_date = apply_date.replace(month=4, day=1)
    end_date = apply_date
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=end_date)))

    # Initialize selected dates in session state if not already present
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates

    for year, month in months:
        st.markdown(f"### {year}년 {month}월")
        cal = calendar.monthcalendar(year, month)
        days = ["일", "월", "화", "수", "목", "금", "토"]

        # Create HTML table for calendar
        table_html = '<table class="calendar-table">'
        # Header row
        table_html += '<tr>'
        for day in days:
            table_html += f'<th>{day}</th>'
        table_html += '</tr>'

        # Calendar grid
        for week in cal:
            table_html += '<tr>'
            for day in week:
                if day == 0:
                    table_html += '<td></td>'
                else:
                    date_obj = date(year, month, day)
                    if date_obj > apply_date:
                        button_key = f"btn_{date_obj}"
                        button_html = f'<button disabled>{day}</button>'
                        table_html += f'<td>{button_html}</td>'
                    else:
                        button_key = f"btn_{date_obj}"
                        is_selected = date_obj in selected_dates
                        # Add selected class if the date is selected
                        button_class = "selected" if is_selected else ""
                        button_html = f'<div id="{button_key}"></div>'
                        table_html += f'<td>{button_html}</td>'
            table_html += '</tr>'
        table_html += '</table>'
        st.markdown(table_html, unsafe_allow_html=True)

        # Render buttons separately to handle clicks
        for week in cal:
            for day in week:
                if day != 0:
                    date_obj = date(year, month, day)
                    if date_obj > apply_date:
                        continue
                    button_key = f"btn_{date_obj}"
                    is_selected = date_obj in selected_dates
                    # Use class to indicate selected state
                    with st.container():
                        if st.button(
                            str(day),
                            key=button_key,
                            on_click=lambda d=date_obj: st.session_state.selected_dates.add(d) if d not in st.session_state.selected_dates else st.session_state.selected_dates.remove(d),
                            help="클릭하여 근무일을 선택하거나 해제하세요",
                            args=(date_obj,)
                        ):
                            st.rerun()

    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([date.strftime("%Y-%m-%d") for date in sorted(selected_dates)]))

    return selected_dates

def daily_worker_eligibility_app():
    st.markdown("""
<style>
div[data-testid="stRadio"] label {
    color: white !important;
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

    st.header("일용근로자 수급자격 요건 모의계산")

    worker_type = st.radio("근로자 유형을 선택하세요", ["일반일용근로자", "건설일용근로자"])

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.today().date())
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

    # 조건 불충족 시 대안 신청일 계산
    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        future_dates = [apply_date + timedelta(days=i) for i in range(1, 31)]
        for future_date in future_dates:
            date_range_future = pd.date_range(start=future_date.replace(month=4, day=1), end=future_date)
            total_days_future = len(date_range_future)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_days if d <= future_date)
            if worked_days_future < threshold_future:
                st.info(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후에 신청하면 요건을 충족할 수 있습니다.")
                break
        else:
            st.warning("❗앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.")

    if worker_type == "건설일용근로자" and not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        last_worked_day = max((d for d in selected_days if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.info(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.info("이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.")

    st.subheader("📌 최종 판단")
    if worker_type == "일반일용근로자":
        if condition1:
            st.success(f"✅ 일반일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지(2025-04-01 ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만**")
        else:
            st.error("❌ 일반일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되어 요건을 충족하지 못합니다.**")
    else:
        if condition1 or condition2:
            st.success(f"✅ 건설일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지(2025-04-01 ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 총 일수의 3분의 1 미만임을 확인하거나, 신청일 이전 14일간({(apply_date - timedelta(days=14)).strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근무 사실이 없음을 확인합니다.**")
        else:
            st.error(f"❌ 건설일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되고, 신청일 이전 14일간({(apply_date - timedelta(days=14)).strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 내 근무기록이 존재하므로 요건을 충족하지 못합니다.**")

if __name__ == "__main__":
    daily_worker_eligibility_app()
