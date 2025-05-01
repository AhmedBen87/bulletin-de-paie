from flask import render_template, redirect, url_for, request, flash
from app.main import bp
from app.models import UserProfile, CalculationHistory
from flask_login import current_user, login_required

@bp.route('/')
def index():
    """Homepage route showing a list of profiles or a welcome page."""
    if current_user.is_authenticated:
        profiles = UserProfile.query.filter_by(user_id=current_user.id).all()
        return render_template('index.html', profiles=profiles)
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with summary of profiles and recent calculations."""
    profiles = UserProfile.query.filter_by(user_id=current_user.id).all()
    
    # Get recent calculations for each profile
    profile_data = []
    for profile in profiles:
        recent_calcs = CalculationHistory.query.filter_by(profile_id=profile.id).order_by(
            CalculationHistory.calculation_date.desc()).limit(3).all()
        profile_data.append({
            'profile': profile,
            'recent_calculations': recent_calcs
        })
    
    # Get overall stats
    total_profiles = len(profiles)
    total_calculations = sum(len(data['recent_calculations']) for data in profile_data)
    
    return render_template('dashboard.html', 
                           profile_data=profile_data,
                           total_profiles=total_profiles,
                           total_calculations=total_calculations) 