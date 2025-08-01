from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm



def create_invoice():
    # Create document
    doc = SimpleDocTemplate("facture.pdf", pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    
    # 1. En-tête avec les informations de l'entreprise
    company_info = [
        ["Nom de l'entreprise", "", "", ""],
        ["Adresse", "", "", ""],
        ["Téléphone", "Email", "SIRET", "TVA Intra"]
    ]
    
    company_table = Table(company_info, colWidths=[5*cm, 5*cm, 5*cm, 5*cm])
    company_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('SPAN', (1,0), (3,0)),
        ('SPAN', (1,1), (3,1)),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # 2. Titre de la facture
    elements.append(Paragraph("FACTURE", title_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # 3. Première ligne avec 2 tableaux
    # Tableau 1: 4 colonnes, 2 lignes
    table1_data = [
        ["Col1", "Col2", "Col3", "Col4"],
        ["", "", "", ""]
    ]
    
    # Tableau 2: 1 cellule (à droite du tableau 1)
    table2_data = [
        ["Cellule unique"]
    ]
    
    # Créer une ligne avec les 2 tableaux côte à côte
    combined_table = Table([
        [Table(table1_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm]), 
         Table(table2_data, colWidths=[6*cm])]
    ], colWidths=[12*cm, 6*cm])
    
    combined_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(combined_table)
    
    # 4. Deuxième ligne avec 2 tableaux
    # Tableau 3: 3 colonnes, 2 lignes (en bas du tableau 1)
    table3_data = [
        ["Col1", "Col2", "Col3"],
        ["", "", ""]
    ]
    
    # Tableau 4: 1 ligne, 2 colonnes
    table4_data = [
        ["Cell1", "Cell2"]
    ]
    
    # Créer une ligne avec les 2 tableaux côte à côte
    combined_table2 = Table([
        [Table(table3_data, colWidths=[4*cm, 4*cm, 4*cm]), 
         Table(table4_data, colWidths=[6*cm, 6*cm])]
    ], colWidths=[12*cm, 6*cm])
    
    combined_table2.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(combined_table2)
    elements.append(Spacer(1, 0.5*cm))
    
    # 5. Tableau de 2 colonnes et 1 ligne
    table5_data = [
        ["Colonne 1", "Colonne 2"]
    ]
    
    table5 = Table(table5_data, colWidths=[9*cm, 9*cm])
    table5.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table5)
    elements.append(Spacer(1, 0.5*cm))
    
    # 6. Deux tableaux horizontaux
    # Tableau 6: 4 colonnes, 2 lignes (à gauche)
    table6_data = [
        ["Col1", "Col2", "Col3", "Col4"],
        ["", "", "", ""]
    ]
    
    # Tableau 7: 3 lignes, 3 colonnes (à droite)
    table7_data = [
        ["Col1", "Col2", "Col3"],
        ["", "", ""],
        ["", "", ""]
    ]
    
    # Combiner les deux tableaux horizontalement
    combined_table3 = Table([
        [Table(table6_data, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm]), 
         Table(table7_data, colWidths=[6*cm, 6*cm, 6*cm])]
    ], colWidths=[18*cm, 18*cm])
    
    combined_table3.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(combined_table3)
    elements.append(Spacer(1, 0.5*cm))
    
    # 7. Grand tableau de 8 colonnes et 5 lignes
    table8_data = [
        ["Col1", "Col2", "Col3", "Col4", "Col5", "Col6", "Col7", "Col8"],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""]
    ]
    
    table8 = Table(table8_data, colWidths=[2.25*cm]*8)
    table8.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table8)
    elements.append(Spacer(1, 0.5*cm))
    
    # 8. Deux tableaux en dessous
    # Tableau 9: 4 colonnes et 2 lignes
    table9_data = [
        ["Col1", "Col2", "Col3", "Col4"],
        ["", "", "", ""]
    ]
    
    # Tableau 10: 1 ligne et 2 colonnes
    table10_data = [
        ["Cell1", "Cell2"]
    ]
    
    # Combiner les deux tableaux horizontalement
    combined_table4 = Table([
        [Table(table9_data, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm]), 
         Table(table10_data, colWidths=[9*cm, 9*cm])]
    ], colWidths=[18*cm, 18*cm])
    
    combined_table4.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(combined_table4)
    elements.append(Spacer(1, 0.5*cm))
    
    # 9. Grand tableau de 11 lignes et 5 colonnes
    table11_data = [
        ["Col1", "Col2", "Col3", "Col4", "Col5"],
        *[[""]*5 for _ in range(10)]  # 10 lignes vides
    ]
    
    table11 = Table(table11_data, colWidths=[3.6*cm]*5)
    table11.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table11)
    elements.append(Spacer(1, 1*cm))
    
    # 10. Espace pour la signature
    signature_line = Table([["Signature : _________________________"]], colWidths=[18*cm])
    elements.append(signature_line)
    
    # Build PDF
    doc.build(elements)

create_invoice()