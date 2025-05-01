import json
import math
from datetime import datetime

# --- Constants for Salary Calculations ---
CNSS_RATE = 0.0448
CNSS_CEILING_MONTHLY = 6000.00
MALADIE_MATERNITE_RATE = 0.027025
ASSURANCE_COMPLEMENTAIRE_RATE = 0.002280
DECES_RATE = 0.002750
INCAP_INVALID_RATE = 0.003135
DECES_ACCIDENTEL_RATE = 0.000570
CIMR_RATE = 0.0450
PROFESSIONAL_EXPENSES_RATE = 0.20
PROFESSIONAL_EXPENSES_CEILING_MONTHLY = 2500.00
STANDARD_MONTHLY_HOURS = 191.0
STANDARD_ANNUAL_WORK_DAYS = 288.0
IGR_BRACKETS = [
    (30000.00,    0.00,      0.00), 
    (50000.00,    0.10,   3000.00),
    (60000.00,    0.20,   8000.00), 
    (80000.00,    0.30,  14000.00),
    (180000.00,   0.34,  17200.00), 
    (float('inf'),0.38,  24400.00)
]

# --- Utility Functions ---
def parse_json(value):
    """Parse JSON string into Python dictionary."""
    if value is None:
        return {}
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return {}

def calculate_leave_bases(hourly_rate, function_bonus_base):
    """Calculate daily bases for paid and exceptional leaves."""
    try:
        paid_leave_daily_base = ((hourly_rate * STANDARD_MONTHLY_HOURS) + function_bonus_base) * 12 / STANDARD_ANNUAL_WORK_DAYS
    except ZeroDivisionError: 
        paid_leave_daily_base = 0
    exceptional_leave_daily_base = paid_leave_daily_base * 0.65
    return round(paid_leave_daily_base, 2), round(exceptional_leave_daily_base, 2)

def calculate_igr(sni_monthly):
    """Calculate Income Tax (IGR) based on net taxable income (SNI)."""
    if sni_monthly <= 0: 
        return 0.0
    sni_annual = sni_monthly * 12
    gross_annual_igr = 0
    for limit, rate, deduction in IGR_BRACKETS:
        if sni_annual <= limit:
            gross_annual_igr = (sni_annual * rate) - deduction
            break
    net_annual_igr = gross_annual_igr
    monthly_igr = max(0, net_annual_igr / 12)
    return monthly_igr

def calculate_salary(inputs):
    """Main salary calculation function."""
    try:
        # --- Extract Inputs ---
        hourly_rate = inputs['hourly_rate']
        worked_hours = inputs['worked_hours']
        function_bonus_base = inputs['function_bonus_base_amount']
        night_hours = inputs['night_hours_worked']
        # Using fixed 20% night hour bonus rate
        night_rate_percent = 20.0
        # Extra hours
        extra_hours_125 = inputs['extra_hours_125']
        extra_hours_150 = inputs['extra_hours_150']
        extra_hours_200 = inputs['extra_hours_200']
        perf_bonus = inputs['performance_bonus_amount']
        niveau_amount = inputs['prime_de_niveau_amount']
        seniority_rate = inputs['seniority_rate_percent'] / 100.0
        paid_days = inputs['paid_leave_days']
        excp_days = inputs['exceptional_leave_days']

        # --- Calculate Leave Bases ---
        paid_leave_daily_base, exceptional_leave_daily_base = calculate_leave_bases(hourly_rate, function_bonus_base)

        # --- Calculate Salary Components ---
        base_salary = hourly_rate * worked_hours
        night_bonus = hourly_rate * night_hours * (night_rate_percent / 100.0)
        
        # Calculate extra hours bonuses
        extra_hours_125_bonus = hourly_rate * extra_hours_125 * 1.25
        extra_hours_150_bonus = hourly_rate * extra_hours_150 * 1.50
        extra_hours_200_bonus = hourly_rate * extra_hours_200 * 2.00

        # Calculate function bonus proportional to worked hours
        try:
            function_bonus = (worked_hours * function_bonus_base) / STANDARD_MONTHLY_HOURS if STANDARD_MONTHLY_HOURS else 0
        except ZeroDivisionError:
            function_bonus = 0

        # Calculate leave amounts
        paid_leave_amount = paid_leave_daily_base * paid_days
        exceptional_leave_amount = exceptional_leave_daily_base * excp_days

        # Calculate seniority bonus
        seniority_base = base_salary + night_bonus + function_bonus + perf_bonus + extra_hours_125_bonus + extra_hours_150_bonus + extra_hours_200_bonus
        seniority_bonus = seniority_base * seniority_rate

        # Calculate gross salary
        gross_salary = (base_salary + night_bonus + extra_hours_125_bonus + extra_hours_150_bonus + extra_hours_200_bonus +
                        function_bonus + perf_bonus + paid_leave_amount + exceptional_leave_amount + niveau_amount + seniority_bonus)

        # --- Calculate Deductions ---
        # CNSS (with ceiling)
        cnss_base = min(gross_salary, CNSS_CEILING_MONTHLY)
        cnss_contribution = cnss_base * CNSS_RATE

        # Detailed Social Contributions
        maladie_maternite = gross_salary * MALADIE_MATERNITE_RATE
        assurance_complementaire = gross_salary * ASSURANCE_COMPLEMENTAIRE_RATE
        deces_contribution = gross_salary * DECES_RATE
        incap_invalid_contribution = gross_salary * INCAP_INVALID_RATE
        deces_accidentel_contribution = gross_salary * DECES_ACCIDENTEL_RATE
        cimr_contribution = gross_salary * CIMR_RATE

        # Calculate total social & pension contributions
        total_social_pension_contributions = (
            cnss_contribution + maladie_maternite + assurance_complementaire +
            deces_contribution + incap_invalid_contribution +
            deces_accidentel_contribution + cimr_contribution
        )

        # Professional Expenses & SNI
        prof_exp_base = gross_salary - total_social_pension_contributions
        prof_exp_deduction = min(prof_exp_base * PROFESSIONAL_EXPENSES_RATE, PROFESSIONAL_EXPENSES_CEILING_MONTHLY)
        prof_exp_deduction = max(0, prof_exp_deduction)
        sni_monthly = gross_salary - total_social_pension_contributions - prof_exp_deduction
        sni_monthly = max(0, sni_monthly)

        # Calculate Income Tax (IGR)
        monthly_igr = calculate_igr(sni_monthly)

        # Calculate total deductions
        total_deductions = total_social_pension_contributions + monthly_igr

        # Calculate net salary
        net_salary = gross_salary - total_social_pension_contributions - monthly_igr

        # --- Prepare Results ---
        results = {
            "earnings": {
                "Base Salary": base_salary,
                "Night Hours Bonus": night_bonus,
                "Extra Hours Bonus (125%)": extra_hours_125_bonus,
                "Extra Hours Bonus (150%)": extra_hours_150_bonus,
                "Extra Hours Bonus (200%)": extra_hours_200_bonus,
                "Function Bonus": function_bonus,
                "Performance Bonus": perf_bonus,
                "Paid Leave Amount": paid_leave_amount,
                "Exceptional Leave Amount": exceptional_leave_amount,
                "Prime de Niveau": niveau_amount,
                "Seniority Bonus": seniority_bonus,
            },
            "gross_salary": gross_salary,
            "social_pension_contributions": {
                "CNSS Contribution (4.48%)": cnss_contribution,
                "Maladie Maternité Contrib.": maladie_maternite,
                "Assurance Complém. Contrib.": assurance_complementaire,
                "Décès Contribution": deces_contribution,
                "Incap./Invalid. Contribution": incap_invalid_contribution,
                "Décès Accidentel Contrib.": deces_accidentel_contribution,
                "Retraite/CIMR Contrib. (4.5%)": cimr_contribution,
            },
            "total_social_pension_contributions": total_social_pension_contributions,
            "igr_calculation_details": {
                "Professional Expenses Deduction (Info)": prof_exp_deduction,
                "Net Taxable Income (SNI - Monthly)": sni_monthly,
                "IGR (Income Tax - calc. 0 dependents)": monthly_igr,
            },
            "net_salary": net_salary,
        }

        return results

    except Exception as e:
        # Log the error and return None
        print(f"Error during salary calculation: {e}")
        return None 