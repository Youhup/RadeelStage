from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from radeel.db import get_db

from radeel.auth import login_required

bc = Blueprint('contrat', __name__, url_prefix='/contrat')

@bc.before_request
@login_required  
def before_request():
    pass 

@bc.route('/')
def contrat_index():
    db = get_db()
    contrats = db.execute(
        'SELECT * FROM contrats ORDER BY date_contrat DESC'
    ).fetchall()
    return render_template('contrats/index.html', contrats= contrats )

@bc.route('/ajouter', methods=('GET', 'POST'))
def contrat_ajouter():
    if request.method == 'POST':
        Nr_contrat = request.form['Nr_contrat']
        nom_abonne = request.form['nom_abonne']
        Adresse = request.form['Adresse']
        date = request.form['date_contrat']
        Secteur = request.form['Secteur']
        Puissance_souscrite = request.form['Puissance_souscrite']
        Puissance_installee = request.form['Puissance_installee']
        type_installation = request.form['type_installation']
        error = None

        """if not Nr_contrat or not Nr_contrat.isdigit():
            error = 'Nr_contrat is required.'"""
        if not nom_abonne:
            error = 'Nom abonné is required.'
        elif not Adresse:
            error = 'Adresse is required.'
        elif not Secteur:
            error = 'Secteur is required.'
        elif not Puissance_souscrite or not Puissance_souscrite.isdigit():
            error = 'Puissance souscrite is required.'
        elif not Puissance_installee or not Puissance_installee.isdigit():
            error = 'Puissance installée is required.'
        elif not type_installation or not type_installation.isdigit() or int(type_installation) not in [1, 2, 12]:
            error = 'Type installation is required.'


        if error is not None:
            flash(error)
        else:
            db = get_db()
            try:
               
                db.execute(
                    'INSERT INTO contrats (Nr_contrat, nom_abonne, Adresse, date_contrat, Secteur, Puissance_souscrite, Puissance_installee, type_installation) VALUES (?, ?, ?,?, ?, ?, ?, ?)',
                (int(Nr_contrat), nom_abonne, Adresse,date ,Secteur, int(Puissance_souscrite), int(Puissance_installee), int(type_installation))
            )
                
                db.commit()
            except db.IntegrityError:
                error = f"Contrat {Nr_contrat} existe."
                flash(error)
            else:
                flash('Contrat ajouté avec succès!')
                # Redirect to the contrat index page after successful addition
                return redirect(url_for('contrat.contrat_index'))   

    return render_template('contrats/ajouter.html')

def get_contrat(Nr_contrat):
    contrat = get_db().execute(
        'SELECT * FROM contrats WHERE Nr_contrat = ?',(Nr_contrat,)).fetchone()
    if contrat is None:
        abort(404, f"Contrat Nr_contrat {Nr_contrat} n'existe pas.")

    return contrat

@bc.route('/<int:Nr_contrat>/modifier', methods=('GET', 'POST'))
def contrat_modifier(Nr_contrat):
    contrat = get_contrat(Nr_contrat)
    
    if request.method == 'POST':
        nom_abonne = request.form['nom_abonne']
        Adresse = request.form['Adresse']
        date = request.form['date_contrat']
        Secteur = request.form['Secteur']
        Puissance_souscrite = request.form['Puissance_souscrite']
        Puissance_installee = request.form['Puissance_installee']
        type_installation = request.form['type_installation']
        error = None

       
        if not nom_abonne:
            error = 'Nom abonné is required.'
        elif not Adresse:
            error = 'Adresse is required.'
        elif not Secteur:
            error = 'Secteur is required.'
        elif not Puissance_souscrite or not Puissance_souscrite.isdigit():
            error = 'Puissance souscrite is required.'
        elif not Puissance_installee or not Puissance_installee.isdigit():
            error = 'Puissance installée is required.'
        elif not type_installation or not type_installation.isdigit() or int(type_installation) not in [1, 2, 12]:
            error = 'Type installation is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE contrats SET nom_abonne = ?, Adresse = ?, date_contrat = ?, Secteur = ?, Puissance_souscrite = ?, Puissance_installee = ?, type_installation = ? WHERE Nr_contrat = ?',
                (nom_abonne, Adresse, date, Secteur, int(Puissance_souscrite), int(Puissance_installee), int(type_installation), Nr_contrat))
            db.commit()
            return redirect(url_for('contrat.contrat_index'))

    return render_template('contrats/modifier.html', contrat=contrat)



@bc.route('/<int:Nr_contrat>/supprimer', methods=('POST',))
def contrat_supprimer(Nr_contrat):
    get_contrat(Nr_contrat)
    db = get_db()
    db.execute('DELETE FROM contrats WHERE Nr_contrat = ?', (Nr_contrat,))
    db.commit()
    return redirect(url_for('contrat.contrat_index'))