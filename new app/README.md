# Bulletin de Paie - Application Flask

Une application web Flask pour calculer les bulletins de paie et gérer les profils d'employés.

## Fonctionnalités

- Gestion des profils utilisateur avec salaire horaire et primes
- Calculateur de salaire complet (heures normales, supplémentaires, congés, etc.)
- Calcul automatisé des cotisations sociales et impôts
- Historique des calculs
- Export PDF des bulletins
- Interface utilisateur moderne et responsive avec Bootstrap 5

## Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)

## Installation

1. Clonez le dépôt:
```bash
git clone https://github.com/votre-nom/bulletin-de-paie.git
cd bulletin-de-paie
```

2. Créez un environnement virtuel:
```bash
python -m venv venv
```

3. Activez l'environnement virtuel:
   - Sous Windows:
   ```bash
   venv\Scripts\activate
   ```
   - Sous Linux/MacOS:
   ```bash
   source venv/bin/activate
   ```

4. Installez les dépendances:
```bash
pip install -r requirements.txt
```

5. Initialisez la base de données:
```bash
flask init-db
```

## Utilisation

1. Lancez l'application:
```bash
python run.py
```

2. Ouvrez votre navigateur et accédez à:
```
http://localhost:5000
```

3. Créez un compte utilisateur et connectez-vous.

4. Créez des profils d'employés avec leurs taux horaires et primes.

5. Utilisez le calculateur pour générer des bulletins de paie.

## Structure de l'application

L'application suit une architecture modulaire avec des blueprints Flask:

- `app/`: Package principal de l'application
  - `__init__.py`: Factory pattern pour créer l'application Flask
  - `models.py`: Modèles de données SQLAlchemy
  - `utils.py`: Fonctions utilitaires pour les calculs
  - `pdf_generator.py`: Générateur de PDF pour les bulletins
  - `config.py`: Configuration de l'application
  - `auth/`: Blueprint d'authentification
  - `main/`: Blueprint principal
  - `profiles/`: Blueprint pour la gestion des profils
  - `calculator/`: Blueprint pour le calculateur de salaire
  - `history/`: Blueprint pour l'historique des calculs
  - `templates/`: Templates Jinja2
  - `static/`: Fichiers statiques (CSS, JS, images)

## Commandes CLI

L'application fournit des commandes utiles pour l'administration:

- Initialiser la base de données:
```bash
flask init-db
```

- Réinitialiser la base de données:
```bash
flask reset-db
```

- Créer un utilisateur administrateur:
```bash
flask create-admin <username> <email> <password>
```

## Licence

Ce projet est sous licence [MIT](LICENSE).

## Contact

Pour toute question ou suggestion, veuillez ouvrir une issue sur ce dépôt GitHub. 