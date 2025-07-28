from flask import Flask, render_template, make_response
import pdfkit

app = Flask(__name__)

@app.route('/')
def generate_pdf():
    donnees = {
        'ICE_client':0,
        'N_facture':0,
        'net_a_payer':0,
        'secteur':0,
        'N_abonne':0,
        'N_contrat':0,
        'date_contrat':'8/1994',
        'code_pro':0,
        'matricule_poste':0,
        'date_quittancement':'5/2025'
    }
    # Rendre le template HTML
    rendered = render_template('input-html.html')#,**donnees)
    # Configuration pour PDFKit
    options = {
        'enable-local-file-access': '',
        'encoding': 'UTF-8',
        'page-size': 'A4',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm'
    }
    # Générer le PDF
    pdf = pdfkit.from_string(rendered, False, options=options)
    
    # Créer la réponse
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=facture.pdf'
    
    return response

if __name__ == '__main__':
    app.run(debug=True)