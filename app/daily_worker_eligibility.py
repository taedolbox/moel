import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import pytz
import time

# 📌 달력 시작 요일 설정
calendar.setfirstweekday(calendar.SUNDAY)

# 📌 KST 시간대
KST = pytz.timezone('Asia/Seoul')

# 📌 CSS 로드 (캐시 방지 쿼리)
timestamp = time.time()
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def get_date_range(apply_date):
    """신청일 기준 직전 달 초일부터 신청일까지 범위"""
    start_of_apply_month = apply_date.replace(day=1)
    start_date = (start_of_apply_month - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date


def render_calendar(apply_date):
    """달력 렌더링 + 날짜 선택"""
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

        # 요일 헤더
        day_headers = ["일", "월", "화", "수", "목", "금", "토"]
        cols = st.columns(7)
        for i, day_name in enumerate(day_headers):
            with cols[i]:
                st.markdown(f'<div class="day-header">{day_name}</div>', unsafe_allow_html=True)

        # 날짜 블록
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
    st.header("일용근로자 수급자격 요건 모의계산")

    now_kst = datetime.now(KST)
    st.markdown(f"**오늘 날짜와 시간**: {now_kst.strftime('%Y년 %m월 %d일 %A %p %I:%M KST')}", unsafe_allow_html=True)

    st.markdown("""
    ### 📋 요건 조건
    - **조건 1**: 직전 달 초일부터 신청일까지 근무일 수가 총 일수의 1/3 미만
    - **조건 2 (건설일용근로자만)**: 신청일 직전 14일간 근무내역 없음 (신청일 제외)
    """)

    st.markdown("---")

    apply_date = st.date_input("수급자격 신청일 선택", value=now_kst.date(), key="apply_date_input")

    date_range_objects, start_date = get_date_range(apply_date)

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
    condition1_msg = "✅ 조건 1 충족: 근무일 수 기준 미만입니다." if condition1 else "❌ 조건 1 불충족: 기준 이상입니다."
    st.markdown(f"<p>{condition1_msg}</p>", unsafe_allow_html=True)

    fourteen_end = apply_date - timedelta(days=1)
    fourteen_start = fourteen_end - timedelta(days=13)
    fourteen_range = [d.date() for d in pd.date_range(start=fourteen_start, end=fourteen_end)]
    no_work_14 = all(day not in selected_dates for day in fourteen_range)

    condition2_msg = f"✅ 조건 2 충족: 신청일 직전 14일간({fourteen_start} ~ {fourteen_end}) 근무내역 없음." \
        if no_work_14 else \
        f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_start} ~ {fourteen_end}) 근무내역 있음."
    st.markdown(f"<p>{condition2_msg}</p>", unsafe_allow_html=True)

    st.markdown("---")

    if not condition2_msg.startswith("✅"):
        last_work = max((d for d in selected_dates if d < apply_date), default=None)
        if last_work:
            suggestion = last_work + timedelta(days=15)
            st.markdown(f"📅 조건 2 충족 예상 신청일: **{suggestion} 이후**")
        else:
            st.markdown("신청일 직전 14일간 근무내역이 없으므로 따로 조정 필요 없음.")

    st.subheader("📌 최종 판단")

    if condition1:
        st.markdown("✅ **일반일용근로자: 신청 가능**")
    else:
        st.markdown("❌ **일반일용근로자: 신청 불가능**")

    if condition1 and no_work_14:
        st.markdown("✅ **건설일용근로자: 신청 가능**")
    else:
        st.markdown("❌ **건설일용근로자: 신청 불가능**")


if __name__ == "__main__":
    daily_worker_eligibility_app()
