from flask import Blueprint, request, render_template, redirect, url_for, flash
import json
import os

bp = Blueprint('parametres', __name__, url_prefix='/parametres')

# Chemin du fichier JSON
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

@bp.route('/', methods=['GET', 'POST'])
def admin():
    # Charger les paramètres actuels
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    if request.method == 'POST':
        try:
            # Mettre à jour tous les paramètres
            config.update({
                'Nr_roues': int(request.form['nr_roues']),
                'Prix_HC': float(request.form['prix_hc']),
                'Prix_HN': float(request.form['prix_hn']),
                'Prix_HP': float(request.form['prix_hp']),
                'taxe_entretien': float(request.form['taxe_entretien']),
                'taxe_location': float(request.form['taxe_location']),
                'prix_RDPS': float(request.form['prix_rdps']),
                'prix_Red_Puiss_annee': float(request.form['prix_red_puiss_annee'])
            })
            
            # Sauvegarder
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=4)
            
            flash("Paramètres mis à jour avec succès !", "success")
        except (ValueError, KeyError) as e:
            flash(f"Erreur : Donnée invalide ({str(e)})", "danger")
        
        return redirect(url_for('parametres.admin'))
    
    return render_template('admin.html', config=config)

def load_parametres():
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    return config