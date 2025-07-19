from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField
from wtforms.validators import DataRequired, NumberRange

class AjouterContratForm(FlaskForm):
    Nr_contrat = IntegerField('Numéro de contrat', validators=[DataRequired()])
    nom_abonne = StringField('Nom abonné', validators=[DataRequired()])
    Adresse = StringField('Adresse', validators=[DataRequired()])
    Secteur = IntegerField('Secteur', validators=[DataRequired(), NumberRange(min=1)])
    Puissance_souscrite = IntegerField('Puissance souscrite (kW)', validators=[DataRequired(), NumberRange(min=1)])
    Puissance_installee = IntegerField('Puissance installée (kW)', validators=[DataRequired(), NumberRange(min=1)])
    type_installation = IntegerField('Type installation (1, 2 ou 12)', validators=[DataRequired()])