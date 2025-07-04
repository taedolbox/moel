from datetime import datetime, timedelta

def check_conditions(selected_dates_list, calendar_dates, fourteen_days_start_str, fourteen_days_end_str):
    # 날짜 문자열 -> datetime 변환
    cal_dates = [datetime.strptime(d, "%Y-%m-%d") for d in calendar_dates]
    selected_dates = set()
    for d in selected_dates_list:
        try:
            # 선택된 날짜는 mm/dd 형식이므로 yyyy- 앞부분은 calendar_dates에서 가져옴
            for cd in cal_dates:
                if cd.strftime("%m/%d") == d:
                    selected_dates.add(cd)
                    break
        except:
            pass

    total_days = len(cal_dates)
    threshold = total_days / 3
    worked_days = len(selected_dates)

    fourteen_start = datetime.strptime(fourteen_days_start_str, "%Y-%m-%d")
    fourteen_end = datetime.strptime(fourteen_days_end_str, "%Y-%m-%d")

    fourteen_range = [d for d in cal_dates if fourteen_start <= d <= fourteen_end]
    # 조건2: 14일간 근무없음 => selected_dates에 14일간 날짜가 하나도 없어야 True
    condition2 = all(d not in selected_dates for d in fourteen_range)
    # 조건1: 전체 기간 근무일수 < 1/3
    condition1 = worked_days < threshold

    # 조건2 충족하려면 언제부터 가능한지 계산 (14일 근무 없었을 때)
    next_possible_date = None
    if not condition2:
        last_worked_date = max(d for d in selected_dates if fourteen_start <= d <= fourteen_end)
        next_possible_date = (last_worked_date + timedelta(days=15)).strftime("%Y-%m-%d")

    return {
        "condition1": condition1,
        "condition2": condition2,
        "worked_days": worked_days,
        "total_days": total_days,
        "threshold": threshold,
        "next_possible_date": next_possible_date,
        "calendar_start": cal_dates[0].strftime("%Y-%m-%d"),
        "calendar_end": cal_dates[-1].strftime("%Y-%m-%d"),
        "fourteen_days_start": fourteen_days_start_str,
        "fourteen_days_end": fourteen_days_end_str,
    }
