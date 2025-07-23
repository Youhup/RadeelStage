from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from radeel.db import get_db

br = Blueprint('releve', __name__, url_prefix='/releve')


@br.route('/')
def index():
    db = get_db()
    releves = db.execute(
        'SELECT * FROM releves_index ORDER BY date_releve DESC'
    ).fetchall()
    return render_template('releves/index.html', releves= releves)

@br.route('/ajouter', methods=('GET', 'POST'))
def ajouter():
    if request.method == 'POST':
        Nr_contrat = request.form['Nr_contrat']
        date = request.form['date_releve']
        IEA_HC = request.form['IEA_HC']
        IEA_HP = request.form['IEA_HP']
        IEA_HN = request.form['IEA_HN']
        I_energie_reactif = request.form['I_energie_reactif']
        Puissance_demande = request.form['Puissance_demande']
        error = None

        if not Nr_contrat or not Nr_contrat.isdigit():
            error = 'Nr_contrat is required.'
        elif not date:
            error = 'Date is required.'
        elif not IEA_HC or not IEA_HC.isdigit():
            error = 'IEA_HC is required.'
        elif not IEA_HP or not IEA_HP.isdigit():
            error = 'IEA_HP is required.'
        elif not IEA_HN or not IEA_HN.isdigit():
            error = 'IEA_HN is required.'
        elif not I_energie_reactif or not I_energie_reactif.isdigit():
            error = 'I_energie_reactif is required.'
        elif not Puissance_demande or not Puissance_demande.isdigit():
            error = 'Puissance_demande is required.'


        if error is not None:
            flash(error)
        else:
            db = get_db()
            try:
               
                db.execute(
                    'INSERT INTO releves_index (Nr_contrat, date_releve, IEA_HC, IEA_HP, IEA_HN, I_energie_reactif, Puissance_demande) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (int(Nr_contrat), date, int(IEA_HC), int(IEA_HP), int(IEA_HN), int(I_energie_reactif), int(Puissance_demande))
            )
                
                db.commit()
            except db.IntegrityError:
                error = f"Le contrat avec le numéro {Nr_contrat} n'existe pas."
                flash(error)    
            else:
                flash('Releve ajouté avec succès!')
                # Redirect to the contrat index page after successful addition
                return redirect(url_for('releve.index'))   

    return render_template('releves/ajouter.html')