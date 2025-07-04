def check_conditions(selected_dates, cal_dates, fourteen_start, fourteen_end):
    """
    - selected_dates: YYYY-MM-DD 형식 근무일 리스트
    - cal_dates: YYYY-MM-DD 형식 달력 전체 날짜 리스트
    - fourteen_start: YYYY-MM-DD 형식 14일간 시작일
    - fourteen_end: YYYY-MM-DD 형식 14일간 종료일
    """

    total_days = len(cal_dates)
    threshold = total_days / 3
    worked_days = len(selected_dates)

    # 조건 1: 근무일 수가 총 일수 1/3 미만인가?
    cond1 = worked_days < threshold

    # 조건 2: 신청일 직전 14일간 근무 여부 (없어야 충족)
    fourteen_range = [d for d in cal_dates if fourteen_start <= d <= fourteen_end]
    cond2 = all(day not in selected_dates for day in fourteen_range)

    # 조건 2 충족 여부 및 다음 신청 가능 날짜 안내
    if not cond2:
        # 조건 2를 충족하려면 14일간 무근무 기간 종료 후 신청 가능
        from datetime import datetime, timedelta
        next_possible_date = datetime.strptime(fourteen_end, "%Y-%m-%d") + timedelta(days=14)
        next_possible_str = next_possible_date.strftime("%Y-%m-%d")
        next_msg = f"📅 조건 2를 충족하려면 {next_possible_str} 이후에 신청하면 조건 2를 충족할 수 있습니다."
    else:
        next_msg = ""

    # 결과 메시지 작성 (HTML)
    result_html = f"""
    <p>총 기간 일수: {total_days}일</p>
    <p>1/3 기준: {threshold:.1f}일</p>
    <p>근무일 수: {worked_days}일</p>
    <p>{'✅ 조건 1 충족: 근무일 수가 기준 미만입니다.' if cond1 else '❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.'}</p>
    <p>{'✅ 조건 2 충족: 신청일 직전 14일간 무근무' if cond2 else '❌ 조건 2 불충족: 신청일 직전 14일간 근무 기록이 존재합니다.'}</p>
    <p>{next_msg}</p>

    <h3>📌 최종 판단</h3>
    <p>✅ 일반일용근로자: {'신청 가능' if cond1 else '신청 불가능'}</p>
    <p>✅ 건설일용근로자: {'신청 가능' if (cond1 or cond2) else '신청 불가능'}</p>
    """

    return result_html
