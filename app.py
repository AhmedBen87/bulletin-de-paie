from flask import Flask, render_template, request
import math

app = Flask(__name__)

# --- Constants (Unchanged from previous version) ---
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
    (30000.00,    0.00,      0.00), (50000.00,    0.10,   3000.00),
    (60000.00,    0.20,   8000.00), (80000.00,    0.30,  14000.00),
    (180000.00,   0.34,  17200.00), (float('inf'),0.38,  24400.00)
]
# ------------------------------

# --- Helper Functions (Unchanged) ---
def calculate_leave_bases(hourly_rate, function_bonus_base):
    try:
        paid_leave_daily_base = ((hourly_rate * STANDARD_MONTHLY_HOURS) + function_bonus_base) * 12 / STANDARD_ANNUAL_WORK_DAYS
    except ZeroDivisionError: paid_leave_daily_base = 0
    exceptional_leave_daily_base = paid_leave_daily_base * 0.65
    return round(paid_leave_daily_base, 2), round(exceptional_leave_daily_base, 2)

def calculate_igr(sni_monthly):
    if sni_monthly <= 0: return 0.0
    sni_annual = sni_monthly * 12
    gross_annual_igr = 0
    for limit, rate, deduction in IGR_BRACKETS:
        if sni_annual <= limit:
            gross_annual_igr = (sni_annual * rate) - deduction
            break
    net_annual_igr = gross_annual_igr
    monthly_igr = max(0, net_annual_igr / 12)
    return monthly_igr
# ------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    error = None
    inputs = {}

    if request.method == 'POST':
        try:
            # --- Get Inputs (Unchanged) ---
            inputs = {
                'hourly_rate': float(request.form.get('hourly_rate', 0)),
                'worked_hours': float(request.form.get('worked_hours', 0)),
                'performance_bonus_amount': float(request.form.get('performance_bonus_amount', 0)),
                'night_hours_worked': float(request.form.get('night_hours_worked', 0)),
                'night_hour_bonus_rate_percent': float(request.form.get('night_hour_bonus_rate_percent', 0)),
                'function_bonus_base_amount': float(request.form.get('function_bonus_base_amount', 0)),
                'seniority_rate_percent': float(request.form.get('seniority_rate_percent', 0)),
                'paid_leave_days': float(request.form.get('paid_leave_days', 0)),
                'exceptional_leave_days': float(request.form.get('exceptional_leave_days', 0)),
                'prime_de_niveau_amount': float(request.form.get('prime_de_niveau_amount', 0)),
            }

            # --- Calculations (Unchanged up to Gross Salary) ---
            hourly_rate = inputs['hourly_rate']
            worked_hours = inputs['worked_hours']
            function_bonus_base = inputs['function_bonus_base_amount']
            night_hours = inputs['night_hours_worked']
            night_rate_percent = inputs['night_hour_bonus_rate_percent']
            perf_bonus = inputs['performance_bonus_amount']
            niveau_amount = inputs['prime_de_niveau_amount']
            seniority_rate = inputs['seniority_rate_percent'] / 100.0
            paid_days = inputs['paid_leave_days']
            excp_days = inputs['exceptional_leave_days']

            paid_leave_daily_base, exceptional_leave_daily_base = calculate_leave_bases(hourly_rate, function_bonus_base)

            base_salary = hourly_rate * worked_hours
            night_bonus = hourly_rate * night_hours * (night_rate_percent / 100.0)
            try: function_bonus = (worked_hours * function_bonus_base) / STANDARD_MONTHLY_HOURS if STANDARD_MONTHLY_HOURS else 0
            except ZeroDivisionError: function_bonus = 0
            paid_leave_amount = paid_leave_daily_base * paid_days
            exceptional_leave_amount = exceptional_leave_daily_base * excp_days
            seniority_base = base_salary + night_bonus + function_bonus + perf_bonus
            seniority_bonus = seniority_base * seniority_rate
            gross_salary = ( base_salary + night_bonus + function_bonus + perf_bonus + paid_leave_amount + exceptional_leave_amount + niveau_amount + seniority_bonus )

            # 3. Calculate Deductions (Separating Social/Pension from IGR)
            # CNSS
            cnss_base = min(gross_salary, CNSS_CEILING_MONTHLY)
            cnss_contribution = cnss_base * CNSS_RATE

            # Detailed Social Contributions
            maladie_maternite = gross_salary * MALADIE_MATERNITE_RATE
            assurance_complementaire = gross_salary * ASSURANCE_COMPLEMENTAIRE_RATE
            deces_contribution = gross_salary * DECES_RATE
            incap_invalid_contribution = gross_salary * INCAP_INVALID_RATE
            deces_accidentel_contribution = gross_salary * DECES_ACCIDENTEL_RATE
            cimr_contribution = gross_salary * CIMR_RATE

            # **Calculate subtotal of Social & Pension Contributions**
            total_social_pension_contributions = (
                cnss_contribution + maladie_maternite + assurance_complementaire +
                deces_contribution + incap_invalid_contribution +
                deces_accidentel_contribution + cimr_contribution
            )

            # Professional Expenses & SNI (Unchanged logic)
            prof_exp_base = gross_salary - total_social_pension_contributions
            prof_exp_deduction = min(prof_exp_base * PROFESSIONAL_EXPENSES_RATE, PROFESSIONAL_EXPENSES_CEILING_MONTHLY)
            prof_exp_deduction = max(0, prof_exp_deduction)
            sni_monthly = gross_salary - total_social_pension_contributions - prof_exp_deduction
            sni_monthly = max(0, sni_monthly)

            # Calculate IGR (Unchanged logic)
            monthly_igr = calculate_igr(sni_monthly)

            # **Calculate Total Deductions (for info if needed, but Net uses separate components)**
            total_deductions = total_social_pension_contributions + monthly_igr

            # 4. Net Salary (Calculated as Gross - Social/Pension - IGR)
            net_salary = gross_salary - total_social_pension_contributions - monthly_igr

            # --- Prepare results for display (Adjusted Structure) ---
            results = {
                "earnings": { # Unchanged
                    "Base Salary": base_salary, "Night Hours Bonus": night_bonus,
                    "Function Bonus": function_bonus, "Performance Bonus": perf_bonus,
                    "Paid Leave Amount": paid_leave_amount, "Exceptional Leave Amount": exceptional_leave_amount,
                    "Prime de Niveau": niveau_amount, "Seniority Bonus": seniority_bonus,
                },
                "gross_salary": gross_salary,
                "social_pension_contributions": { # New structure for these deductions
                    "CNSS Contribution (4.48%)": cnss_contribution,
                    "Maladie Maternité Contrib.": maladie_maternite,
                    "Assurance Complém. Contrib.": assurance_complementaire,
                    "Décès Contribution": deces_contribution,
                    "Incap./Invalid. Contribution": incap_invalid_contribution,
                    "Décès Accidentel Contrib.": deces_accidentel_contribution,
                    "Retraite/CIMR Contrib. (4.5%)": cimr_contribution,
                },
                "total_social_pension_contributions": total_social_pension_contributions, # Pass subtotal
                "igr_calculation_details": { # Group IGR related info
                    "Professional Expenses Deduction (Info)": prof_exp_deduction,
                    "Net Taxable Income (SNI - Monthly)": sni_monthly,
                    "IGR (Income Tax - calc. 0 dependents)": monthly_igr,
                },
                # "total_deductions": total_deductions, # Keep if you want to display it, but less critical now
                "net_salary": net_salary,
            }

        except ValueError: error = "Invalid input. Please ensure all inputs are valid numbers."; results = None
        except Exception as e: error = f"An unexpected error occurred: {e}"; results = None

    return render_template('index.html', results=results, error=error, inputs=inputs)

if __name__ == '__main__':
    app.run(debug=True)