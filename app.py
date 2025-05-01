from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import math
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_for_dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salary_calculator_new.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Custom Jinja filter for parsing JSON
@app.template_filter('fromjson')
def parse_json(value):
    return json.loads(value)

# --- Database Models ---
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    function_bonus_base_amount = db.Column(db.Float, default=0)
    performance_bonus_amount = db.Column(db.Float, default=0)
    prime_de_niveau_amount = db.Column(db.Float, default=0)
    seniority_rate_percent = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    calculations = db.relationship('CalculationHistory', backref='profile', lazy=True)

class CalculationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)
    calculation_date = db.Column(db.DateTime, default=datetime.utcnow)
    input_data = db.Column(db.Text)  # JSON string of inputs
    result_data = db.Column(db.Text)  # JSON string of results
    gross_salary = db.Column(db.Float)
    net_salary = db.Column(db.Float)

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

# --- Salary Calculation Function ---
def calculate_salary(inputs):
    try:
        # --- Calculations ---
            hourly_rate = inputs['hourly_rate']
            worked_hours = inputs['worked_hours']
            function_bonus_base = inputs['function_bonus_base_amount']
            night_hours = inputs['night_hours_worked']
        # Using fixed 20% night hour bonus rate instead of user input
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

            paid_leave_daily_base, exceptional_leave_daily_base = calculate_leave_bases(hourly_rate, function_bonus_base)

            base_salary = hourly_rate * worked_hours
            night_bonus = hourly_rate * night_hours * (night_rate_percent / 100.0)
        # Calculate extra hours bonuses
        extra_hours_125_bonus = hourly_rate * extra_hours_125 * 1.25
        extra_hours_150_bonus = hourly_rate * extra_hours_150 * 1.50
        extra_hours_200_bonus = hourly_rate * extra_hours_200 * 2.00

        try:
            function_bonus = (worked_hours * function_bonus_base) / STANDARD_MONTHLY_HOURS if STANDARD_MONTHLY_HOURS else 0
        except ZeroDivisionError:
            function_bonus = 0

            paid_leave_amount = paid_leave_daily_base * paid_days
            exceptional_leave_amount = exceptional_leave_daily_base * excp_days

        # Note: Adjusted seniority_base calculation to happen *after* function_bonus is determined
        seniority_base = base_salary + night_bonus + function_bonus + perf_bonus + extra_hours_125_bonus + extra_hours_150_bonus + extra_hours_200_bonus
            seniority_bonus = seniority_base * seniority_rate

        gross_salary = (base_salary + night_bonus + extra_hours_125_bonus + extra_hours_150_bonus + extra_hours_200_bonus + 
                        function_bonus + perf_bonus + paid_leave_amount + exceptional_leave_amount + niveau_amount + seniority_bonus)

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
        # It's good practice to log the error
        app.logger.error(f"Error during salary calculation: {e}", exc_info=True)
        return None

# --- Routes ---
@app.route('/')
def index():
    profiles = UserProfile.query.all()
    return render_template('profile_select.html', profiles=profiles)

@app.route('/profile/new', methods=['GET', 'POST'])
def new_profile():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '')
            hourly_rate = float(request.form.get('hourly_rate', 0))
            function_bonus = float(request.form.get('function_bonus_base_amount', 0))
            performance_bonus = float(request.form.get('performance_bonus_amount', 0))
            prime_niveau = float(request.form.get('prime_de_niveau_amount', 0))
            seniority_rate = float(request.form.get('seniority_rate_percent', 0))
            
            # Create new profile
            profile = UserProfile(
                name=name,
                hourly_rate=hourly_rate,
                function_bonus_base_amount=function_bonus,
                performance_bonus_amount=performance_bonus,
                prime_de_niveau_amount=prime_niveau,
                seniority_rate_percent=seniority_rate
            )
            db.session.add(profile)
            db.session.commit()
            
            flash(f"Profile '{name}' created successfully!")
            return redirect(url_for('calculator', profile_id=profile.id))
        except ValueError:
            flash("Invalid input. Please ensure all fields contain valid numbers.")
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
            
    return render_template('profile_form.html', profile=None)

@app.route('/profile/edit/<int:profile_id>', methods=['GET', 'POST'])
def edit_profile(profile_id):
    profile = UserProfile.query.get_or_404(profile_id)
    
    if request.method == 'POST':
        try:
            profile.name = request.form.get('name', '')
            profile.hourly_rate = float(request.form.get('hourly_rate', 0))
            profile.function_bonus_base_amount = float(request.form.get('function_bonus_base_amount', 0))
            profile.performance_bonus_amount = float(request.form.get('performance_bonus_amount', 0))
            profile.prime_de_niveau_amount = float(request.form.get('prime_de_niveau_amount', 0))
            profile.seniority_rate_percent = float(request.form.get('seniority_rate_percent', 0))
            
            db.session.commit()
            flash("Profile updated successfully!")
            return redirect(url_for('calculator', profile_id=profile.id))
        except ValueError:
            flash("Invalid input. Please ensure all fields contain valid numbers.")
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
    
    return render_template('profile_form.html', profile=profile)

@app.route('/profile/delete/<int:profile_id>', methods=['POST'])
def delete_profile(profile_id):
    profile = UserProfile.query.get_or_404(profile_id)
    db.session.delete(profile)
    db.session.commit()
    flash(f"Profile '{profile.name}' deleted successfully!")
    return redirect(url_for('index'))

@app.route('/calculator/<int:profile_id>', methods=['GET', 'POST'])
def calculator(profile_id):
    profile = UserProfile.query.get_or_404(profile_id)
    results = None
    error = None
    # Get current month in YYYY-MM format for the calendar input
    current_month = datetime.now().strftime('%Y-%m')
    
    inputs = {
        'hourly_rate': profile.hourly_rate,
        'function_bonus_base_amount': profile.function_bonus_base_amount,
        'performance_bonus_amount': profile.performance_bonus_amount,
        'prime_de_niveau_amount': profile.prime_de_niveau_amount,
        'worked_hours': '',
        'night_hours_worked': 0,
        'extra_hours_125': 0,
        'extra_hours_150': 0,
        'extra_hours_200': 0,
        'seniority_rate_percent': profile.seniority_rate_percent,
        'paid_leave_days': 0,
        'exceptional_leave_days': 0,
        'calendar_month': current_month,
        'calendar_data_storage': '{}'
    }

    if request.method == 'POST':
        try:
            # Check input method (regular or calendar)
            input_method = request.form.get('input_method', 'regular')
            
            # --- Get Inputs ---
            inputs = {
                'hourly_rate': profile.hourly_rate,
                'function_bonus_base_amount': profile.function_bonus_base_amount,
                'performance_bonus_amount': profile.performance_bonus_amount,
                'prime_de_niveau_amount': profile.prime_de_niveau_amount,
                'calendar_month': request.form.get('calendar_month', current_month),
                'worked_hours': float(request.form.get('worked_hours', 0)),
                'night_hours_worked': float(request.form.get('night_hours_worked', 0)),
                'extra_hours_125': float(request.form.get('extra_hours_125', 0)),
                'extra_hours_150': float(request.form.get('extra_hours_150', 0)),
                'extra_hours_200': float(request.form.get('extra_hours_200', 0)),
                'seniority_rate_percent': float(request.form.get('seniority_rate_percent', profile.seniority_rate_percent)),
                'paid_leave_days': float(request.form.get('paid_leave_days', 0)),
                'exceptional_leave_days': float(request.form.get('exceptional_leave_days', 0)),
                'calendar_data_storage': request.form.get('calendar_data_storage', '{}')
            }

            results = calculate_salary(inputs)
            
            if results:
                # Save calculation to history
                calc_history = CalculationHistory(
                    profile_id=profile.id,
                    input_data=json.dumps(inputs),
                    result_data=json.dumps(results),
                    gross_salary=results['gross_salary'],
                    net_salary=results['net_salary']
                )
                db.session.add(calc_history)
                db.session.commit()
                
                # Add a success flash message
                flash("Salary calculation completed successfully!")
                
                # Don't redirect, simply render the page with results
                # The tab parameter will be passed in the template context

        except ValueError: 
            error = "Invalid input. Please ensure all inputs are valid numbers."
        except Exception as e: 
            error = f"An unexpected error occurred: {e}"

    # Get the active tab from either POST data or query parameters
    active_tab = request.form.get('tab') or request.args.get('tab', 'regular')

    return render_template('calculator.html', 
                           profile=profile, 
                           results=results, 
                           error=error, 
                           inputs=inputs,
                           current_month=current_month,
                           active_tab=active_tab)

@app.route('/history/<int:profile_id>')
def history(profile_id):
    profile = UserProfile.query.get_or_404(profile_id)
    calculations = CalculationHistory.query.filter_by(profile_id=profile_id).order_by(CalculationHistory.calculation_date.desc()).all()
    return render_template('history.html', profile=profile, calculations=calculations)

@app.route('/history/view/<int:calculation_id>')
def view_calculation(calculation_id):
    calculation = CalculationHistory.query.get_or_404(calculation_id)
    profile = calculation.profile
    inputs = json.loads(calculation.input_data)
    results = json.loads(calculation.result_data)
    return render_template('calculation_view.html', 
                           calculation=calculation, 
                           profile=profile,
                           inputs=inputs, 
                           results=results)

# Initialize database
with app.app_context():
    # Check if the instance folder exists, create if not
    if not os.path.exists(os.path.join(app.instance_path)):
        os.makedirs(os.path.join(app.instance_path))
        app.logger.info(f"Created instance folder at {app.instance_path}")
    db.create_all()
    app.logger.info("Database tables checked/created.")

if __name__ == '__main__':
    app.run(debug=True)