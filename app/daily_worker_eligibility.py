import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import pytz
import time

# 달력 시작 요일 설정
calendar.setfirstweekday(calendar.SUNDAY)

# KST 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# 스타일시트 로드 (캐시 방지 쿼리 추가)
timestamp = time.time()
try:
    with open("static/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.error("CSS 파일을 찾을 수 없습니다. 경로를 확인하세요: static/styles.css")
    # 대안: CSS를 직접 삽입
    st.markdown("""
    <style>
    /* 아래 CSS 코드 삽입 */
    div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(7, 1fr) !important;
        gap: 0px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        justify-content: flex-start !important;
    }
    div[data-testid="stMarkdownContainer"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        height: 100% !important;
        text-align: left !important;
    }
    div[data-testid="stMarkdownContainer"]:not(:has(.day-header)):not(:has(.day)) {
        justify-content: flex-start !important;
    }
    .month-container {
        margin-bottom: 4rem !important;
    }
    .day-header {
        text-align: center !important;
        font-weight: bold !important;
        margin: 0 auto !important;
        padding: 0 !important;
        color: #333 !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;
        aspect-ratio: 1/1 !important;
        line-height: 40px !important;
        border: 1px solid #ccc !important;
        border-radius: 50% !important;
        background-color: #f8f8f8 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    .day-header.sunday {
        color: red !important;
    }
    .day-header.saturday {
        color: blue !important;
    }
    .day {
        text-align: center !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;
        aspect-ratio: 1/1 !important;
        line-height: 40px !important;
        border: 1px solid #ccc !important;
        border-radius: 50% !important;
        margin: 0 auto !important;
        background-color: #fff !important;
        color: #333 !important;
        cursor: pointer !important;
        transition: background-color 0.2s, border 0.2s !important;
        position: relative !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        z-index: 6000 !important;
        pointer-events: auto !important;
        touch-action: manipulation !important;
        padding: 10px !important;
    }
    .day:not(.disabled):hover::before {
        content: '숫자 오른쪽을 클릭해주세요' !important;
        position: absolute !important;
        right: 50px !important;
        top: 0 !important;
        background-color: #333 !important;
        color: #fff !important;
        padding: 5px 10px !important;
        border-radius: 4px !important;
        font-size: 12px !important;
        white-space: nowrap !important;
        z-index: 7000 !important;
        opacity: 0.9 !important;
        pointer-events: none !important;
    }
    .day:not(.disabled):hover::after,
    .day:not(.disabled):active::after {
        content: '' !important;
        position: absolute !important;
        width: 8px !important;
        height: 8px !important;
        background-color: #00ff00 !important;
        border-radius: 50% !important;
        left: -10px !important;
        top: 20px !important;
        z-index: 7000 !important;
        opacity: 1 !important;
        animation: fadeOut 1s forwards !important;
    }
    @keyframes fadeOut {
        0% { opacity: 1; }
        100% { opacity: 0; }
    }
    .day.selected {
        border: 2px solid #4444ff !important; /* 파란색 테두리 */
        font-weight: bold !important;
        background-color: #e6e6ff !important;
    }
    .stCheckbox {
        position: absolute !important;
        width: 40px !important;
        height: 40px !important;
        left: 0 !important;
        top: 0 !important;
        z-index: 6500 !important;
        opacity: 0 !important;
        pointer-events: auto !important;
        cursor: pointer !important;
    }
    .stCheckbox > div > div {
        display: block !important;
        width: 40px !important;
        height: 40px !important;
        border: none !important;
        background-color: transparent !important;
    }
    .result-text {
        margin: 10px 0 !important;
        padding: 10px !important;
        border-left: 4px solid #36A2EB !important;
        background-color: #f9f9f9 !important;
    }
    @media (max-width: 767px) {
        div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: repeat(7, 1fr) !important;
            gap: 2px !important;
            justify-content: flex-start !important;
            margin-left: 0 !important;
        }
        .day {
            width: 40px !important;
            height: 40px !important;
            min-width: 40px !important;
            min-height: 40px !important;
            aspect-ratio: 1/1 !important;
            line-height: 40px !important;
            font-size: 1em !important;
            margin: 2px auto !important;
            padding: 15px !important;
            touch-action: manipulation !important;
        }
        .day.selected {
            border: 2px solid #4444ff !important;
            font-weight: bold !important;
            background-color: #e6e6ff !important;
        }
    }
    @media (min-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            max-width: 600px !important;
            margin: 0 !important;
            justify-content: flex-start !important;
        }
    }
    .stMarkdown, .stText, .stHeader {
        text-align: left !important;
    }
    @media (prefers-color-scheme: dark), [data-theme="dark"] {
        .day-header {
            color: #ddd !important;
            background-color: #444 !important;
        }
        .day-header.sunday {
            color: red !important;
        }
        .day-header.saturday {
            color: blue !important;
        }
        .day {
            background-color: #333 !important;
            color: #ddd !important;
            border-color: #888 !important;
        }
        .day:hover:not(.disabled) {
            background-color: #444 !important;
        }
        .day:not(.disabled):hover::before {
            background-color: #555 !important;
            color: #fff !important;
        }
        .day.disabled {
            background-color: #555 !important;
            color: #888 !important;
        }
        .day.selected {
            border: 2px solid #6666ff !important;
            font-weight: bold !important;
            background-color: #4a2a2a !important;
        }
        .day.current {
            border-color: #6666ff !important;
        }
        .result-text {
            background-color: #2a2a2a !important;
            border-left-color: #4CAF50 !important;
        }
    }
    .day:hover:not(.disabled) {
        background-color: #f0f0f0 !important;
    }
    .day.current {
        border: 2px solid #4444ff !important;
    }
    .day.disabled {
        background-color: #e0e0e0 !important;
        color: #888 !important;
        cursor: not-allowed !important;
    }
    </style>
    """, unsafe_allow_html=True)

def get_date_range(apply_date):
    """신청일을 기준으로 이전 달 초일부터 신청일까지의 날짜 범위를 반환합니다."""
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar(apply_date):
    """달력을 렌더링하고 날짜 선택 기능을 제공합니다."""
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = datetime.now(KST).date()
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=apply_date)))

    for year, month in months:
        # 달력 간격을 위해 month-container 추가
        with st.container():
            st.markdown(f'<div class="month-container"><h3>{year}년 {month}월</h3></div>', unsafe_allow_html=True)
            cal = calendar.monthcalendar(year, month)
            days_of_week = ["일", "월", "화", "수", "목", "금", "토"]

            # 요일 헤더
            with st.container():
                cols = st.columns(7, gap="small")
                for i, day in enumerate(days_of_week):
                    with cols[i]:
                        class_name = "day-header"
                        if i == 0:
                            class_name += " sunday"
                        elif i == 6:
                            class_name += " saturday"
                        st.markdown(f'<div class="{class_name}">{day}</div>', unsafe_allow_html=True)

            # 날짜 렌더링
            for week in cal:
                with st.container():
                    cols = st.columns(7, gap="small")
                    for i, day in enumerate(week):
                        with cols[i]:
                            if day == 0:
                                st.empty()
                                continue
                            date_obj = date(year, month, day)
                            is_selected = date_obj in selected_dates
                            is_current = date_obj == current_date
                            is_disabled = date_obj > apply_date

                            class_name = "day"
                            if is_selected:
                                class_name += " selected"
                            if is_current:
                                class_name += " current"
                            if is_disabled:
                                class_name += " disabled"

                            with st.container():
                                if is_disabled:
                                    st.markdown(f'<div class="{class_name}">{day}</div>', unsafe_allow_html=True)
                                else:
                                    with st.container():
                                        checkbox_key = f"date_{date_obj}"
                                        checkbox_value = st.checkbox(
                                            "", key=checkbox_key, value=is_selected, label_visibility="hidden"
                                        )
                                        st.markdown(
                                            f'<div class="{class_name}" data-date="{date_obj}">{day}</div>',
                                            unsafe_allow_html=True
                                        )
                                        if checkbox_value != is_selected:
                                            if checkbox_value:
                                                selected_dates.add(date_obj)
                                            else:
                                                selected_dates.discard(date_obj)
                                            st.session_state.selected_dates = selected_dates
                                            st.rerun()

    # 선택된 근무일자 표시
    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%m/%d") for d in sorted(selected_dates)]))

    return st.session_state.selected_dates

def daily_worker_eligibility_app():
    """일용근로자 수급자격 요건 모의계산 앱."""
    st.header("일용근로자 수급자격 요건 모의계산")

    current_datetime = datetime.now(KST)
    current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %I:%M KST')

    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 수급자격 인정신청일의 직전 달 초일부터 신청일까지의 근무일 수가 총 일의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date(), key="apply_date_input")

    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### 근무일 선택 달력")
    selected_dates = render_calendar(apply_date)
    st.markdown("---")

    total_days = len(date_range_objects)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 1 충족: 근무일 수가 기준 미만입니다." if condition1 else "❌ 조건 1 불충족: 근무일 수가 기준 이상입니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    no_work_14_days = all(day not in selected_dates for day in fourteen_days_prior_range)
    condition2 = no_work_14_days

    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 2 충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 근무내역이 없습니다." if no_work_14_days else "❌ 조건 2 불충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 내 근무기록이 존재합니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        found_suggestion = False
        for i in range(1, 31):
            future_date = apply_date + timedelta(days=i)
            date_range_future_objects, _ = get_date_range(future_date)
            total_days_future = len(date_range_future_objects)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_dates if d <= future_date)

            if worked_days_future < threshold_future:
                st.markdown(
                    f'<div class="result-text">'
                    f'<p>✅ <b>{future_date.strftime("%Y-%m-%d")}</b> 이후에 신청하면 요건을 충족할 수 있습니다.</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                found_suggestion = True
                break
        if not found_suggestion:
            st.markdown(
                f'<div class="result-text">'
                f'<p>❗ 앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    if not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        last_worked_day = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.markdown(
                f'<div class="result-text">'
                f'<p>✅ <b>{suggested_date.strftime("%Y-%m-%d")}</b> 이후에 신청하면 조건 2를 충족할 수 있습니다.</p>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="result-text">'
                f'<p>이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.subheader("📌 최종 판단")
    if condition1:
        st.markdown(
            f'<div class="result-text">'
            f'<p>✅ 일반일용근로자: 신청 가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="result-text">'
            f'<p>❌ 일반일용근로자: 신청 불가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )

    if condition1 and condition2:
        st.markdown(
            f'<div class="result-text">'
            f'<p>✅ 건설일용근로자: 신청 가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 총 일수의 3분의 1 미만이고, 신청일 직전 14일간({fourteen_days_prior_start.strftime("%Y-%m-%d")} ~ {fourteen_days_prior_end.strftime("%Y-%m-%d")}) 근무 사실이 없음을 확인합니다.</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        error_message = "❌ 건설일용근로자: 신청 불가능<br>"
        if not condition1:
            error_message += f"<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.</b><br>"
        if not condition2:
            error_message += f"<b>신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 있습니다.</b>"
        st.markdown(
            f'<div class="result-text">'
            f'<p>{error_message}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    daily_worker_eligibility_app()
