import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import pytz

def get_date_range(apply_date):
    # Start from the first day of the previous month
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
    return pd.date_range(start=start_date, end=apply_date), start_date

def render_calendar(apply_date):
    # Inject custom CSS for styling buttons and text alignment
    st.markdown("""
    <style>
    /* Button container for centering */
    div.stButton {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    /* Button styling */
    div.stButton > button {
        width: 40px;
        height: 60px;
        font-size: 1rem;
        color: white;
        background-color: #1e1e1e;
        border: 1px solid #ccc;
        border-radius: 5px;
        transition: all 0.2s ease;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 0;
        position: relative;
    }
    /* Hover effect for unselected buttons */
    div.stButton > button:not(.selected):not(.current):not(.disabled):hover {
        border: 2px solid #00ff00;
        background-color: rgba(0, 255, 0, 0.2);
    }
    /* Selected button style - green background with blue border */
    div.stButton > button.selected {
        background-color: #00ff00;
        border: 2px solid #0000ff;
    }
    /* Current date style - blue background */
    div.stButton > button.current {
        background-color: #0000ff;
    }
    /* Disabled button style */
    div.stButton > button:disabled {
        cursor: not-allowed;
        background-color: #1e1e1e;
        border: 1px solid #ccc;
        color: gray;
    }
    /* Checkmark for selected buttons */
    div.stButton > button.selected::after {
        content: "✅";
        position: absolute;
        bottom: 5px;
        font-size: 0.8rem;
    }
    /* Day header styles */
    div[data-testid="stMarkdownContainer"] p {
        text-align: center;
        font-size: 0.9rem;
        margin: 0;
    }
    /* Month boundary styling */
    div[data-testid="stMarkdownContainer"] h3 {
        margin: 0.5rem 0;
        padding: 0.2rem;
        background-color: #2e2e2e;
        text-align: center;
        color: white;
    }
    /* Left-align text for results */
    div[data-testid="stMarkdownContainer"] {
        text-align: left !important;
    }
    /* PC layout (above 600px) */
    @media (min-width: 601px) {
        div.stButton > button {
            width: 40px;
            height: 60px;
            font-size: 1rem;
        }
    }
    /* Mobile layout (below 600px) */
    @media (max-width: 600px) {
        div.stButton > button {
            width: 35px;
            height: 55px;
            font-size: 0.8rem;
        }
        div.stButton > button.selected::after {
            font-size: 0.7rem;
            bottom: 3px;
        }
    }
    </style>
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

    # Display day headers
    cols = st.columns(7)
    for i, day in enumerate(korean_days):
        color = "red" if day == "일" else "blue" if day == "토" else "white"
        cols[i].markdown(f"<p style='color:{color}'>{day}</p>", unsafe_allow_html=True)

    for year, month in months:
        st.markdown(f"### {year} {korean_months[month]}", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)

        # Fill the calendar with days
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].empty()
                else:
                    date_obj = date(year, month, day)
                    date_str = date_obj.strftime("%Y-%m-%d")
                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date
                    is_disabled = date_obj > apply_date

                    # Define button style classes
                    button_class = ""
                    if is_selected:
                        button_class += " selected"
                    if is_current:
                        button_class += " current"

                    # Create button for the day
                    button_key = f"button_{date_str}"
                    if is_disabled:
                        cols[i].button(str(day), key=button_key, disabled=True)
                    else:
                        if cols[i].button(str(day), key=button_key, help=date_str):
                            toggle_date(date_obj)
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
    /* Left-align radio buttons */
    div[data-testid="stRadio"] {
        text-align: left !important;
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
    selected_days = render_calendar(apply_date)
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
