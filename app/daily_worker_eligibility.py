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

        # ✅ 조건 1 출력
    st.markdown(
        f"✅ 조건 1 {'충족: 근무일 수가 기준 미만입니다.' if condition1 else '불충족: 근무일 수가 기준 이상입니다.'}"
    )

    # ✅ 조건 2 출력
    st.markdown(
        f"{'✅ 조건 2 충족: 신청일 직전 14일간(' + fourteen_days_prior_start.strftime('%Y-%m-%d') + ' ~ ' + fourteen_days_prior_end.strftime('%Y-%m-%d') + ') 근무내역이 없습니다.' if condition2 else '❌ 조건 2 불충족: 신청일 직전 14일간(' + fourteen_days_prior_start.strftime('%Y-%m-%d') + ' ~ ' + fourteen_days_prior_end.strftime('%Y-%m-%d') + ') 내 근무기록이 존재합니다.'}"
    )

    # ✅ 조건 2 불충족 시 대안
    if not condition2:
        last_worked_day = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.markdown(
                f"📅 조건 2를 충족하려면 언제 신청해야 할까요?\n"
                f"✅ {suggested_date.strftime('%Y-%m-%d')} 이후에 신청하면 조건 2를 충족할 수 있습니다."
            )

    st.markdown("📌 최종 판단")

    if condition1:
        st.markdown(
            f"✅ 일반일용근로자: 신청 가능  \n"
            f"수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만"
        )
    else:
        st.markdown(
            f"❌ 일반일용근로자: 신청 불가능  \n"
            f"수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상"
        )

    if condition1 and condition2:
        st.markdown(
            f"✅ 건설일용근로자: 신청 가능  \n"
            f"수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 총 일수의 3분의 1 미만이고, 신청일 직전 14일간 근무내역이 없습니다."
        )
    else:
        if not condition2:
            st.markdown(
                f"❌ 건설일용근로자: 신청 불가능  \n"
                f"신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 있습니다."
            )
        elif not condition1:
            st.markdown(
                f"❌ 건설일용근로자: 신청 불가능  \n"
                f"수급자격 인정신청일이 속한 달의 직전 달 초일부터 신청일까지 근로일 수의 합이 총 일수의 3분의 1 이상입니다."
            )

    st.markdown("ⓒ 2025 실업급여 도우미는 도움을 드리기 위한 목적입니다. 실제 가능 여부는 고용센터의 판단을 기준으로 합니다.\n\n거주지역 고용센터 찾기에서 자세한 정보를 확인하세요.")


if __name__ == "__main__":
    daily_worker_eligibility_app()


