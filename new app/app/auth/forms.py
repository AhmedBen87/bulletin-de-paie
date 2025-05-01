from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    """User login form."""
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion')

class RegistrationForm(FlaskForm):
    """User registration form."""
    username = StringField('Nom d\'utilisateur', validators=[
        DataRequired(), 
        Length(min=3, max=64, message="Le nom d'utilisateur doit contenir entre 3 et 64 caractères.")
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message="Veuillez entrer une adresse email valide.")
    ])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(),
        Length(min=8, message="Le mot de passe doit contenir au moins 8 caractères.")
    ])
    password2 = PasswordField('Répéter le mot de passe', validators=[
        DataRequired(), 
        EqualTo('password', message="Les mots de passe ne correspondent pas.")
    ])
    submit = SubmitField('S\'inscrire')

    def validate_username(self, username):
        """Check if username is already in use."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Ce nom d\'utilisateur est déjà utilisé. Veuillez en choisir un autre.')

    def validate_email(self, email):
        """Check if email is already in use."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Cette adresse email est déjà utilisée. Veuillez en choisir une autre.') 