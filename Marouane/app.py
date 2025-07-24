from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("factures.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET"])
def main():
    return render_template("releves_insertion.html")

@app.route("/afficher_releves", methods=["POST"])
def afficher_releves():
    mois = request.form["mois"]
    conn = get_db_connection()
    cur = conn.cursor()

    # Vérifier si des relevés existent déjà
    cur.execute("""
        SELECT releves.*, contrats.nom
        FROM releves
        JOIN contrats ON contrats.contrat_id = releves.contrat_id
        WHERE date = ?
    """, (mois,))
    releves = cur.fetchall()

    if releves:
        # Relevés existent déjà : les afficher
        conn.close()
        return redirect(url_for('afficher_releves_mois', mois=mois))
    # Sinon, les créer
    cur.execute("SELECT contrat_id FROM contrats")
    contrats = cur.fetchall()

    for contrat in contrats:
        cur.execute("""
            INSERT INTO releves (contrat_id, date, indice_ER, indice_HC, indice_HN, indice_HP, perte_ER, perte_HC, perte_HN, perte_HP, puissance_demandee)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (contrat["contrat_id"], mois, None, None, None, None, None, None, None, None, None))

    conn.commit()
    conn.close()
    return redirect(f'/modifier_releves/{mois}')

@app.route("/afficher_releves/<mois>")
def afficher_releves_mois(mois):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT r.*, c.nom
        FROM releves r
        JOIN contrats c ON c.contrat_id = r.contrat_id
        WHERE r.date = ?
    """, (mois,))
    releves = cur.fetchall()
    conn.close()
    
    return render_template("formulaire.html", releves=releves, mois=mois)

@app.route("/modifier_releves/<mois>", methods=["GET", "POST"])
def modifier_releves(mois):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        # Récupérer les données envoyées et faire les mises à jour
        for releve_id in request.form.getlist("releve_id"):
            # Pour chaque relevé on récupère ses valeurs
            indice_ER = request.form.get(f"indice_ER_{releve_id}")
            indice_HC = request.form.get(f"indice_HC_{releve_id}")
            indice_HN = request.form.get(f"indice_HN_{releve_id}")
            indice_HP = request.form.get(f"indice_HP_{releve_id}")
            perte_ER = request.form.get(f"perte_ER_{releve_id}")
            perte_HC = request.form.get(f"perte_HC_{releve_id}")
            perte_HN = request.form.get(f"perte_HN_{releve_id}")
            perte_HP = request.form.get(f"perte_HP_{releve_id}")
            puissance_demandee = request.form.get(f"puissance_demandee_{releve_id}")

            cur.execute("""
                UPDATE releves SET
                    indice_ER = ?, indice_HC = ?, indice_HN = ?, indice_HP = ?,
                    perte_ER = ?, perte_HC = ?, perte_HN = ?, perte_HP = ?,
                    puissance_demandee = ?
                WHERE releve_id = ?
            """, (
                indice_ER, indice_HC, indice_HN, indice_HP,
                perte_ER, perte_HC, perte_HN, perte_HP,
                puissance_demandee, releve_id
            ))

        conn.commit()
    
    # Afficher les relevés pour le mois (GET ou après POST)
    cur.execute("""
        SELECT r.*, c.nom
        FROM releves r
        JOIN contrats c ON c.contrat_id = r.contrat_id
        WHERE r.date = ?
    """, (mois,))
    releves = cur.fetchall()
    conn.close()
    return render_template("modifier_releves.html", releves=releves, mois=mois)

@app.route("/modifier_releve/<int:releve_id>", methods=["GET", "POST"])
def modifier_un_releve(releve_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        # Récupérer les valeurs du formulaire
        indice_ER = request.form.get("indice_ER")
        indice_HC = request.form.get("indice_HC")
        indice_HN = request.form.get("indice_HN")
        indice_HP = request.form.get("indice_HP")
        perte_ER = request.form.get("perte_ER")
        perte_HC = request.form.get("perte_HC")
        perte_HN = request.form.get("perte_HN")
        perte_HP = request.form.get("perte_HP")
        puissance_demandee = request.form.get("puissance_demandee")

        cur.execute("SELECT date FROM releves WHERE releve_id = ?", (releve_id,))
        releve_data = cur.fetchone()
        mois = releve_data['date']

        cur.execute("""
            UPDATE releves SET
                indice_ER = ?, indice_HC = ?, indice_HN = ?, indice_HP = ?,
                perte_ER = ?, perte_HC = ?, perte_HN = ?, perte_HP = ?,
                puissance_demandee = ?
            WHERE releve_id = ?
        """, (
            indice_ER, indice_HC, indice_HN, indice_HP,
            perte_ER, perte_HC, perte_HN, perte_HP,
            puissance_demandee, releve_id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("modifier_releves", mois=mois))

    # GET : afficher le formulaire pré-rempli
    cur.execute("""
        SELECT r.*, c.nom
        FROM releves r
        JOIN contrats c ON c.contrat_id = r.contrat_id
        WHERE r.releve_id = ?
    """, (releve_id,))
    releve = cur.fetchone()
    conn.close()

    if releve is None:
        return "Relevé non trouvé", 404

    return render_template("modifier_un_releve.html", releve=releve)

#@app.route("/hello", methods=["GET", "POST"])
#def hello():
 #   name = request.args.get("name", "world")
  #  Age = request.args.get("age", None)
   # return render_template("hello.html", name=name, age=Age)