import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from app.questions import get_daily_worker_eligibility_questions
import calendar

# 달력의 시작 요일을 일요일로 설정
calendar.setfirstweekday(calendar.SUNDAY)

# 현재 날짜와 시간을 KST로 설정 (2025년 5월 25일 오후 2시 11분 KST)
current_datetime = datetime(2025, 5, 25, 14, 11)
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %I:%M KST')

def get_date_range(apply_date):
    """신청일을 기준으로 이전 달 초일부터 신청일까지의 날짜 범위를 반환합니다."""
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar_interactive(apply_date):
    """달력을 렌더링하고 날짜 선택 기능을 제공합니다."""
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()

    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar)))

    st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
    }
    div[data-testid="stMarkdownContainer"] h3 {
        background-color: #f0f0f0;
        color: #000000;
        text-align: center;
        padding: 10px;
        font-size: 1.5em;
        width: 100%;
        border-radius: 5px;
    }
    @media (prefers-color-scheme: dark) {
        div[data-testid="stMarkdownContainer"] h3 {
            background-color: #2e2e2e;
            color: #ffffff;
        }
    }
    .day-header span {
        font-size: 1.1em;
        font-weight: bold;
        text-align: center;
        display: block;
        color: #000000;
    }
    .day-header:nth-child(1) span { color: red; }
    .day-header:nth-child(7) span { color: blue; }
    @media (prefers-color-scheme: dark) {
        .day-header span { color: #ffffff; }
        .day-header:nth-child(1) span { color: #ff5555; }
        .day-header:nth-child(7) span { color: #5555ff; }
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        max-width: 100%;
        margin: 0 auto;
        gap: 2px;
    }
    div[data-testid="stHorizontalBlock"] > div {
        flex-basis: calc(100% / 7 - 4px) !important;
        min-width: 40px !important;
        max-width: calc(100% / 7) !important;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    div[data-testid="stCheckbox"] {
        width: 40px !important;
        height: 40px !important;
        margin: 2px;
    }
    div[data-testid="stCheckbox"] label {
        width: 100% !important;
        height: 100% !important;
        border: 1px solid #ddd;
        border-radius: 50%;
        background-color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }
    div[data-testid="stCheckbox"] label div[data-testid="stMarkdownContainer"] p {
        font-size: 1em;
        color: #000000;
        margin: 0;
    }
    div[data-testid="stCheckbox"] input:checked + label {
        background-color: #4CAF50;
        border-color: #4CAF50;
    }
    div[data-testid="stCheckbox"] input:checked + label div[data-testid="stMarkdownContainer"] p {
        color: #ffffff;
    }
    div[data-testid="stCheckbox"].current-day label {
        border: 2px solid blue;
    }
    div[data-testid="stCheckbox"].disabled label {
        background-color: #e0e0e0;
        border-color: #aaa;
        cursor: not-allowed;
        opacity: 0.6;
    }
    @media (prefers-color-scheme: dark) {
        div[data-testid="stCheckbox"] label {
            border-color: #444;
            background-color: #1e1e1e;
        }
        div[data-testid="stCheckbox"] label div[data-testid="stMarkdownContainer"] p {
            color: #ffffff;
        }
        div[data-testid="stCheckbox"].disabled label {
            background-color: #2e2e2e;
            border-color: #666;
        }
        div[data-testid="stCheckbox"].current-day label {
            border-color: #00f;
        }
    }
    @media (max-width: 600px) {
        div[data-testid="stHorizontalBlock"] > div {
            flex-basis: calc(100% / 7 - 2px) !important;
            min-width: 35px !important;
            max-width: calc(100% / 7) !important;
        }
        div[data-testid="stCheckbox"] {
            width: 35px !important;
            height: 35px !important;
        }
        div[data-testid="stCheckbox"] label div[data-testid="stMarkdownContainer"] p {
            font-size: 0.9em;
        }
        .day-header span {
            font-size: 0.9em;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    for year, month in months_to_display:
        st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

        cols = st.columns(7, gap="small")
        for i, day_name in enumerate(days_of_week_korean):
            cols[i].markdown(f'<div class="day-header"><span>{day_name}</span></div>', unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7, gap="small")
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown(" ")
                    continue

                date_obj = date(year, month, day)
                if date_obj > apply_date:
                    cols[i].markdown(" ")
                    continue

                is_current = date_obj == current_date
                is_selected = date_obj in selected_dates

                classes = ["stCheckbox"]
                if is_current:
                    classes.append("current-day")
                if date_obj > apply_date:
                    classes.append("disabled")

                with cols[i]:
                    st.markdown(f'<div data-testid="{" ".join(classes)}">', unsafe_allow_html=True)
                    checked = st.checkbox(
                        label=str(day),
                        value=is_selected,
                        key=f"date_{date_obj}",
                        disabled=(date_obj > apply_date),
                        label_visibility="visible"
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

                    if checked and not is_selected:
                        selected_dates.add(date_obj)
                    elif not checked and is_selected:
                        selected_dates.discard(date_obj)

    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join(d.strftime("%Y-%m-%d") for d in sorted(selected_dates)))

    return selected_dates

def daily_worker_eligibility_app():
    """일용근로자 수급자격 요건 모의계산 앱의 메인 함수입니다."""
    st.header("일용근로자 수급자격 요건 모의계산")

    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}")

    st.markdown("""
    ### 📋 요건 조건
    - **조건 1**: 수급자격 인정신청일이 속한 달의 직전 달 초일부터 신청일까지 근로일 수가 총 일수의 1/3 미만이어야 합니다.
    - **조건 2 (건설일용근로자만 해당)**: 신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).
    """)
    st.markdown("---")

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date(), key="apply_date_input")

    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("#### ✅ 근무일 선택 달력")
    selected_days = render_calendar_interactive(apply_date)
    st.markdown("---")

    total_days = len(date_range_objects)
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

    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    no_work_14_days = all(day not in selected_days for day in fourteen_days_prior_range)
    condition2 = no_work_14_days

    if no_work_14_days:
        st.success(f"✅ 조건 2 충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 없습니다.")
    else:
        st.warning(f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재합니다.")

    st.markdown("---")

    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        found_suggestion = False
        for i in range(1, 31):
            future_date = apply_date + timedelta(days=i)
            date_range_future_objects, _ = get_date_range(future_date)
            total_days_future = len(date_range_future_objects)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_days if d <= future_date)

            if worked_days_future < threshold_future:
                st.info(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후에 신청하면 요건을 충족할 수 있습니다.")
                found_suggestion = True
                break
        if not found_suggestion:
            st.warning("❗앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.")

    if not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        last_worked_day = max((d for d in selected_days if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.info(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.info("이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.")

    st.subheader("📌 최종 판단")
    if condition1:
        st.success(f"✅ 일반일용근로자: 신청 가능\n\n**{start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')} 근로일 수의 합이 총 일수의 3분의 1 미만**")
    else:
        st.error(f"❌ 일반일용근로자: 신청 불가능\n\n**{start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')} 근로일 수의 합이 총 일수의 3분의 1 이상**")

    if condition1 and condition2:
        st.success(f"✅ 건설일용근로자: 신청 가능\n\n**{start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')} 근로일 수의 합이 총 일수의 3분의 1 미만이고, {fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')} 근무 사실 없음**")
    else:
        error_message = "❌ 건설일용근로자: 신청 불가능\n\n"
        if not condition1:
            error_message += f"**{start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')} 근로일 수의 합이 총 일수의 3분의 1 이상**\n\n"
        if not condition2:
            error_message += f"**{fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')} 근무내역 있음**"
        st.error(error_message)

if __name__ == "__main__":
    daily_worker_eligibility_app()

