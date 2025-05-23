import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar


def get_date_range(base_date):
    """Return the date range from 1st of previous month to the given date."""
    first_day_prev_month = (base_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    return pd.date_range(start=first_day_prev_month, end=base_date)


def main():
    st.title("일용근로자 수급자격 요건 모의계산")

    st.markdown("""
    수급자격 인정신청일 기준으로 직전 달 초일부터 신청일까지의 총 일수 중 근무일이 3분의 1 미만이거나,
    신청일 이전 14일간 연속 근무내역이 없는 경우 요건 충족.
    """)

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.today())

    date_range = get_date_range(apply_date)
    date_labels = [date.strftime('%Y-%m-%d') for date in date_range]

    st.markdown("근무일자를 아래에서 선택하세요:")
    selected_days = st.multiselect("근무일자 선택", options=date_labels)

    total_days = len(date_range)
    worked_days = len(selected_days)
    threshold = total_days / 3

    st.markdown(f"총 기간 일수: **{total_days}일**")
    st.markdown(f"선택한 근무일 수: **{worked_days}일**")
    st.markdown(f"기준 (총일수의 1/3): **{threshold:.2f}일**")

    if worked_days < threshold:
        st.success("✅ 근무일 수가 기준 미만입니다. 요건을 충족할 수 있습니다.")
    else:
        st.warning("❌ 근무일 수가 기준 이상입니다. 요건을 충족하지 않을 수 있습니다.")

    # 연속 미근무 14일 여부 체크
    date_set = set(pd.to_datetime(selected_days))
    fourteen_day_window = [apply_date - timedelta(days=i) for i in range(1, 15)]
    non_worked_14 = all(day not in date_set for day in fourteen_day_window)

    if non_worked_14:
        st.success("✅ 신청일 이전 14일간 연속 미근무 요건을 충족합니다.")
    else:
        st.warning("❌ 신청일 이전 14일간 연속 미근무 요건을 충족하지 않습니다.")


if __name__ == "__main__":
    main()
