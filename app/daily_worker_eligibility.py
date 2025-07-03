import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import pytz

calendar.setfirstweekday(calendar.SUNDAY)
KST = pytz.timezone('Asia/Seoul')


def get_date_range(apply_date):
    start_of_apply_month = apply_date.replace(day=1)
    start_date = (start_of_apply_month - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date


def render_calendar(apply_date):
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = datetime.now(KST).date()

    start_of_prev_month = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    months_to_render = sorted(set(
        (d.year, d.month) for d in pd.date_range(start=start_of_prev_month, end=apply_date)
    ))

    for year, month in months_to_render:
        st.markdown(f"### {year}년 {month}월", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)

        day_headers = ["일", "월", "화", "수", "목", "금", "토"]
        cols = st.columns(7)
        for i, day_name in enumerate(day_headers):
            with cols[i]:
                st.markdown(f'<div class="day-header">{day_name}</div>', unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7)
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

                    checkbox_key = f"date_{date_obj}"
                    checkbox_value = st.checkbox(
                        "", key=checkbox_key, value=is_selected,
                        label_visibility="hidden", disabled=is_disabled
                    )

                    st.markdown(
                        f'<div class="{class_name}">{day}</div>',
                        unsafe_allow_html=True
                    )

                    if not is_disabled and checkbox_value != is_selected:
                        if checkbox_value:
                            selected_dates.add(date_obj)
                        else:
                            selected_dates.discard(date_obj)
                        st.session_state.selected_dates = selected_dates
                        st.rerun()

    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%m/%d") for d in sorted(selected_dates)]))

    return st.session_state.selected_dates


def daily_worker_eligibility_app():
    st.header("📋 일용근로자 수급자격 요건 모의계산")

    now_kst = datetime.now(KST)
    st.markdown(f"**오늘 날짜와 시간**: {now_kst.strftime('%Y년 %m월 %d일 %A %p %I:%M KST')}", unsafe_allow_html=True)

    st.markdown("""
    ### 📌 요건 조건
    - **조건 1:** 수급자격 인정신청일의 직전 달 초일부터 신청일까지의 근무일 수가 총 일수의 **1/3 미만**이어야 합니다.
    - **조건 2 (건설일용근로자만):** 신청일 직전 **14일간** 근무 사실이 없어야 합니다 (**신청일 제외**).
    """)

    st.markdown("---")

    apply_date = st.date_input("📅 수급자격 인정신청일 선택", value=now_kst.date(), key="apply_date_input")
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("### 근무일 선택 달력")
    selected_dates = render_calendar(apply_date)

    st.markdown("""
    <style>
    .day {
        display: inline-block;
        width: 40px;
        height: 40px;
        margin: 2px;
        line-height: 40px;
        text-align: center;
        border: 1px solid #ddd;
        border-radius: 50%;
        cursor: pointer;
        background: white;
        user-select: none;
    }
    .day:hover {
        background: #eee;
    }
    .day.selected {
        background: #2196F3;
        color: white;
        border: 2px solid #2196F3;
    }
    .day.current {
        border: 2px solid #4CAF50;
    }
    .day.disabled {
        background: #f0f0f0;
        color: #999;
        cursor: not-allowed;
    }
    .day-header {
        text-align: center;
        font-weight: bold;
    }
    .result-text {
        margin-top: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("---")

    total_days = len(date_range_objects)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    st.markdown(f"- **총 기간 일수:** {total_days}일")
    st.markdown(f"- **기준 (총일수의 1/3):** {threshold:.1f}일")
    st.markdown(f"- **선택한 근무일 수:** {worked_days}일")

    condition1 = worked_days < threshold
    condition2 = True

    fourteen_end = apply_date - timedelta(days=1)
    fourteen_start = fourteen_end - timedelta(days=13)
    fourteen_range = [d.date() for d in pd.date_range(start=fourteen_start, end=fourteen_end)]
    no_work_14 = all(day not in selected_dates for day in fourteen_range)

    st.markdown("---")

    st.markdown("### ✅ 조건 결과")
    st.write(
        f"{'✅' if condition1 else '❌'} **조건 1:** "
        f"{'수급자격 인정신청일의 직전 달 초일부터 신청일까지의 근무일 수가 총 일수의 1/3 미만입니다.' if condition1 else '근무일 수가 총 일수의 1/3 이상으로 조건을 충족하지 못했습니다.'}"
    )

    st.write(
        f"{'✅' if no_work_14 else '❌'} **조건 2:** "
        f"{'신청일 직전 14일간(' + fourteen_start.strftime('%Y-%m-%d') + ' ~ ' + fourteen_end.strftime('%Y-%m-%d') + ') 근무내역이 없습니다.' if no_work_14 else '신청일 직전 14일간(' + fourteen_start.strftime('%Y-%m-%d') + ' ~ ' + fourteen_end.strftime('%Y-%m-%d') + ') 근무내역이 존재합니다.'}"
    )

    if not no_work_14:
        last_work = max((d for d in selected_dates if d < apply_date), default=None)
        if last_work:
            suggestion = last_work + timedelta(days=15)
            st.markdown(f"✅ **조건 2 충족 예상 신청일:** {suggestion.strftime('%Y-%m-%d')} 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.markdown("조건 2는 이미 충족 상태입니다.")

    st.markdown("---")

    st.subheader("📌 최종 판단")
    if condition1:
        st.write(
            f"✅ **일반일용근로자:** 신청 가능. "
            f"수급자격 인정신청일({apply_date})이 속한 달의 직전 달 초일부터 신청일까지({start_date} ~ {apply_date}) 근로일 수가 총 일수의 1/3 미만입니다."
        )
    else:
        st.write(
            f"❌ **일반일용근로자:** 신청 불가능. "
            f"근로일 수가 총 일수의 1/3 이상으로 조건을 충족하지 못합니다."
        )

    if condition1 and no_work_14:
        st.write(
            f"✅ **건설일용근로자:** 신청 가능. "
            f"근로일 수가 총 일수의 1/3 미만이고 신청일 직전 14일간 근무내역이 없습니다."
        )
    else:
        st.write(
            f"❌ **건설일용근로자:** 신청 불가능. "
            f"{'근로일 수가 기준 이상입니다.' if not condition1 else ''} "
            f"{'신청일 직전 14일간 근무내역이 있습니다.' if not no_work_14 else ''}"
        )


if __name__ == "__main__":
    daily_worker_eligibility_app()

