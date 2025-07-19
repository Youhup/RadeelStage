# app/parametres.py
import os
import json
from typing import Any

class ParametresSysteme:
    _defaults = {
        'tarif_pleine': 0.95,
        'tarif_creuse': 0.55,
        'tva': 0.10,
        'taxe_fixe': 15.00
    }

    def __init__(self, app=None):
        self._parametres = self._defaults.copy()
        self.app = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialisation avec l'application Flask"""
        self.app = app
        app.parametres_systeme = self
        self.charger_config()
        app.logger.info("Paramètres système initialisés")

    def charger_config(self):
        """Charge la configuration depuis instance/config.json"""
        try:
            config_path = os.path.join(self.app.instance_path, 'config.json')
            with open(config_path) as f:
                config = json.load(f)
                for k, v in config.items():
                    if k in self._parametres:
                        self._parametres[k] = self._convertir_type(k, v)
        except FileNotFoundError:
            if self.app:
                self.app.logger.warning("Config.json non trouvé, valeurs par défaut utilisées")

    def _convertir_type(self, nom: str, valeur: Any) -> Any:
        """Convertit la valeur vers le type original"""
        try:
            return type(self._defaults[nom])(valeur)
        except (ValueError, TypeError) as e:
            if self.app:
                self.app.logger.error(f"Erreur conversion paramètre {nom}: {e}")
            raise

    def get(self, nom: str) -> Any:
        if nom not in self._parametres:
            raise KeyError(f"Paramètre inconnu: {nom}")
        return self._parametres[nom]

    def set(self, nom: str, valeur: Any, persist: bool = False):
        if nom not in self._parametres:
            raise KeyError(f"Paramètre inconnu: {nom}")
        
        self._parametres[nom] = self._convertir_type(nom, valeur)
        
        if persist and self.app:
            self._sauvegarder_config()

    def _sauvegarder_config(self):
        """Sauvegarde dans instance/config.json"""
        config_path = os.path.join(self.app.instance_path, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(self._parametres, f, indent=2)
        self.app.logger.info("Configuration sauvegardée")