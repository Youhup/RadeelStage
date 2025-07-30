// Charge la config au chargement de la page
document.addEventListener('DOMContentLoaded', async () => {
    const response = await fetch('/parametre/afficher');
    const config = await response.json();
    
    // Remplit le formulaire avec les valeurs actuelles
    document.getElementById('tauxTVA').value = config.TAUX_TVA || 0.20;
    document.getElementById('fraisDossier').value = config.FRAIS_DOSSIER || 50.0;
});

// Envoie les modifications au backend
document.getElementById('configForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const newConfig = {
        TAUX_TVA: parseFloat(document.getElementById('tauxTVA').value),
        FRAIS_DOSSIER: parseFloat(document.getElementById('fraisDossier').value)
    };
    
    const response = await fetch('/parametre/modifier', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig)
    });
    
    const result = await response.json();
    if (result.success) {
        alert('Paramètres mis à jour !');
    } else {
        alert('Erreur: ' + (result.error || 'Échec de la mise à jour'));
    }
});