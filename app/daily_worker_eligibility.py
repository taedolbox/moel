import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import pytz

def get_date_range(apply_date):
    # Start from the first day of the previous month
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
    return pd.date_range(start=start_date, end=apply_date), start_date

def render_table(apply_date):
    # Inject custom CSS and JavaScript for styling and interaction
    st.markdown("""
    <style>
    /* Table styling */
    .calendar-table {
        border-collapse: collapse;
        width: 100%;
        max-width: 100%;
        margin: 0;
        padding: 0;
        background-color: #1e1e1e;
    }
    .calendar-table th, .calendar-table td.day-cell {
        border: 1px solid #ccc;
        width: 40px;
        height: 60px;
        text-align: center;
        padding: 0;
        margin: 0;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
    }
    /* Hover effect for unselected cells */
    .calendar-table td.day-cell:not(.selected):not(.current):not(.disabled):hover {
        border: 2px solid #00ff00;
        background-color: rgba(0, 255, 0, 0.2);
    }
    /* Selected cell style - green background with blue border */
    .calendar-table td.day-cell.selected {
        background-color: #00ff00;
        border: 2px solid #0000ff;
    }
    /* Current date style - blue background */
    .calendar-table td.day-cell.current {
        background-color: #0000ff;
    }
    /* Disabled cell style */
    .calendar-table td.day-cell.disabled {
        cursor: not-allowed;
        background-color: #1e1e1e;
        border: 1px solid #ccc;
    }
    .calendar-table td.day-cell.disabled .day-number {
        color: gray;
    }
    /* Day number styling */
    .day-number {
        font-size: 1rem;
        color: white;
        margin: 0;
        padding: 0;
        line-height: 30px;
        display: block;
    }
    /* Checkbox styling */
    .day-checkbox {
        margin: 0 auto;
        padding: 0;
        width: 16px;
        height: 16px;
        display: block;
    }
    /* Day header styles */
    .calendar-table th {
        font-size: 0.9rem;
        color: white;
        background-color: #2e2e2e;
    }
    /* PC layout (above 600px) */
    @media (min-width: 601px) {
        .calendar-table td.day-cell {
            width: 40px;
            height: 60px;
        }
        .day-number {
            font-size: 1rem;
        }
        .day-checkbox {
            width: 16px;
            height: 16px;
        }
    }
    /* Mobile layout (below 600px) */
    @media (max-width: 600px) {
        .calendar-table td.day-cell {
            width: 35px;
            height: 55px;
        }
        .day-number {
            font-size: 0.8rem;
            line-height: 25px;
        }
        .day-checkbox {
            width: 14px;
            height: 14px;
        }
    }
    /* Month boundary styling */
    div[data-testid="stMarkdownContainer"] h3 {
        margin: 0.5rem 0;
        padding: 0.2rem;
        background-color: #2e2e2e;
        text-align: center;
        color: white;
    }
    </style>
    <script>
    function toggleCheckbox(dateStr) {
        var checkbox = document.getElementById('checkbox-' + dateStr);
        if (checkbox) {
            checkbox.click();
        }
    }
    </script>
    """, unsafe_allow_html=True)

    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
    end_date = apply_date
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=end_date)))

    # Initialize selected dates in session state if not already present
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    # Set current date with KST
    kst = pytz.timezone('Asia/Seoul')
    current_date = datetime.now(kst).date()

    # Korean month names
    korean_months = [
        "", "1월", "2월", "3월", "4월", "5월", "6월",
        "7월", "8월", "9월", "10월", "11월", "12월"
    ]
    # Korean day names
    korean_days = ["일", "월", "화", "수", "목", "금", "토"]

    # Set calendar to start on Sunday
    calendar.setfirstweekday(calendar.SUNDAY)

    for year, month in months:
        st.markdown(f"### {year} {korean_months[month]}", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)

        # Generate table HTML
        table_html = "<table class='calendar-table'><tr>"
        # Add day headers
        for day in korean_days:
            color = "red" if day == "일" else "blue" if day == "토" else "white"
            table_html += f"<th style='color:{color}'>{day}</th>"
        table_html += "</tr>"

        # Fill the table with days
        for week in cal:
            table_html += "<tr>"
            for day in week:
                if day == 0:
                    table_html += "<td></td>"
                else:
                    date_obj = date(year, month, day)
                    date_str = date_obj.strftime("%Y-%m-%d")
                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date
                    is_disabled = date_obj > apply_date

                    # Define cell classes
                    cell_classes = "day-cell"
                    if is_selected:
                        cell_classes += " selected"
                    if is_current:
                        cell_classes += " current"
                    if is_disabled:
                        cell_classes += " disabled"

                    # Create cell content
                    if is_disabled:
                        table_html += f"<td class='{cell_classes}'><div class='day-number'>{day}</div><div style='height: 16px;'></div></td>"
                    else:
                        table_html += f"""
                        <td class='{cell_classes}' onclick="toggleCheckbox('{date_str}')">
                            <div class='day-number'>{day}</div>
                            <input type='checkbox' id='checkbox-{date_str}' class='day-checkbox' {'checked' if is_selected else ''} onchange="this.closest('td').classList.toggle('selected', this.checked)">
                        </td>
                        """
            table_html += "</tr>"
        table_html += "</table>"

        st.markdown(table_html, unsafe_allow_html=True)

        # Hidden Streamlit checkbox to manage state
        for day in [date(year, month, d) for week in cal for d in week if d != 0]:
            if day <= apply_date:
                checkbox_key = f"checkbox_{day}"
                is_checked = st.checkbox("", value=day in selected_dates, key=checkbox_key, on_change=toggle_date, kwargs={"date_obj": day}, label_visibility="hidden")
                if is_checked != (day in selected_dates):
                    toggle_date(day)
                    st.rerun()

    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자", unsafe_allow_html=True)
        st.markdown(", ".join([date.strftime("%Y-%m-%d") for date in sorted(selected_dates)]), unsafe_allow_html=True)

    return selected_dates

def toggle_date(date_obj):
    # Ensure selected_dates exists in session state
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    
    if date_obj in st.session_state.selected_dates:
        st.session_state.selected_dates.remove(date_obj)
    else:
        st.session_state.selected_dates.add(date_obj)

def daily_worker_eligibility_app():
    st.markdown("""
    <style>
    div[data-testid="stRadio"] label {
        color: white;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.header("일용근로자 수급자격 요건 모의계산")

    # Display current date and time in Korean with KST
    kst = pytz.timezone('Asia/Seoul')
    current_datetime = datetime.now(kst)
    st.markdown(f"**오늘 날짜와 시간**: {current_datetime.strftime('%Y년 %m월 %d일 %A 오전 %I:%M KST')}", unsafe_allow_html=True)

    # Display conditions at the top
    st.markdown("### 📋 요건 조건", unsafe_allow_html=True)
    st.markdown("- **조건 1**: 수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지의 근로일 수가 총 일수의 1/3 미만이어야 합니다.", unsafe_allow_html=True)
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 수급자격 인정신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).", unsafe_allow_html=True)
    st.markdown("---", unsafe_allow_html=True)

    worker_type = st.radio("근로자 유형을 선택하세요", ["일반일용근로자", "건설일용근로자"])

    # Set initial apply_date to today
    kst = pytz.timezone('Asia/Seoul')
    initial_date = datetime.now(kst).date()
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=initial_date)
    date_range, start_date = get_date_range(apply_date)

    st.markdown("---", unsafe_allow_html=True)
    st.markdown("#### ✅ 근무일 선택 달력", unsafe_allow_html=True)
    selected_days = render_table(apply_date)
    st.markdown("---", unsafe_allow_html=True)

    total_days = len(date_range)
    worked_days = len(selected_days)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**", unsafe_allow_html=True)
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**", unsafe_allow_html=True)
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**", unsafe_allow_html=True)

    condition1 = worked_days < threshold
    if condition1:
        st.success("✅ 조건 1 충족: 근무일 수가 기준 미만입니다.")
    else:
        st.warning("❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.")

    condition2 = False
    if worker_type == "건설일용근로자":
        fourteen_days_prior_end = apply_date - timedelta(days=1)
        fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
        fourteen_days_prior = pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)
        # Convert selected_days to a set of dates for comparison
        selected_dates_set = set(d for d in selected_days)
        # Check if any date in the 14-day range is in selected_dates
        no_work_14_days = all(day not in selected_dates_set for day in fourteen_days_prior)
        condition2 = no_work_14_days

        if no_work_14_days:
            st.success(f"✅ 조건 2 충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 없습니다.")
        else:
            st.warning(f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재합니다.")

    st.markdown("---", unsafe_allow_html=True)

    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?", unsafe_allow_html=True)
        future_dates = [apply_date + timedelta(days=i) for i in range(1, 31)]
        for future_date in future_dates:
            date_range_future, _ = get_date_range(future_date)
            total_days_future = len(date_range_future)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_days if d <= future_date)
            if worked_days_future < threshold_future:
                st.info(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후에 신청하면 요건을 충족할 수 있습니다.")
                break
        else:
            st.warning("❗앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.")

    if worker_type == "건설일용근로자" and not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?", unsafe_allow_html=True)
        last_worked_day = max((d for d in selected_days if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.info(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.info("이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.")

    st.subheader("📌 최종 판단")
    if worker_type == "일반일용근로자":
        if condition1:
            st.success(f"✅ 일반일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만**")
        else:
            st.error("❌ 일반일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되어 요건을 충족하지 못합니다.**")
    else:
        fourteen_days_prior_end = apply_date - timedelta(days=1)
        fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
        if condition1 or condition2:
            st.success(f"✅ 건설일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 총 일수의 3분의 1 미만임을 확인하거나, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무 사실이 없음을 확인합니다.**")
        else:
            st.error(f"❌ 건설일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되고, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재하므로 요건을 충족하지 못합니다.**")

if __name__ == "__main__":
    daily_worker_eligibility_app()
    
