from radeel.db import get_db
from radeel.form import AjouterContratForm

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)


bc = Blueprint('contrats', __name__, url_prefix='/contrats')

@bc.route('/ajouter', methods=['GET', 'POST'])
def ajouter_contrat():
    form = AjouterContratForm()
    db = get_db()
    
    if form.validate_on_submit():
        try:
            db.execute('''
                INSERT INTO contrats (
                    Nr_contrat, nom_abonne, Adresse, date_contrat,
                    Secteur, Puissance_souscrite, Puissance_installee, type_installation
                ) VALUES (?, ?, ?, CURRENT_DATE, ?, ?, ?, ?)
            ''', (
                form.Nr_contrat.data,
                form.nom_abonne.data,
                form.Adresse.data,
                form.Secteur.data,
                form.Puissance_souscrite.data,
                form.Puissance_installee.data,
                form.type_installation.data
            ))
            db.commit()
            flash('Contrat ajouté avec succès!', 'success')
            return redirect(url_for('contrats.liste_contrats'))
        except Exception as e:
            db.rollback()
            flash(f"Erreur lors de l'ajout du contrat: {str(e)}", 'danger')
    
    return render_template('contrats/ajouter.html', form=form)

@bc.route('/liste')
def liste_contrats():
    db = get_db()
    contrats = db.execute('''
        SELECT Nr_contrat, nom_abonne, Adresse, date_contrat, 
               Puissance_souscrite, type_installation
        FROM contrats
        ORDER BY nom_abonne
    ''').fetchall()
    return render_template('contrats/liste.html', contrats=contrats)