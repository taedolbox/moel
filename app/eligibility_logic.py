# app/eligibility_logic.py
from datetime import datetime, timedelta, date

def check_conditions(selected_dates, cal_dates, fourteen_days_start, fourteen_days_end):
    """
    selected_dates: ['07/01', '07/02', ...] 선택된 날짜 문자열 리스트 (MM/DD)
    cal_dates: datetime.date 객체 리스트 (전체 기간 날짜 리스트)
    fourteen_days_start, fourteen_days_end: "YYYY-MM-DD" 문자열, 조건 2 판정 기간

    반환값:
    {
        'condition1': True/False,
        'condition2': True/False,
        'next_possible_date': datetime.date or None,
        'worked_days': int,
        'total_days': int,
        'threshold': float,
        'general_worker_eligible': True/False,
        'construction_worker_eligible': True/False,
    }
    """

    # cal_dates를 datetime.datetime 객체로 변환 (시간 0:00:00)
    cal_dates_dt = [datetime.combine(d, datetime.min.time()) if isinstance(d, date) and not isinstance(d, datetime) else d for d in cal_dates]

    fourteen_start_dt = datetime.strptime(fourteen_days_start, "%Y-%m-%d")
    fourteen_end_dt = datetime.strptime(fourteen_days_end, "%Y-%m-%d")

    # 1. 조건 1: 전체 기간 내 근무일 수가 1/3 미만
    total_days = len(cal_dates_dt)
    threshold = total_days / 3

    # 선택된 날짜는 MM/DD 형태, 이를 "YYYY-MM-DD"로 변환해서 cal_dates와 비교해야 함
    # cal_dates_dt와 같은 연/월 기준으로 변환
    selected_dates_set = set()
    for d in selected_dates:
        for cd in cal_dates_dt:
            # cd 날짜에서 MM/DD 문자열 생성
            if cd.strftime("%m/%d") == d:
                selected_dates_set.add(cd.date())
                break

    worked_days = len(selected_dates_set)

    condition1 = worked_days < threshold

    # 2. 조건 2 (건설일용근로자만) : 신청일 직전 14일간 무근무
    # 기간 내 cal_dates 필터링
    fourteen_range = [d for d in cal_dates_dt if fourteen_start_dt <= d <= fourteen_end_dt]

    # 기간 내 근무일 (selected_dates_set) 중 조건 2 기간에 해당하는 날짜 찾기
    worked_in_14_days = [d for d in fourteen_range if d.date() in selected_dates_set]

    condition2 = (len(worked_in_14_days) == 0)

    # 조건 2 충족 못 하면, 다음 가능한 신청일 계산 (조건 2 마지막 날짜 + 14일)
    next_possible_date = None
    if not condition2:
        next_possible_date = fourteen_end_dt + timedelta(days=14)
        next_possible_date = next_possible_date.date()

    # 최종 판정
    general_worker_eligible = condition1
    construction_worker_eligible = condition1 or condition2

    return {
        'condition1': condition1,
        'condition2': condition2,
        'next_possible_date': next_possible_date,
        'worked_days': worked_days,
        'total_days': total_days,
        'threshold': threshold,
        'general_worker_eligible': general_worker_eligible,
        'construction_worker_eligible': construction_worker_eligible,
    }

