
    @br.route("/afficher")
def afficher():















    
    db = get_db()
    # Vérifier si le mois est valide
    date = get_date_from_mois(mois)
    if not date:
        return redirect(url_for('releve.index'))
    annne, mois_ = date
    # Vérifier si des relevés existent déjà
    releves = db.execute("""
        SELECT releves.*, contrats.nom_abonne
        FROM releves
        JOIN contrats ON contrats.Nr_contrat = releves.Nr_contrat
        WHERE mois = ? and annee = ?
    """, (mois_,annne,)).fetchall()


    if releves:
        return redirect(url_for('releve.modifier_releves', mois=mois))
    # Sinon, les créer
    contrats = db.execute("SELECT Nr_contrat , secteur , date_contrat FROM contrats where statut = 'actif'").fetchall()

    for contrat in contrats:
        db.execute("""
            INSERT INTO releves (Id, Nr_contrat, mois ,annee, IER ,IEA_HC, IEA_HN, IEA_HP,RED_ER ,RED_EA_HC, RED_EA_HN, RED_EA_HP, IMAX) values (?, ?, ?, ?, NUll, NUll, NUll, NUll, NUll, NUll, NUll, NUll, NUll)
        """, (generer_ID_facture(contrat['secteur'], contrat['Nr_contrat'], contrat['date_contrat']),
              contrat['Nr_contrat'], mois_, annne,))
    db.commit()
    return redirect(url_for('releve.modifier_releves', mois=mois))



@br.route("/<mois>/modifier", methods=["GET", "POST"])
def modifier_releves(mois):
    db = get_db()

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
            Indic_max = request.form.get(f"Indic_max_{id}")
            db.execute("""
                UPDATE releves SET
                    IER = ?, IEA_HC = ?, IEA_HN = ?, IEA_HP = ?,
                    RED_ER = ?, RED_EA_HC = ?, RED_EA_HN = ?, RED_EA_HP = ?,
                    IMAX = ?
                WHERE Id = ?
            """, (
                indice_ER, indice_HC, indice_HN, indice_HP,
                Red_ER,Red_HC,Red_HN,Red_HP,Indic_max, id
            ))

        db.commit()
        return redirect(url_for("releve.inndex"))
    


    # GET : afficher le formulaire pré-rempli
    releve = db.execute("""
        SELECT r.*, c.nom
        FROM releves r
        JOIN contrats c ON c.Nr_contrat = r.Nr_contrat
        WHERE r.Id = ?
    """, (id,)).fetchone()


    if releve is None:
        abort(404, f"Releve de id {id} n'existe pas.")

    return render_template("releves/modifier_un_releve.html", releve=releve)


def afficher_modifier(mois):
    db = get_db()
    date = get_date_from_mois(mois)
    if not date:
        return redirect(url_for('releve.index'))
    annee, mois_ = date

    releves = db.execute("""
        SELECT r.*, c.nom_abonne, c.secteur
        FROM releves r
        JOIN contrats c ON c.Nr_contrat = r.Nr_contrat
        WHERE r.mois = ? and r.annee = ?
        ORDER BY c.secteur, c.nom_abonne
    """, (mois_, annee,)).fetchall()
    
    for releve in releves:
            if test_valide(releve):
                db.execute("""
                    UPDATE releves SET statut = 'valide' WHERE Id = ?
                """, (releve['Id'],))
                
    db.commit()

    if request.method == "POST":
        # Traitement des modifications en masse
        for key, value in request.form.items():
            if key.startswith('indice_'):
                info = key.split('_')
                id = info[-1]  # Récupérer l'ID du relevé
                field = '_'.join(info[1:-1]) 
                db.execute(f"""
                    UPDATE releves SET 
                        {field} = ?
                    WHERE Id = ?
                """, (value, id))
        db.commit()
        # Mise à jour du statut des relevés
        
        flash("Modifications enregistrées avec succès", "success")
        return redirect(url_for('releve.afficher_modifier', mois=mois))
    
    return render_template("releves/afficher_modifier.html", releves=releves, mois=mois)

<img width="892" height="1262" src="file:///C:/Users/HP/Desktop/radeel/project_clone/RadeelStage/RadeelStage1/radeel/static/images/target001.jpg" alt="background image"/>
file:///C:/Users/elaou/OneDrive/Desktop/RadeelStage/RadeelStage1/static/images/target001.jpg
        C:\Users\elaou\OneDrive\Desktop\RadeelStage\RadeelStage1\radeel\static\images


    
    
    for releve in releves:
            if test_valide(releve):
                db.execute("""
                    UPDATE releves SET statut = 'valide' WHERE Id = ?
                """, (releve['Id'],))
                
    db.commit()

@bp.route('/default', methods=['POST', 'GET'])
def default():
    
    try:     
            # Sauvegarder
        with open(CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        flash("Paramètres mis à default avec succès !", "success")
    except (ValueError, KeyError) as e:
        flash(f"Erreur : Donnée invalide ({str(e)})", "danger")
        
        return redirect(url_for('parametres.admin'))
    return render_template('admin.html', config = DEFAULT_CONFIG)