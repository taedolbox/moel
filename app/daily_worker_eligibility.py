import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import pytz

# KST 시간대 설정
KST = pytz.timezone('Asia/Seoul')

def get_date_range(apply_date):
    """신청일을 기준으로 이전 달 초일부터 신청일까지 날짜 범위 반환"""
    start_of_apply_month = apply_date.replace(day=1)
    start_date = (start_of_apply_month - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def daily_worker_eligibility_app():
    st.header("일용근로자 수급자격 요건 모의계산")

    current_datetime = datetime.now(KST)
    current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %I:%M KST')
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}")

    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 신청일이 속한 달의 직전 달 1일부터 신청일까지 근무일 수가 총 일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date(), key="apply_date_input")

    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("### 근무일 선택 (콤보박스 다중 선택)")

    # 콤보박스 대신 멀티셀렉트로 대체
    date_str_list = [d.strftime("%Y-%m-%d (%a)") for d in date_range_objects]
    selected_date_strs = st.multiselect("근무한 날짜를 선택하세요", options=date_str_list)

    # 선택 날짜를 date 객체로 변환
    selected_dates = set()
    for s in selected_date_strs:
        dt = datetime.strptime(s.split()[0], "%Y-%m-%d").date()
        selected_dates.add(dt)

    # 조건 1 계산
    total_days = len(date_range_objects)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    # 조건 2 계산 (건설일용근로자)
    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    worked_in_14_days = any(day in selected_dates for day in fourteen_days_prior_range)

    # 조건 충족 여부
    condition1 = worked_days < threshold
    condition2 = not worked_in_14_days

    # 결과 표시
    st.markdown("---")
    st.markdown("### 결과")

    # 조건 1 결과 메시지
    cond1_msg = f"✅ 조건 1 충족 여부: 근무일 수 {worked_days}일은 총 기간 {total_days}일의 1/3({threshold:.1f}일) 미만입니다." if condition1 else \
                f"❌ 조건 1 불충족: 근무일 수 {worked_days}일이 총 기간 {total_days}일의 1/3({threshold:.1f}일) 이상입니다."
    st.markdown(cond1_msg)

    # 조건 2 결과 메시지
    cond2_msg = f"✅ 조건 2 충족 여부: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무 기록이 없습니다." if condition2 else \
                f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무 기록이 있습니다."
    st.markdown(cond2_msg)

    st.markdown("### 최종 판단")

    # 일반일용근로자 판단
    if condition1:
        st.markdown(
            f"✅ 일반일용근로자: 신청 가능\n"
            f"수급자격 인정신청일이 속한 달의 직전 달 1일부터 신청일까지({start_date} ~ {apply_date}) 근무일 수의 합이 총 일수의 3분의 1 미만입니다."
        )
    else:
        st.markdown(
            f"❌ 일반일용근로자: 신청 불가\n"
            f"수급자격 인정신청일이 속한 달의 직전 달 1일부터 신청일까지({start_date} ~ {apply_date}) 근무일 수의 합이 총 일수의 3분의 1 이상입니다."
        )

    # 건설일용근로자 판단 (조건1과 조건2 모두 충족해야 신청 가능)
    if condition1 and condition2:
        st.markdown(
            f"✅ 건설일용근로자: 신청 가능\n"
            f"수급자격 인정신청일이 속한 달의 직전 달 1일부터 신청일까지({start_date} ~ {apply_date}) 근무일 수가 총 일수의 3분의 1 미만이며,\n"
            f"신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무 기록이 없습니다."
        )
    elif condition1 and not condition2:
        st.markdown(
            f"❌ 건설일용근로자: 신청 불가\n"
            f"조건 1은 충족하였으나, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무 기록이 있어 조건 2를 충족하지 못했습니다."
        )
    else:
        st.markdown(
            f"❌ 건설일용근로자: 신청 불가\n"
            f"수급자격 인정신청일이 속한 달의 직전 달 1일부터 신청일까지 근무일 수가 총 일수의 3분의 1 이상이거나,\n"
            f"신청일 직전 14일간 근무 기록이 있습니다."
        )

if __name__ == "__main__":
    daily_worker_eligibility_app()


