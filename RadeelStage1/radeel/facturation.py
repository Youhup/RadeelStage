from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from radeel.db import get_db

bf = Blueprint('facturation', __name__,url_prefix='/facturation')

def get_releve(Id):
    releve = get_db().execute(
        'SELECT * FROM releves_index WHERE Id = ?',(Id,)).fetchone()
    if releve is None:
        abort(404, f"Releve Nr {Id} n'existe pas.")
    return releve

@bf.route('/')
def index():
    db = get_db()
    releves = db.execute(
        'SELECT * FROM releves_index ORDER BY date_releve DESC'
    ).fetchall()
    return render_template('releves/index.html', releves= releves)



@bf.route('/<int:id>/calculer', methods='GET')
def calculer(id):
    releve = get_releve(id)
    IEA_HC = releve['IEA_HC']
    IEA_HP = releve['IEA_HP']
    IEA_HN = releve['IEA_HN']
    I_energie_reactif = releve['I_energie_reactif']
    Puissance_demande = releve['Puissance_demande']
    
    # Calcul des valeurs
    total_energie_active = IEA_HC + IEA_HP + IEA_HN
    cos_O = total_energie_active/(I_energie_reactif** 2 + total_energie_active** 2)**0.5
    Valeurs = {
        'IEA_HC': IEA_HC,
        'IEA_HP': IEA_HP,
        'IEA_HN': IEA_HN,
        'I_energie_reactif': I_energie_reactif,
        'Puissance_demande': Puissance_demande,
        'total_energie_active': total_energie_active,
        'cos_O': cos_O
    }
    return render_template('releves/calculer.html', releve=releve, Valeurs=Valeurs)
 