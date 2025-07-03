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
    months_to_render = sorted(set((d.year, d.month) for d in pd.date_range(
        start=(apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1),
        end=apply_date
    )))
    for year, month in months_to_render:
        st.markdown(f"### {year}년 {month}월")
        cal = calendar.monthcalendar(year, month)
        day_headers = ["일", "월", "화", "수", "목", "금", "토"]
        cols = st.columns(7)
        for i, day_name in enumerate(day_headers):
            with cols[i]:
                st.markdown(f"**{day_name}**")
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].write("")
                else:
                    date_obj = date(year, month, day)
                    is_selected = date_obj in selected_dates
                    checkbox_key = f"date_{date_obj}"
                    checked = cols[i].checkbox(f"{day}", value=is_selected, key=checkbox_key)
                    if checked:
                        selected_dates.add(date_obj)
                    else:
                        selected_dates.discard(date_obj)
    if selected_dates:
        st.markdown("✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%m/%d") for d in sorted(selected_dates)]))
    st.session_state.selected_dates = selected_dates
    return selected_dates

def daily_worker_eligibility_app():
    st.header("일용근로자 수급자격 요건 모의계산")
    current_datetime = datetime.now(KST)
    st.markdown(f"오늘 날짜와 시간: {current_datetime.strftime('%Y년 %m월 %d일 %A %p %I:%M KST')}")
    st.markdown("### 📋 요건 조건")
    st.markdown("- 조건 1: 직전 달 초일부터 신청일까지 근무일 수가 총 일수의 1/3 미만이어야 함")
    st.markdown("- 조건 2 (건설일용): 신청일 직전 14일간 근무 사실 없음")

    apply_date = st.date_input("수급자격 신청일 선택", value=current_datetime.date())
    date_range_objects, start_date = get_date_range(apply_date)
    selected_dates = render_calendar(apply_date)

    total_days = len(date_range_objects)
    worked_days = len([d for d in selected_dates if d in date_range_objects])
    threshold = total_days / 3
    condition1 = worked_days < threshold

    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_range = [d.date() for d in pd.date_range(fourteen_days_prior_start, fourteen_days_prior_end)]
    condition2 = all(d not in selected_dates for d in fourteen_days_range)

    st.markdown("---")
    st.markdown(f"총 기간 일수: {total_days}일")
    st.markdown(f"기준 (총일수의 1/3): {threshold:.1f}일")
    st.markdown(f"선택한 근무일 수: {worked_days}일")
    st.markdown("---")

    ## ✅ 결과 출력 : 요청하신 포맷 그대로 ##
    result_text = ""

    # 조건 1
    if condition1:
        result_text += f"✅ 조건 1 충족: 근무일 수가 기준 미만입니다.\n\n"
    else:
        result_text += f"❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.\n\n"

    # 조건 2
    if condition2:
        result_text += f"✅ 조건 2 충족: 신청일 직전 14일간({fourteen_days_prior_start} ~ {fourteen_days_prior_end}) 근무내역이 없습니다.\n\n"
    else:
        result_text += f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_days_prior_start} ~ {fourteen_days_prior_end}) 내 근무기록이 존재합니다.\n\n"
        # 조건 2 불충족이면 제안일 출력
        last_worked_day = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            result_text += f"📅 조건 2를 충족하려면 언제 신청해야 할까요?\n"
            result_text += f"✅ {suggested_date} 이후에 신청하면 조건 2를 충족할 수 있습니다.\n\n"

    # 최종 판단
    result_text += "📌 최종 판단\n"

    if condition1:
        result_text += f"✅ 일반일용근로자: 신청 가능\n"
        result_text += f"수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date} ~ {apply_date}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만\n\n"
    else:
        result_text += f"❌ 일반일용근로자: 신청 불가능\n"
        result_text += f"수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date} ~ {apply_date}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상\n\n"

    if condition1 and condition2:
        result_text += f"✅ 건설일용근로자: 신청 가능\n"
        result_text += f"수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date} ~ {apply_date}) 근로일 수의 합이 총 일수의 3분의 1 미만이고, 신청일 직전 14일간 근무내역이 없습니다.\n\n"
    else:
        result_text += f"❌ 건설일용근로자: 신청 불가능\n"
        if not condition1:
            result_text += f"수급자격 인정신청일이 속한 달의 직전 달 초일부터 신청일까지 근로일 수의 합이 총 일수의 3분의 1 이상입니다.\n"
        if not condition2:
            result_text += f"신청일 직전 14일간({fourteen_days_prior_start} ~ {fourteen_days_prior_end}) 근무내역이 있습니다.\n"

    result_text += "\nⓒ 2025 실업급여 도우미는 도움을 드리기 위한 목적입니다. 실제 가능 여부는 고용센터의 판단을 기준으로 합니다.\n\n거주지역 고용센터 찾기에서 자세한 정보를 확인하세요."

    st.markdown(result_text)

if __name__ == "__main__":
    daily_worker_eligibility_app()

