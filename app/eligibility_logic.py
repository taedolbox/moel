from datetime import datetime, timedelta

def check_conditions(selected_dates, calendar_dates, input_date):
    """
    - selected_dates: ['MM/DD', ...] 형식의 근무일 리스트
    - calendar_dates: ['YYYY-MM-DD', ...] 직전 달 1일부터 신청일까지 날짜 리스트
    - input_date: datetime.date, 신청일 기준일

    반환값: dict 형식의 판단 결과
    """
    total_days = len(calendar_dates)
    threshold = total_days / 3
    worked_days = len(selected_dates)

    # 14일 전 기간
    fourteen_days_start = (input_date - timedelta(days=14)).strftime("%Y-%m-%d")
    fourteen_days_end = (input_date - timedelta(days=1)).strftime("%Y-%m-%d")

    # 신청일 제외 직전 14일 기간 날짜 리스트
    fourteen_days_range = [d for d in calendar_dates if fourteen_days_start <= d <= fourteen_days_end]

    # 날짜 형식 변환 함수 (YYYY-MM-DD → M/D)
    def format_md(date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{dt.month}/{dt.day}"

    no_work_14_days = all(format_md(d) not in selected_dates for d in fourteen_days_range)

    # 조건1 충족 여부
    cond1 = worked_days < threshold

    # 다음 조건2 충족 가능한 날짜
    next_possible_date = (input_date - timedelta(days=1)) + timedelta(days=1)
    if not no_work_14_days:
        next_possible_date = datetime.strptime(fourteen_days_end, "%Y-%m-%d") + timedelta(days=1)

    results = {
        "total_days": total_days,
        "threshold": threshold,
        "worked_days": worked_days,
        "cond1": cond1,
        "no_work_14_days": no_work_14_days,
        "fourteen_days_start": fourteen_days_start,
        "fourteen_days_end": fourteen_days_end,
        "next_possible_date": next_possible_date.strftime("%Y-%m-%d"),
    }
    return results
