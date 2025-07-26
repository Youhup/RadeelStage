from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from radeel.db import get_db



br = Blueprint('releve', __name__)


def generer_ID_facture( Secteur, Nr_contrat,mois,annee ): 
    return f"{Secteur}{Nr_contrat}{mois:02d}{annee}"

def get_date_from_mois(mois):
    try:
        annee,mois = map(int, mois.split("-"))
        if 1 <= mois <= 12:
            return  annee, mois
        else:
            raise ValueError("Mois invalide")
    except ValueError:
        flash("Format de mois invalide. Utilisez 'MM-AAAA'.", "error")
        return None
    

@br.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        mois = request.form.get("mois")
        if mois:
            return redirect(url_for('releve.afficher', mois=mois))
    return render_template("releves/index.html")

@br.route("/<mois>/afficher")
def afficher(mois):
    
    db = get_db()
    date = get_date_from_mois(mois)
    if not date:
        return redirect(url_for('releve.index'))
    annee ,mois_= date

    releves = db.execute("""
        SELECT r.*, c.nom_abonne
        FROM releves r
        JOIN contrats c ON c.Nr_contrat = r.Nr_contrat
        WHERE r.mois = ? and r.annee = ?
    """, (mois_,annee,)).fetchall()
    
    return render_template("releves/afficher.html", releves=releves, mois=mois)


@br.route("/<mois>/creer", methods=["GET"])
def creer(mois):
    db = get_db()
    date = get_date_from_mois(mois)
    if not date:
        flash("Format de mois invalide. Utilisez 'MM-AAAA'.", "error")
        return redirect(url_for('releve.index'))
    annee, mois_ = date
    # les contrats doivent avoir date_contrat <= date du mois
    contrats = db.execute("""
    SELECT Nr_contrat, secteur, date_contrat 
    FROM contrats 
    WHERE statut = 'actif'
    AND strftime('%Y-%m', date_contrat) <= ?
""", (f"{annee}-{mois_:02d}",)).fetchall()

    for contrat in contrats:
        db.execute("""
            INSERT INTO releves (Id, Nr_contrat, mois ,annee) values (?, ?, ?, ?)""", 
            (generer_ID_facture(contrat['secteur'], contrat['Nr_contrat'],mois_, annee),
              contrat['Nr_contrat'], mois_, annee,))
    db.commit()
    return redirect(url_for('releve.afficher', mois=mois))


@br.route("/<id>/modifier", methods=["GET", "POST"])
def modifier(id):
    db = get_db()
    releve = db.execute("""
        SELECT r.*, c.nom_abonne
        FROM releves r
        JOIN contrats c ON c.Nr_contrat = r.Nr_contrat
        WHERE r.id= ? """, (id,)).fetchone()
    if  releve is None:
        flash("Relevé non trouvé.", "error")
        return redirect(url_for('releve.index'))
    mois = f"{releve['annee']}-{releve['mois']}"
    
    if request.method == "POST":
        # Récupérer les valeurs du formulaire
        indice_ER = request.form.get("indice_ER")
        indice_HC = request.form.get("indice_HC")
        indice_HN = request.form.get("indice_HN")
        indice_HP = request.form.get("indice_HP")
        Red_ER = request.form.get("Red_ER") or "0"
        Red_HC = request.form.get("Red_HC") or "0"
        Red_HN = request.form.get("Red_HN") or "0"
        Red_HP = request.form.get("Red_HP") or "0"
        Indic_max = request.form.get("Indic_max")

        db.execute("""
            UPDATE releves SET 
                IER = ?, IEA_HC = ?, IEA_HN = ?, IEA_HP = ?,
                RED_ER = ?, RED_EA_HC = ?, RED_EA_HN = ?, RED_EA_HP = ?,
                IMAX = ?
            WHERE Id = ?
        """, (
            indice_ER, indice_HC, indice_HN, indice_HP,
            Red_ER, Red_HC, Red_HN, Red_HP, Indic_max, id
        ))
        db.commit()
        return redirect(url_for("releve.afficher", mois=mois))
    return render_template('releves/modifier.html', releve = releve , mois=mois)







