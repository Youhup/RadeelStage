from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)
from werkzeug.exceptions import abort

from radeel.db import get_db


import os

import pdfkit

from radeel.auth import login_required

from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, 'French_France')
from radeel.parametre import load_parametres

br = Blueprint('releve', __name__)

@br.before_request
@login_required  
def before_request():
    pass 


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
    
def test_valide(releve):
    if releve['IER'] is None or releve['IER'] == '':
         return False
    if releve['IEA_HC'] is None or releve['IEA_HC'] == '':
         return False
    if releve['IEA_HN'] is None or releve['IEA_HN'] == '':
        return False
    if releve['IEA_HP'] is None or releve['IEA_HP'] == '':
        return False
    if releve['IMAX'] is None or releve['IMAX'] == '':
        return False
    return True

@br.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        mois = request.form.get("mois")
        client = request.form.get("nom")
        statut = request.form.get("statut")
        if mois:
            return redirect(url_for('releve.afficher_modifier', mois=mois, client=client, stat=statut))
    return render_template("releves/index.html")

@br.route("/<mois>/afficher_modifier", methods=["GET", "POST"])
def afficher_modifier(mois):
    db = get_db()
    date = get_date_from_mois(mois)

    client = request.args.get('client')
    stat = request.args.get('stat')

    if not date:
        return redirect(url_for('releve.index'))
    annee, mois_ = date

    if request.method == "POST":
        # Récupérer les données envoyées et faire les mises à jour
        for id in request.form.getlist("id"):
            # Pour chaque relevé on récupère ses valeurs
            indice_ER = request.form.get(f"indice_ER_{id}")
            indice_HC = request.form.get(f"indice_HC_{id}")
            indice_HN = request.form.get(f"indice_HN_{id}")
            indice_HP = request.form.get(f"indice_HP_{id}")
            Red_ER = request.form.get(f"Red_ER_{id}")
            Red_HC = request.form.get(f"Red_HC_{id}")
            Red_HN = request.form.get(f"Red_HN_{id}")
            Red_HP = request.form.get(f"Red_HP_{id}")
            Indic_max = request.form.get(f"Ind_Max_{id}")

            if indice_ER == '' or indice_HC == '' or indice_HN == '' or indice_HP == '' or Indic_max == '':
                statut = 'non valide'
            else:
                statut = 'valide'
            db.execute("""
                UPDATE releves SET
                    IER = ?, IEA_HC = ?, IEA_HN = ?, IEA_HP = ?,
                    RED_ER = ?, RED_EA_HC = ?, RED_EA_HN = ?, RED_EA_HP = ?,
                    IMAX = ?,statut = ?
                WHERE Id = ?
            """, (
                indice_ER, indice_HC, indice_HN, indice_HP,
                Red_ER,Red_HC,Red_HN,Red_HP,Indic_max,statut, id
            ))

        db.commit()
        flash("Modifications enregistrées avec succès", "success")
    
    query = """
        SELECT r.*, c.nom_abonne, c.secteur
        FROM releves r
        JOIN contrats c ON c.Nr_contrat = r.Nr_contrat
        WHERE r.mois = ? AND r.annee = ?
    """
    params = [mois_, annee]

    # Filtre Nom ou ID
    if client:
        if client.isdigit():
            query += " AND c.Nr_contrat = ?"
            params.append(int(client))
        else:
            query += " AND c.nom_abonne LIKE ?"
            params.append(f"%{client}%")

    # Filtre Statut
    if stat:
        query += " AND r.statut = ?"
        params.append(stat)

    # Tri
    query += " ORDER BY c.secteur, c.nom_abonne"

    # Exécution
    releves = db.execute(query, params).fetchall()
    
    if client or stat == 'valide':
        return redirect(url_for('releve.afficher', mois=mois, client=client, stat=stat))
    return render_template("releves/afficher_modifier.html", releves=releves, mois=mois, stat=stat)

@br.route("/afficher")
def afficher():

    mois = request.args.get('mois', '')
    db = get_db()
    date = get_date_from_mois(mois)
    client = request.args.get('client', '')
    stat = request.args.get('stat', '')

    query = """
        SELECT r.*, c.nom_abonne, c.secteur
        FROM releves r
        JOIN contrats c ON c.Nr_contrat = r.Nr_contrat
        WHERE r.mois = ? AND r.annee = ?
    """
    if not date:
        return redirect(url_for('releve.index'))
    annee, mois_ = date
    params = [mois_, annee]

    # Filtre Nom ou ID
    if client:
        if client.isdigit():
            query += " AND c.Nr_contrat = ?"
            params.append(int(client))
        else:
            query += " AND c.nom_abonne LIKE ?"
            params.append(f"%{client}%")

    # Filtre Statut
    if stat:
        query += " AND r.statut = ?"
        params.append(stat)

    # Tri
    query += " ORDER BY c.secteur, c.nom_abonne"

    # Exécution
    releves = db.execute(query, params).fetchall()

    db = get_db()
    date = get_date_from_mois(mois)
    if not date:
        return redirect(url_for('releve.index'))
    annee ,mois_= date
    
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
    return redirect(url_for('releve.afficher_modifier', mois=mois))


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
    retour = request.args.get("retour", url_for("releve.index"))
    
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

        if indice_ER == '' or indice_HC == '' or indice_HN == '' or indice_HP == '' or Indic_max == '':
            statut = 'non valide'
        else:
            statut = 'valide'

        db.execute("""
            UPDATE releves SET 
                IER = ?, IEA_HC = ?, IEA_HN = ?, IEA_HP = ?,
                RED_ER = ?, RED_EA_HC = ?, RED_EA_HN = ?, RED_EA_HP = ?,
                IMAX = ?, statut = ?
            WHERE Id = ?
        """, (
            indice_ER, indice_HC, indice_HN, indice_HP,
            Red_ER, Red_HC, Red_HN, Red_HP, Indic_max, statut, id
        ))
        db.commit()
        return redirect(retour)
    return render_template('releves/modifier.html', releve = releve , mois=mois)

def get_releve(Id):
    releve = get_db().execute(
        'SELECT * FROM releves WHERE Id = ?',(Id,)).fetchone()
    if releve is None:
        abort(404, f"Releve Nr {Id} n'existe pas.")
    return releve


from urllib.parse import quote

def format_file_url(path):
    # 1. Obtenir le chemin absolu
    abs_path = os.path.abspath(path)
    
    # 2. Convertir les backslashes en forward slashes
    forward_slash_path = abs_path.replace('\\', '/')
    
    # 3. Encoder les caractères spéciaux et ajouter le préfixe
    encoded_path = quote(forward_slash_path, safe='/:')
    file_url = f"file:///{encoded_path}"
    
    return file_url

@br.route('/<mois>/calculer')
def calculer(mois):
    
    parametres = load_parametres()

    factures_html = []

    annee, mois_num = mois.split("-")

    non_valide = []

    id = request.args.get('id', '')
    if id:
        releves = [get_releve(id)]
    else:
        releves = get_db().execute(
                'SELECT * FROM releves WHERE mois = ? and annee = ?',
                (mois_num, annee,)).fetchall()

    for releve in releves:
        if releve['statut'] == 'non valide' :
            client = get_db().execute(
                'SELECT nom_abonne FROM contrats WHERE Nr_contrat = ?',
                (releve['Nr_contrat'],)).fetchone()
            non_valide.append(str(client['nom_abonne']))
        else:
            def flash_error(message):
                flash("Index de " + message + " est manquant")

            if releve['IER'] is None or releve['IER'] == '':
                flash_error("energie reactive")
                return redirect(url_for("releve.afficher", mois=mois))
            if releve['IEA_HC'] is None or releve['IEA_HC'] == '':
                flash_error("energie active heures creuses")
                return redirect(url_for("releve.afficher", mois=mois))
            if releve['IEA_HN'] is None or releve['IEA_HN'] == '':
                flash_error("energie active heures normales")
                return redirect(url_for("releve.afficher", mois=mois))
            if releve['IEA_HP'] is None or releve['IEA_HP'] == '':
                flash_error("energie active heures plaines")
                return redirect(url_for("releve.afficher", mois=mois))
            if releve['IMAX'] is None or releve['IMAX'] == '':
                flash_error("maximum")
                return redirect(url_for("releve.afficher", mois=mois))


            date_facture = datetime.today().strftime('%d %B %Y').upper()
            date_facture = date_facture.encode('utf-8').decode('utf-8')

            contrat = get_db().execute(
                'SELECT * FROM contrats WHERE Nr_contrat = ?',
                (releve['Nr_contrat'],)).fetchone()

            if releve['mois'] > 1:
                old_releve = get_db().execute(
                    'SELECT * FROM releves WHERE mois = ? and annee = ? and Nr_contrat = ?',
                    (releve['mois'] - 1, releve['annee'], releve['Nr_contrat'],)).fetchone()
            else:
                old_releve = get_db().execute(
                    'SELECT * FROM releves WHERE annee = ? and Nr_contrat = ? and mois = 12',
                    (releve['annee'] - 1, releve['Nr_contrat'],)).fetchone()
                
            if old_releve :
                old_facture = get_db().execute(
                    'SELECT * FROM factures WHERE id = ?',
                    (old_releve['Id'],)).fetchone()
            
            
            # Calcul d'energie decomptée
            def calcul_ED(old_value, new_value):
                if old_value is None:
                    return new_value
                if old_value > new_value :
                    return 10**parametres['Nr_roues'] + new_value - old_value 
                return new_value - old_value

            #ED = energie  decomptée
            ERD = calcul_ED(old_releve['IER'] if old_releve else None, releve['IER'])
            EAD_HC = calcul_ED(old_releve['IEA_HC'] if old_releve else None, releve['IEA_HC']) 
            EAD_HN = calcul_ED(old_releve['IEA_HN'] if old_releve else None, releve['IEA_HN'])
            EAD_HP = calcul_ED(old_releve['IEA_HP'] if old_releve else None, releve['IEA_HP'])
            
            #Calcul des pertes
            def perte_ED_Red(ED, Red):
                return 0.035 * (ED + Red) if Red > 0 else 0.035 * ED
                
            
            if contrat['type_installation'] == 1:
                Perte_ER = 0 # perte d'energie réactive
                Perte_HC = 0 # perte d'energie active HC
                Perte_HN = 0
                Perte_HP = 0
            else :
                Puiss_pandere =  7.3 * contrat['Puissance_installee']  
                # Calcul des coeficients de perte
                if releve['mois'] < 4 or releve['mois'] > 9:
                    Coef_P_HC = 9/24
                    Coef_P_HN = 10/24
                else:
                    Coef_P_HC = 8/24
                    Coef_P_HN = 11/24
                Coef_P_HP = 5/24
                Perte_ER = round(6 * Puiss_pandere) if contrat['type_installation'] == 2 else 0
                Perte_HC = round(Coef_P_HC * Puiss_pandere  + perte_ED_Red(EAD_HC, releve['RED_EA_HC']))
                Perte_HN = round(Coef_P_HN * Puiss_pandere + perte_ED_Red(EAD_HN, releve['RED_EA_HN']))
                Perte_HP = round(Coef_P_HP * Puiss_pandere + perte_ED_Red(EAD_HP, releve['RED_EA_HP']))

            # Calcul des consommations
            CER = ERD + Perte_ER + releve['RED_ER'] # Consommation d'energie réactive
            CEA_HC = EAD_HC + Perte_HC + releve['RED_EA_HC']
            CEA_HN = EAD_HN + Perte_HN + releve['RED_EA_HN']
            CEA_HP = EAD_HP + Perte_HP + releve['RED_EA_HP']
            Tot_EA = CEA_HC + CEA_HN + CEA_HP #Total de consommation energie active

            # Calcul des montants
            Montant_HC = round(CEA_HC * parametres['Prix_HC'], 2)
            Montant_HN = round(CEA_HN * parametres['Prix_HN'], 2)
            Montant_HP = round(CEA_HP * parametres['Prix_HP'], 2)
            # Montant total
            Montant_total_cons = Montant_HC + Montant_HN + Montant_HP

            # Calcul du cosinus phi
            cos_phi = round(Tot_EA/(CER** 2 + Tot_EA** 2)**0.5,2)

            # Calcul des taxes
            taxe_entretien = parametres['taxe_entretien'] 
            taxe_location = parametres['taxe_location'] 


            # Calcul de puissance appelée
            Puiss_appelee = round(releve['IMAX'] /cos_phi) 

            # Redevance de depassement et puissance
            # Nouvelle contrat : contrat date de moins de 6 mois
            date_contrat = contrat['date_contrat']
            nouvel_contrat = ((date_contrat.year == releve['annee'] and releve['mois'] - date_contrat.mounth <6 ) or 
                            date_contrat.year == releve['annee'] -1 and date_contrat.mounth - releve['mois'] > 6)
            if nouvel_contrat :
                redevance_puiss_cal = max(contrat['puissance_souscrite'],Puiss_appelee)
                Redevance_puiss = round(redevance_puiss_cal * parametres['prix_Red_Puiss_annee'] /12 ,2)
                Depass ,Redevance_depass = 0,0
            else :
                redevance_puiss_cal = contrat['puissance_souscrite']
                Depass = round(Puiss_appelee - contrat['puissance_souscrite']) if Puiss_appelee > contrat['puissance_souscrite'] else 0
                Redevance_depass = round(Depass * parametres['prix_RDPS'],2)
                Redevance_puiss = round(redevance_puiss_cal * parametres['prix_Red_Puiss_annee'] /12 ,2)

            # Majoration
            ecart_cos_phi = round(cos_phi - 0.8 ,2)
            total_cons_maj = round(Montant_total_cons + Redevance_depass + Redevance_puiss,2)
            if ecart_cos_phi < 0 :
                maj_cos_insuff = round(-2 * ecart_cos_phi * total_cons_maj,2)
            else :
                maj_cos_insuff = 0

            # Calcul de TVA
            tva_cons_18 = round((Montant_total_cons + Redevance_depass + Redevance_puiss + maj_cos_insuff) * 18/100 , 2)
            tva_taxes_15 = round(taxe_location * 15 /100 ,2)
            tva_taxes_20 = round(taxe_entretien * 20 /100 ,2)

            #Calcul de Net a payer
            Net_a_payer = round((Montant_total_cons + Redevance_depass + Redevance_puiss + maj_cos_insuff +
                            taxe_entretien + taxe_location +
                            tva_cons_18 + tva_taxes_15 + tva_taxes_20),2)
            
            # Calcul du cumul annuel
            
            if old_facture :
                cumul_EA_annuel = old_facture['cumul_EA_annuel'] + Tot_EA
            else:   
                cumul_EA_annuel = Tot_EA
            
            facture = {'ERD':ERD , 'EAD_HC' : EAD_HC, 'EAD_HN' : EAD_HN ,'EAD_HP': EAD_HP,
                    'Perte_ER': Perte_ER,'Perte_HC':Perte_HC,'Perte_HN':Perte_HN,'Perte_HP':Perte_HP,
                    'CER':CER,'CHC':CEA_HC,'CHN':CEA_HN,'CHP':CEA_HP,
                    'total_EA':Tot_EA,'cumul_annuel':cumul_EA_annuel,
                    'cos_phi':cos_phi,'ecart_cos_phi':ecart_cos_phi,
                    'puiss_appele':Puiss_appelee ,
                    'montant_HC':Montant_HC,'montant_HN':Montant_HN,'montant_HP':Montant_HP,
                    'Rend_puiss_cal':redevance_puiss_cal,'Rend_puis':Redevance_puiss,
                    'depass_puiss':Depass,'Rend_depass':Redevance_depass,
                    'tva_18':tva_cons_18,'tva_15':tva_taxes_15,'tva_20':tva_taxes_20,
                    'Cons_maj':total_cons_maj, 'debit_maj':maj_cos_insuff,
                    'Net_apayer':Net_a_payer, 'date':date_facture}
            
            # Enregistrer la facture
            db = get_db()
            try:
            
                db.execute(
                    'INSERT INTO factures (id,Nr_contrat, Net_apayer,cumul_EA_annuel) VALUES (?, ?, ?,?)',
                    (releve['id'],contrat['Nr_contrat'], facture['Net_apayer'],cumul_EA_annuel)
                )
                        
                db.commit()
            except db.IntegrityError:
                db.execute(
                    'UPDATE factures set Nr_contrat =? , Net_apayer = ?,cumul_EA_annuel= ? where id = ?',
                    (contrat['Nr_contrat'], facture['Net_apayer'],cumul_EA_annuel,releve['id'],)
                )
                
            #path vers l'image
            chemin_relatif = "radeel/static/images/target001.jpg"
            url_facture = format_file_url(chemin_relatif)


            rendered = render_template('releves/calculer.html', 
                                    releve=releve, 
                                    old_releve=old_releve,
                                    contrat=contrat,
                                    parametres=parametres,
                                    facture=facture,
                                    url_facture = url_facture)
            
            factures_html.append(rendered)

    if non_valide: factures_html.append(render_template('releves/non_valide.html', mois=mois, non_valide=non_valide))
    
    html_complet = '<div style="page-break-after: always;"></div>'.join(factures_html)

    # Configuration pour PDFKit
    options = {
        'enable-local-file-access': '',
        'encoding': 'UTF-8',
        'page-size': 'A4',
    }
    # Générer le PDF
    pdf = pdfkit.from_string(html_complet, False, options=options)
    
    # Créer la réponse
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=facture.pdf'
    
    return response