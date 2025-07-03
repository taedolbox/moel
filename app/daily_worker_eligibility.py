import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import pytz

KST = pytz.timezone('Asia/Seoul')

def get_date_range(apply_date):
    """신청일 기준 직전달 초일부터 신청일까지"""
    start_of_apply_month = apply_date.replace(day=1)
    start_date = (start_of_apply_month - pd.DateOffset(months=1)).replace(day=1).date()
    return pd.date_range(start=start_date, end=apply_date).to_list(), start_date

def daily_worker_eligibility_app():
    st.header("📋 일용근로자 수급자격 요건 모의계산")

    now = datetime.now(KST)
    st.markdown(f"**오늘 날짜와 시간**: {now.strftime('%Y년 %m월 %d일 (%A) %p %I:%M KST')}")

    st.markdown("### ✅ 수급자격 조건")
    st.markdown("- **조건 1**: 신청일 직전달 초일부터 신청일까지의 근무일 수가 총일수의 1/3 미만이어야 함")
    st.markdown("- **조건 2 (건설일용)**: 신청일 직전 14일간 근무 사실이 없어야 함 (신청일 제외)")

    # 신청일 선택
    apply_date = st.date_input("📅 수급자격 신청일 선택", value=now.date())

    # 날짜 범위 가져오기
    date_range, start_date = get_date_range(apply_date)

    # 근무일 선택 (콤보박스 멀티셀렉트)
    worked_days = st.multiselect(
        "✅ 근무일을 선택하세요",
        options=date_range,
        format_func=lambda d: d.strftime("%Y-%m-%d")
    )

    total_days = len(date_range)
    worked_count = len(worked_days)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준(1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_count}일**")

    # 조건1 판단
    condition1 = worked_count < threshold
    st.markdown(
        f"<div><strong>{'✅ 조건 1 충족' if condition1 else '❌ 조건 1 불충족'}</strong></div>",
        unsafe_allow_html=True
    )

    # 조건2 판단
    end14 = apply_date - timedelta(days=1)
    start14 = end14 - timedelta(days=13)
    days14 = pd.date_range(start=start14, end=end14).to_list()
    has_work14 = any(d in worked_days for d in days14)
    condition2 = not has_work14

    st.markdown(
        f"<div><strong>{'✅ 조건 2 충족' if condition2 else '❌ 조건 2 불충족'} "
        f"({start14.strftime('%Y-%m-%d')} ~ {end14.strftime('%Y-%m-%d')})</strong></div>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.subheader("📌 최종 판단")
    if condition1:
        st.markdown(f"✅ **일반일용근로자 신청 가능**")
    else:
        st.markdown(f"❌ **일반일용근로자 신청 불가능**")

    if condition1 and condition2:
        st.markdown(f"✅ **건설일용근로자 신청 가능**")
    else:
        msg = "❌ **건설일용근로자 신청 불가능**"
        if not condition1:
            msg += f"<br>- 직전달 초일부터 신청일까지 근무일 수가 기준 이상"
        if not condition2:
            msg += f"<br>- 신청일 직전 14일간 근무내역 있음"
        st.markdown(msg, unsafe_allow_html=True)

if __name__ == "__main__":
    daily_worker_eligibility_app()


