from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
import json
from app import db
from app.history import bp
from app.models import UserProfile, CalculationHistory

@bp.route('/')
@login_required
def index():
    """Show history selection page or all calculations."""
    # Get all profiles
    profiles = UserProfile.query.filter_by(user_id=current_user.id).all()
    
    # Check if profile_id was provided as query parameter
    profile_id = request.args.get('profile_id', type=int)
    
    if profile_id:
        # If profile_id was provided, show calculations for that profile
        return redirect(url_for('history.profile', profile_id=profile_id))
    
    # Get the most recent calculations across all profiles
    calculations = CalculationHistory.query.join(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).order_by(CalculationHistory.calculation_date.desc()).limit(20).all()
    
    return render_template('history/index.html', 
                          title='Historique des Calculs',
                          profiles=profiles,
                          calculations=calculations,
                          selected_profile=None)

@bp.route('/profile/<int:profile_id>')
@login_required
def profile(profile_id):
    """Show calculation history for a specific profile."""
    # Get the profile
    profile = UserProfile.query.get_or_404(profile_id)
    
    # Security check: ensure the profile belongs to the current user
    if profile.user_id != current_user.id:
        abort(403)
    
    # Get all profiles (for the selection dropdown)
    profiles = UserProfile.query.filter_by(user_id=current_user.id).all()
    
    # Get all calculations for this profile
    calculations = CalculationHistory.query.filter_by(profile_id=profile_id).order_by(
        CalculationHistory.calculation_date.desc()).all()
    
    return render_template('history/index.html', 
                          title=f'Historique - {profile.name}',
                          profiles=profiles,
                          calculations=calculations,
                          selected_profile=profile)

@bp.route('/view/<int:calculation_id>')
@login_required
def view(calculation_id):
    """View detailed results of a specific calculation."""
    # Get the calculation
    calculation = CalculationHistory.query.get_or_404(calculation_id)
    profile = calculation.profile
    
    # Security check: ensure the calculation's profile belongs to the current user
    if profile.user_id != current_user.id:
        abort(403)
    
    # Parse the stored JSON data
    inputs = json.loads(calculation.input_data)
    results = json.loads(calculation.result_data)
    
    return render_template('history/view.html', 
                          title=f'Détails Calcul - {profile.name}',
                          calculation=calculation,
                          profile=profile,
                          inputs=inputs,
                          results=results)

@bp.route('/delete/<int:calculation_id>', methods=['POST'])
@login_required
def delete(calculation_id):
    """Delete a specific calculation."""
    # Get the calculation
    calculation = CalculationHistory.query.get_or_404(calculation_id)
    profile = calculation.profile
    
    # Security check: ensure the calculation's profile belongs to the current user
    if profile.user_id != current_user.id:
        abort(403)
    
    # Delete the calculation
    profile_id = profile.id
    calc_date = calculation.calculation_date.strftime('%d/%m/%Y')
    db.session.delete(calculation)
    db.session.commit()
    
    flash(f"Calcul du {calc_date} supprimé avec succès!", "success")
    return redirect(url_for('history.profile', profile_id=profile_id)) 