import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date

def get_date_range(apply_date):
    """신청일을 기준으로 이전 달 1일부터 신청일까지 날짜 리스트 반환"""
    start_of_apply_month = apply_date.replace(day=1)
    start_date = (start_of_apply_month - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def daily_worker_eligibility_app():
    st.header("일용근로자 수급자격 요건 모의계산")

    current_datetime = datetime.now()
    st.markdown(f"**오늘 날짜와 시간:** {current_datetime.strftime('%Y년 %m월 %d일 %A %H:%M')}")

    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1:** 수급자격 인정신청일의 직전 달 1일부터 신청일까지 근무일 수가 총 일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당):** 신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    apply_date = st.date_input("수급자격 신청일 선택", value=current_datetime.date())

    date_range, start_date = get_date_range(apply_date)
    date_str_list = [d.strftime("%Y-%m-%d (%a)") for d in date_range]

    st.markdown(f"### 근무일 선택 (직전 달 1일부터 신청일까지 총 {len(date_range)}일)")
    selected_dates_str = st.multiselect("근무한 날짜를 모두 선택하세요.", options=date_str_list)

    # 선택된 날짜를 date 객체로 변환
    selected_dates = set()
    for s in selected_dates_str:
        dt = datetime.strptime(s.split(" ")[0], "%Y-%m-%d").date()
        selected_dates.add(dt)

    total_days = len(date_range)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    condition1 = worked_days < threshold

    # 조건 2 계산 (건설일용근로자)
    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [fourteen_days_prior_start + timedelta(days=i) for i in range(14)]
    no_work_14_days = all(day not in selected_dates for day in fourteen_days_prior_range)
    condition2 = no_work_14_days

    st.markdown("---")
    # 결과 상세 설명 작성
    result_html = f"""
    <div style="line-height:1.6;">
    <p>✅ <b>조건 1 충족 여부:</b> 근무일 수 {worked_days}일은 총 기간 {total_days}일의 1/3({threshold:.1f}일) 미만입니다.<br>
    { '→ 조건 1을 충족하여 일반일용근로자는 신청 가능합니다.' if condition1 else '→ 조건 1을 충족하지 못해 일반일용근로자는 신청할 수 없습니다.'}</p>

    <p>❌ <b>조건 2 충족 여부:</b> 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무 기록이 {"없음" if no_work_14_days else "존재함"}.<br>
    { '→ 조건 2를 충족하여 건설일용근로자는 신청 가능합니다.' if condition2 else '→ 조건 2를 충족하지 못해 건설일용근로자는 신청할 수 없습니다.'}</p>
    """

    # 조건 2 불충족 시 신청 가능 날짜 제안
    if not condition2:
        last_worked = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked:
            suggested_date = last_worked + timedelta(days=15)
            result_html += f"""
            <p>📅 조건 2를 충족하려면, 마지막 근무일인 <b>{last_worked.strftime('%Y-%m-%d')}</b> 이후 14일 + 1일이 지난<br>
            <b>{suggested_date.strftime('%Y-%m-%d')}</b> 이후에 신청해야 합니다.</p>
            """
        else:
            result_html += "<p>📅 최근 14일간 근무 기록이 없으므로 조건 2는 충족된 상태입니다.</p>"

    result_html += f"""
    <hr>
    <p><b>최종 판단</b></p>
    <p>✅ 일반일용근로자: {'신청 가능' if condition1 else '신청 불가'}<br>
    수급자격 인정신청일이 속한 달의 직전 달 1일부터 신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근무일 수 합이 총 일수의 3분의 1 미만이어야 합니다.</p>

    <p>✅ 건설일용근로자: {'신청 가능' if (condition1 and condition2) else '신청 불가'}<br>
    신청일 직전 14일간 근무 사실이 없고, 조건 1도 충족해야 합니다.</p>

    <p style="font-size:0.9em; color:gray;">
    ⓒ 2025 실업급여 도우미는 참고용 도구입니다. 실제 판정은 고용센터 심사 기준을 따릅니다.<br>
    거주지역 고용센터 찾기에서 자세한 정보를 확인하세요.
    </p>
    </div>
    """
    st.markdown(result_html, unsafe_allow_html=True)

if __name__ == "__main__":
    daily_worker_eligibility_app()

