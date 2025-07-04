# app/eligibility_logic.py

from datetime import datetime, timedelta

def check_conditions(selected_dates, cal_dates, fourteen_days_start, fourteen_days_end):
    """
    조건 판단 결과를 반환한다.
    """
    total_days = len(cal_dates)
    threshold = total_days / 3
    worked_days = len(selected_dates)

    # 날짜 형식 변환
    fourteen_start = datetime.strptime(fourteen_days_start, "%Y-%m-%d")
    fourteen_end = datetime.strptime(fourteen_days_end, "%Y-%m-%d")
    fourteen_range = [d for d in cal_dates if fourteen_start <= d <= fourteen_end]

    fourteen_range_strs = [d.strftime("%m/%d") for d in fourteen_range]
    no_work_14_days = all(d not in selected_dates for d in fourteen_range_strs)

    condition1 = worked_days < threshold
    condition2 = no_work_14_days

    # 조건 텍스트
    cond1_text = f"{'✅' if condition1 else '❌'} 조건1 {'충족' if condition1 else '불충족'}: 근무일 수 {worked_days}일, 기준 {threshold:.1f}일"
    cond2_text = f"{'✅' if condition2 else '❌'} 조건2 {'충족' if condition2 else '불충족'}: 신청일 직전 14일 무근무 여부"

    # 다음 가능일 계산
    next_possible = ""
    if not condition2:
        next_date = fourteen_end + timedelta(days=14)
        next_possible = f"📅 조건2를 충족하려면 오늘 이후 근로 제공이 없을 경우 {next_date.strftime('%Y-%m-%d')} 이후에 신청하면 됩니다."

    # 최종 판단
    general = "✅ 신청 가능" if condition1 else "❌ 신청 불가능"
    construction = "✅ 신청 가능" if (condition1 or condition2) else "❌ 신청 불가능"

    result = f"""
총 기간 일수: {total_days}일  
근무일 수: {worked_days}일  
1/3 기준: {threshold:.1f}일

{cond1_text}  
{cond2_text}

{next_possible}

📌 최종 판단  
- 일반 일용근로자: {general}  
- 건설 일용근로자: {construction}
"""
    return result
