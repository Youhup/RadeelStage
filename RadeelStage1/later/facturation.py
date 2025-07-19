from datetime import datetime
from flask import current_app

def generer_facture(releve_id: int) -> dict:
    #Génère une facture sans la persister
    db = current_app._get_current_object().db
    params = current_app.parametres_systeme

    # Récupère le relevé et le précédent
    releve, precedent = db.execute('''
        SELECT curr.*, prev.* FROM releves_index curr
        LEFT JOIN releves_index prev ON 
            curr.Nr_contrat = prev.Nr_contrat AND 
            prev.date_releve = (
                SELECT MAX(date_releve) 
                FROM releves_index 
                WHERE Nr_contrat = curr.Nr_contrat AND date_releve < curr.date_releve
            )
        WHERE curr.id = ?
    ''', (releve_id,)).fetchone()

    if not releve:
        raise ValueError("Relevé non trouvé")

    # Calcul des consommations
    conso_hc = releve['IEA_HC'] - (precedent['IEA_HC'] if precedent else 0)
    conso_hp = releve['IEA_HP'] - (precedent['IEA_HP'] if precedent else 0)
    conso_hn = releve['IEA_HN'] - (precedent['IEA_HN'] if precedent else 0)

    # Calcul des montants
    montant_hc = conso_hc * params.get('tarif_hc')
    montant_hp = conso_hp * params.get('tarif_hp')
    montant_hn = conso_hn * params.get('tarif_hn')
    taxe_fixe = params.get('taxe_fixe')
    tva = params.get('tva')

    # Calcul du total
    total = (montant_hc + montant_hp + montant_hn + taxe_fixe) * (1 + tva)

    return {
        'releve_id': releve_id,
        'Nr_contrat': releve['Nr_contrat'],
        'periode_debut': precedent['date_releve'] if precedent else releve['date_releve'],
        'periode_fin': releve['date_releve'],
        'total_a_payer': round(total, 2),
        'numero_facture': f"FAC-{releve_id}-{datetime.now().strftime('%Y%m%d')}",
        'statut': 'encours de traitement',  
    }

def creer_facture(releve_id):
    """Génère ET persiste une facture"""
    facture_data = generer_facture(releve_id)
    
    db = current_app.db
    db.execute('''
        INSERT INTO factures (
            Nr_contrat, releve_id, date_emission,
            periode_debut, periode_fin, total_a_payer,
            numero_facture, statut
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        facture_data['Nr_contrat'],
        facture_data['releve_id'],
        datetime.now().date(),
        facture_data['periode_debut'],
        facture_data['periode_fin'],
        facture_data['total_a_payer'],
        facture_data['numero_facture'],
        facture_data['statut']
    ))
    db.commit()
    
    return facture_data