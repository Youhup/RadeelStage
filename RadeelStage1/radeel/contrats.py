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

@bc.route('/<int:contrat_id>/details')
def details_contrat(contrat_id):
    db = get_db()
    contrat = db.execute('''
        SELECT Nr_contrat, nom_abonne, Adresse, date_contrat, 
               Secteur, Puissance_souscrite, Puissance_installee, type_installation
        FROM contrats
        WHERE Nr_contrat = ?
    ''', (contrat_id,)).fetchone()
    
    if contrat is None:
        flash('Contrat non trouvé.', 'warning')
        return redirect(url_for('contrats.liste_contrats'))
    
    return render_template('contrats/details.html', contrat=contrat)

@bc.route('/<int:contrat_id>/modifier', methods=['GET', 'POST'])
def modifier_contrat(contrat_id):
    db = get_db()
    
    # Récupérer le contrat existant
    contrat = db.execute(
        'SELECT * FROM contrats WHERE Nr_contrat = ?', 
        (contrat_id,)
    ).fetchone()
    
    if not contrat:
        flash('Contrat non trouvé', 'danger')
        return redirect(url_for('contrats.liste_contrats'))
    
    # Initialiser le formulaire
    form = AjouterContratForm()
    
    # Si soumission du formulaire
    if request.method == 'POST':
        form = AjouterContratForm(request.form)
        
        if form.validate():
            try:
                # Mise à jour des données
                db.execute('''
                    UPDATE contrats SET
                        nom_abonne = ?,
                        Adresse = ?,
                        Secteur = ?,
                        Puissance_souscrite = ?,
                        Puissance_installee = ?,
                        type_installation = ?
                    WHERE Nr_contrat = ?
                ''', (
                    form.nom_abonne.data,
                    form.Adresse.data,
                    form.Secteur.data,
                    form.Puissance_souscrite.data,
                    form.Puissance_installee.data,
                    form.type_installation.data,
                    contrat_id
                ))
                db.commit()
                flash('Contrat mis à jour avec succès!', 'success')
                return redirect(url_for('contrats.details_contrat', contrat_id=contrat_id))
            except Exception as e:
                db.rollback()
                flash(f'Erreur lors de la mise à jour: {str(e)}', 'danger')
        else:
            flash('Veuillez corriger les erreurs dans le formulaire', 'warning')
    
    # Pré-remplir le formulaire pour les requêtes GET
    elif request.method == 'GET':
        form.nom_abonne.data = contrat['nom_abonne']
        form.Adresse.data = contrat['Adresse']
        form.Secteur.data = contrat['Secteur']
        form.Puissance_souscrite.data = contrat['Puissance_souscrite']
        form.Puissance_installee.data = contrat['Puissance_installee']
        form.type_installation.data = contrat['type_installation']
    
    return render_template('contrats/modifier.html', form=form, contrat=contrat)

@bc.route('/<int:contrat_id>/supprimer', methods=['POST'])
def supprimer_contrat(contrat_id):
    db = get_db()
    contrat = db.execute('''
        SELECT Nr_contrat FROM contrats WHERE Nr_contrat = ?
    ''', (contrat_id,)).fetchone()
    
    if contrat is None:
        flash('Contrat non trouvé.', 'warning')
        return redirect(url_for('contrats.liste_contrats'))
    
    try:
        db.execute('DELETE FROM contrats WHERE Nr_contrat = ?', (contrat_id,))
        db.commit()
        flash('Contrat supprimé avec succès!', 'success')
    except Exception as e:
        db.rollback()
        flash(f"Erreur lors de la suppression du contrat: {str(e)}", 'danger')
    
    return redirect(url_for('contrats.liste_contrats')) 

@bc.route('/rechercher', methods=['GET', 'POST'])
def rechercher_contrat():
    db = get_db()
    query = request.form.get('query', '')
    
    if query:
        contrats = db.execute('''
            SELECT Nr_contrat, nom_abonne, Adresse, date_contrat, 
                   Puissance_souscrite, type_installation
            FROM contrats
            WHERE nom_abonne LIKE ? OR Nr_contrat LIKE ?
            ORDER BY nom_abonne
        ''', ('%' + query + '%', '%' + query + '%')).fetchall()
    else:
        contrats = []
    
    return render_template('contrats/rechercher.html', contrats=contrats, query=query)

#view pour importer)exporter les contrats depuis un fichier CSV
#utile si quelqu'un veut ajouter les contrats automatiquement
@bc.route('/importer', methods=['GET', 'POST'])
def importer_contrats():
    from werkzeug.utils import secure_filename
    import csv
    
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.csv'):
            flash('Veuillez télécharger un fichier CSV valide.', 'danger')
            return redirect(url_for('contrats.importer_contrats')) 
         

  

@bc.route('/statistiques')
def statistiques_contrats():    
    db = get_db()
    
    # Example statistics: count of contracts by type of installation
    stats = db.execute('''
        SELECT type_installation, COUNT(*) as count
        FROM contrats
        GROUP BY type_installation
    ''').fetchall()
    
    return render_template('contrats/statistiques.html', stats=stats)         
