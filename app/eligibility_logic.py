# app/eligibility_logic.py

def check_conditions(total_days, worked_days, fourteen_days_worked):
    threshold = total_days / 3

    # 조건1: 근무일수 총일의 1/3 미만
    condition1 = worked_days < threshold

    # 조건2: 직전 14일간 무근무
    condition2 = fourteen_days_worked == 0

    # 일반 일용근로자 판단: 조건1 충족시 가능
    general = condition1

    # 건설일용근로자 판단: 조건1 또는 조건2 둘 중 하나라도 충족하면 가능
    construction = condition1 or condition2

    return {
        "threshold": threshold,
        "condition1": condition1,
        "condition2": condition2,
        "general": general,
        "construction": construction
    }

