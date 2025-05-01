from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class ProfileForm(FlaskForm):
    """Form for creating and editing user profiles."""
    name = StringField('Nom complet', validators=[
        DataRequired(message="Le nom est requis.")
    ])
    
    hourly_rate = FloatField('Taux horaire (DH/h)', validators=[
        DataRequired(message="Le taux horaire est requis."),
        NumberRange(min=0, message="Le taux horaire doit être positif.")
    ])
    
    function_bonus_base_amount = FloatField('Prime de fonction (DH)', validators=[
        Optional(),
        NumberRange(min=0, message="La prime de fonction doit être positive.")
    ], default=0)
    
    performance_bonus_amount = FloatField('Prime de performance (DH)', validators=[
        Optional(),
        NumberRange(min=0, message="La prime de performance doit être positive.")
    ], default=0)
    
    prime_de_niveau_amount = FloatField('Prime de niveau (DH)', validators=[
        Optional(),
        NumberRange(min=0, message="La prime de niveau doit être positive.")
    ], default=0)
    
    seniority_rate_percent = FloatField('Taux d\'ancienneté (%)', validators=[
        Optional(),
        NumberRange(min=0, max=100, message="Le taux d'ancienneté doit être compris entre 0 et 100%.")
    ], default=0)
    
    submit = SubmitField('Enregistrer') 