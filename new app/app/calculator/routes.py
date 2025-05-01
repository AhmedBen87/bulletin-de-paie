from flask import render_template, redirect, url_for, flash, request, abort, jsonify, make_response
from flask_login import login_required, current_user
from datetime import datetime
import json
import io
from app import db
from app.calculator import bp
from app.calculator.forms import CalculatorForm
from app.models import UserProfile, CalculationHistory
from app.utils import calculate_salary
from app.pdf_generator import generate_pdf

@bp.route('/')
@login_required
def index():
    """Show calculator selection page."""
    profiles = UserProfile.query.filter_by(user_id=current_user.id).all()
    if not profiles:
        flash("Vous devez d'abord créer un profil avant de pouvoir calculer un salaire.", "info")
        return redirect(url_for('profiles.new'))
    return render_template('calculator/select.html', title='Sélectionner un Profil', profiles=profiles)

@bp.route('/<int:profile_id>', methods=['GET', 'POST'])
@login_required
def calculate(profile_id):
    """Calculator page for specific profile."""
    profile = UserProfile.query.get_or_404(profile_id)
    
    # Security check: ensure the profile belongs to the current user
    if profile.user_id != current_user.id:
        abort(403)
    
    # Get current month in YYYY-MM format for the calendar input
    current_month = datetime.now().strftime('%Y-%m')
    
    # Get recent calculations for this profile
    recent_calculations = CalculationHistory.query.filter_by(profile_id=profile.id).order_by(
        CalculationHistory.calculation_date.desc()).limit(3).all()
    
    form = CalculatorForm()
    
    # Pre-fill form with profile data
    if request.method == 'GET':
        form.hourly_rate.data = profile.hourly_rate
        form.function_bonus_base_amount.data = profile.function_bonus_base_amount
        form.performance_bonus_amount.data = profile.performance_bonus_amount
        form.prime_de_niveau_amount.data = profile.prime_de_niveau_amount
        form.seniority_rate_percent.data = profile.seniority_rate_percent
        form.calendar_month.data = current_month
    
    # Process form submission
    calculation_id = None
    results = None
    
    if form.validate_on_submit():
        try:
            # Prepare inputs for calculation
            inputs = {
                'hourly_rate': profile.hourly_rate,
                'function_bonus_base_amount': profile.function_bonus_base_amount,
                'performance_bonus_amount': profile.performance_bonus_amount,
                'prime_de_niveau_amount': profile.prime_de_niveau_amount,
                'worked_hours': float(form.worked_hours.data),
                'night_hours_worked': float(form.night_hours_worked.data),
                'extra_hours_125': float(form.extra_hours_125.data),
                'extra_hours_150': float(form.extra_hours_150.data),
                'extra_hours_200': float(form.extra_hours_200.data),
                'seniority_rate_percent': float(form.seniority_rate_percent.data),
                'paid_leave_days': float(form.paid_leave_days.data),
                'exceptional_leave_days': float(form.exceptional_leave_days.data),
                'calendar_month': form.calendar_month.data,
                'calendar_data_storage': form.calendar_data_storage.data
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
                
                calculation_id = calc_history.id
                flash("Calcul du salaire effectué avec succès!", "success")
            else:
                flash("Une erreur est survenue lors du calcul.", "error")
                
        except ValueError:
            flash("Données invalides. Veuillez vérifier vos entrées.", "error")
        except Exception as e:
            flash(f"Une erreur inattendue est survenue: {str(e)}", "error")
    
    # Re-fetch recent calculations if a new calculation was added
    if calculation_id:
        recent_calculations = CalculationHistory.query.filter_by(profile_id=profile.id).order_by(
            CalculationHistory.calculation_date.desc()).limit(3).all()
    
    return render_template('calculator/form.html',
                          title=f'Calculateur - {profile.name}',
                          profile=profile,
                          form=form,
                          results=results,
                          inputs=form.data,
                          current_month=current_month,
                          calculation_id=calculation_id,
                          recent_calculations=recent_calculations)

@bp.route('/print/<int:calculation_id>')
@login_required
def print(calculation_id):
    """Print view for a specific calculation."""
    calculation = CalculationHistory.query.get_or_404(calculation_id)
    profile = calculation.profile
    
    # Security check: ensure the calculation's profile belongs to the current user
    if profile.user_id != current_user.id:
        abort(403)
    
    inputs = json.loads(calculation.input_data)
    results = json.loads(calculation.result_data)
    
    return render_template('calculator/print.html',
                          title=f'Impression - {profile.name}',
                          calculation=calculation,
                          profile=profile,
                          inputs=inputs,
                          results=results)

@bp.route('/export-pdf/<int:calculation_id>')
@login_required
def export_pdf(calculation_id):
    """Export calculation as PDF."""
    calculation = CalculationHistory.query.get_or_404(calculation_id)
    profile = calculation.profile
    
    # Security check: ensure the calculation's profile belongs to the current user
    if profile.user_id != current_user.id:
        abort(403)
    
    # Generate PDF using the utility function
    pdf_data = generate_pdf(calculation)
    if not pdf_data:
        flash("Erreur lors de la génération du PDF.", "error")
        return redirect(url_for('calculator.view', calculation_id=calculation_id))
    
    # Create response with PDF attachment
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=bulletin_{profile.name.replace(" ", "_")}_{calculation.calculation_date.strftime("%Y%m%d")}.pdf'
    
    return response 