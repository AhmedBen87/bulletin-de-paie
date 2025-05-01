from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.profiles import bp
from app.profiles.forms import ProfileForm
from app.models import UserProfile, CalculationHistory

@bp.route('/')
@login_required
def index():
    """List all user profiles."""
    profiles = UserProfile.query.filter_by(user_id=current_user.id).all()
    return render_template('profiles/index.html', title='Mes Profils', profiles=profiles)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create a new profile."""
    form = ProfileForm()
    if form.validate_on_submit():
        profile = UserProfile(
            name=form.name.data,
            hourly_rate=form.hourly_rate.data,
            function_bonus_base_amount=form.function_bonus_base_amount.data,
            performance_bonus_amount=form.performance_bonus_amount.data,
            prime_de_niveau_amount=form.prime_de_niveau_amount.data,
            seniority_rate_percent=form.seniority_rate_percent.data,
            user_id=current_user.id
        )
        db.session.add(profile)
        db.session.commit()
        flash(f"Profil '{profile.name}' créé avec succès!", 'success')
        return redirect(url_for('profiles.index'))
    
    return render_template('profiles/form.html', title='Nouveau Profil', form=form, profile=None)

@bp.route('/edit/<int:profile_id>', methods=['GET', 'POST'])
@login_required
def edit(profile_id):
    """Edit an existing profile."""
    profile = UserProfile.query.get_or_404(profile_id)
    
    # Security check: ensure the profile belongs to the current user
    if profile.user_id != current_user.id:
        abort(403)
    
    form = ProfileForm(obj=profile)
    if form.validate_on_submit():
        form.populate_obj(profile)
        db.session.commit()
        flash("Profil mis à jour avec succès!", 'success')
        return redirect(url_for('profiles.index'))
    
    return render_template('profiles/form.html', title=f'Modifier {profile.name}', form=form, profile=profile)

@bp.route('/delete/<int:profile_id>', methods=['POST'])
@login_required
def delete(profile_id):
    """Delete a profile and its related calculation history."""
    profile = UserProfile.query.get_or_404(profile_id)
    
    # Security check: ensure the profile belongs to the current user
    if profile.user_id != current_user.id:
        abort(403)
    
    profile_name = profile.name
    db.session.delete(profile)  # Cascade will delete related calculations
    db.session.commit()
    
    flash(f"Profil '{profile_name}' supprimé avec succès!", 'success')
    return redirect(url_for('profiles.index'))

@bp.route('/view/<int:profile_id>')
@login_required
def view(profile_id):
    """View a profile's details and calculation history."""
    profile = UserProfile.query.get_or_404(profile_id)
    
    # Security check: ensure the profile belongs to the current user
    if profile.user_id != current_user.id:
        abort(403)
    
    # Get the profile's recent calculations
    recent_calculations = CalculationHistory.query.filter_by(profile_id=profile.id).order_by(
        CalculationHistory.calculation_date.desc()).limit(5).all()
    
    return render_template('profiles/view.html', 
                          title=f'Profil: {profile.name}', 
                          profile=profile,
                          recent_calculations=recent_calculations) 