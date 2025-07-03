import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import pytz

KST = pytz.timezone('Asia/Seoul')

def get_date_range(apply_date):
    start_of_apply_month = apply_date.replace(day=1)
    start_date = (start_of_apply_month - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def daily_worker_eligibility_app():
    st.header("일용근로자 수급자격 요건 모의계산")

    current_datetime = datetime.now(KST)
    st.markdown(f"**오늘:** {current_datetime.strftime('%Y-%m-%d %A %H:%M')}")

    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 신청일이 속한 달의 직전 달 1일부터 신청일까지 근무일 수가 총 일수의 1/3 미만")
    st.markdown("- **조건 2 (건설일용)**: 신청일 직전 14일간 근무 사실이 없어야 함 (신청일 제외)")

    apply_date = st.date_input("신청일을 선택하세요", value=current_datetime.date())
    date_range, start_date = get_date_range(apply_date)

    st.markdown("### 근무일 선택 (콤보박스)")
    date_options = [d.strftime("%Y-%m-%d (%a)") for d in date_range]
    selected_strs = st.multiselect("근무한 날짜 선택", date_options)
    selected_dates = set(datetime.strptime(s.split()[0], "%Y-%m-%d").date() for s in selected_strs)

    total_days = len(date_range)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    cond1 = worked_days < threshold

    fourteen_end = apply_date - timedelta(days=1)
    fourteen_start = fourteen_end - timedelta(days=13)

    # ✅ 타입 불일치 방지: date()로 맞춤
    worked_in_14 = any(
        d in selected_dates for d in [dt.date() for dt in pd.date_range(fourteen_start, fourteen_end)]
    )
    cond2 = not worked_in_14

    st.markdown("---")
    st.markdown("### ✅ 조건별 판정")

    st.markdown(
        f"{'✅ 조건 1 충족: 근무일 수가 기준 미만입니다.' if cond1 else '❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.'} "
        f"(총 {worked_days}일 / 기간 {total_days}일, 기준 {threshold:.1f}일)"
    )

    st.markdown(
        f"{'✅ 조건 2 충족: 신청일 직전 14일간 근무 기록이 없습니다.' if cond2 else '❌ 조건 2 불충족: 신청일 직전 14일간'
         f'({fourteen_start} ~ {fourteen_end}) 내 근무기록이 존재합니다.'}"
    )

    if not cond2:
        # 조건 2 불충족 시, 대안 제시
        last_worked = max(
            (d for d in selected_dates if d < apply_date), default=None
        )
        if last_worked:
            suggested = last_worked + timedelta(days=15)
            st.markdown(
                f"📅 조건 2를 충족하려면 언제 신청해야 할까요?\n"
                f"✅ {suggested} 이후에 신청하면 조건 2를 충족할 수 있습니다."
            )

    st.markdown("---")
    st.markdown("### 📌 최종 판단")

    if cond1:
        st.markdown(
            f"✅ 일반일용근로자: 신청 가능\n"
            f"수급자격 인정신청일이 속한 달의 직전 달 초일부터 신청일까지({start_date} ~ {apply_date}) "
            f"근무일 수의 합이 같은 기간 총 일수의 1/3 미만으로 신청 가능합니다."
        )
    else:
        st.markdown(
            f"❌ 일반일용근로자: 신청 불가\n"
            f"근무일 수가 총 일수의 1/3 이상으로 신청이 어렵습니다."
        )

    if cond1 or cond2:
        if cond1 and cond2:
            reason = f"조건 1과 조건 2 모두 충족하여 신청 가능합니다."
        elif cond1:
            reason = f"신청일 직전 14일간({fourteen_start} ~ {fourteen_end}) 근무기록은 있으나 조건 1을 충족하여 신청 가능합니다."
        else:
            reason = f"조건 1은 불충족하였으나 조건 2를 충족하여 신청 가능합니다."
        st.markdown(
            f"✅ 건설일용근로자: 신청 가능\n{reason}"
        )
    else:
        st.markdown(
            f"❌ 건설일용근로자: 신청 불가\n"
            f"조건 1과 조건 2 모두 충족하지 않아 신청이 어렵습니다."
        )

if __name__ == "__main__":
    daily_worker_eligibility_app()
