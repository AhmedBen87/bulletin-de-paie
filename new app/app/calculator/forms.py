from flask_wtf import FlaskForm
from wtforms import FloatField, HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class CalculatorForm(FlaskForm):
    """Form for salary calculations."""
    # Hidden fields for storing profile data
    hourly_rate = HiddenField('Taux horaire')
    function_bonus_base_amount = HiddenField('Prime de fonction')
    performance_bonus_amount = HiddenField('Prime de performance')
    prime_de_niveau_amount = HiddenField('Prime de niveau')
    
    # Input fields
    worked_hours = FloatField('Heures travaillées', validators=[
        DataRequired(message="Les heures travaillées sont requises."),
        NumberRange(min=0, message="Les heures travaillées doivent être positives.")
    ])
    
    night_hours_worked = FloatField('Heures de nuit', validators=[
        Optional(),
        NumberRange(min=0, message="Les heures de nuit doivent être positives.")
    ], default=0)
    
    extra_hours_125 = FloatField('Heures supplémentaires (125%)', validators=[
        Optional(),
        NumberRange(min=0, message="Les heures supplémentaires doivent être positives.")
    ], default=0)
    
    extra_hours_150 = FloatField('Heures supplémentaires (150%)', validators=[
        Optional(),
        NumberRange(min=0, message="Les heures supplémentaires doivent être positives.")
    ], default=0)
    
    extra_hours_200 = FloatField('Heures supplémentaires (200%)', validators=[
        Optional(),
        NumberRange(min=0, message="Les heures supplémentaires doivent être positives.")
    ], default=0)
    
    paid_leave_days = FloatField('Jours de congés payés', validators=[
        Optional(),
        NumberRange(min=0, message="Les jours de congés payés doivent être positifs.")
    ], default=0)
    
    exceptional_leave_days = FloatField('Jours de congés exceptionnels', validators=[
        Optional(),
        NumberRange(min=0, message="Les jours de congés exceptionnels doivent être positifs.")
    ], default=0)
    
    seniority_rate_percent = FloatField('Taux d\'ancienneté (%)', validators=[
        Optional(),
        NumberRange(min=0, max=100, message="Le taux d'ancienneté doit être compris entre 0 et 100%.")
    ])
    
    # Hidden fields for tab management and calendar data
    tab = HiddenField('Tab', default='standard')
    calendar_month = HiddenField('Calendar Month')
    calendar_data_storage = HiddenField('Calendar Data')
    
    submit = SubmitField('Calculer le Salaire') 