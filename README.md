# Optimisation Ligne de Fabrication — Streamlit

Application web pour analyser et optimiser une ligne de fabrication d'arbres mécaniques.

## Lancement

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'application
streamlit run app.py

# 3. (Optionnel) Lancer les tests
pytest tests/ -v
```

L'application s'ouvre sur http://localhost:8501

## Architecture

```
ligne_fab/
├── app.py                       # Streamlit (entrée principale)
├── services/                    # Logique métier (testable sans Streamlit)
│   ├── domain.py                # Dataclasses (Poste, Parametres, ResultatSimulation)
│   ├── calculs.py               # Toutes les formules du PDF
│   ├── scenarios.py             # S1, S2, S3, S4 + économie
│   ├── alertes.py               # Règles d'alerte déclaratives
│   └── excel_loader.py          # Parsing + validation Excel
├── components/
│   └── animation.py             # Animation SVG/JS du flux
├── tests/
│   └── test_calculs.py          # 15 tests, oracle = valeurs du PDF
└── requirements.txt
```

## Utilisation

1. **Télécharger le template Excel** depuis la barre latérale.
2. Remplir le template avec vos données (ou utiliser les données de démo du PDF).
3. **Uploader** le fichier rempli.
4. Naviguer entre les 4 onglets :
   - **Diagnostic** : indicateurs clés, taux d'utilisation, alertes
   - **Animation** : simulation visuelle du flux de production
   - **Scénarios** : comparaison S1/S2/S3/S4
   - **Économie** : ROI, gain annuel

## Validation

Les 15 tests unitaires reproduisent **exactement** les chiffres du PDF :
capacité = 72 pcs/j, TRS = 85.5%, Lead Time = 136 min, S4 = 92 pcs/j conformes.

## Choix techniques

- **Streamlit** plutôt que Django : l'application est un outil de calcul, pas un site
  multi-utilisateurs. Streamlit divise par 5 le code à écrire.
- **Logique séparée du framework** : le dossier `services/` peut tourner sans Streamlit.
  Si demain tu veux refaire un front Django ou React, tout le calcul est réutilisable.
- **Animation SVG/JS custom** dans un composant HTML : seule façon d'avoir un vrai
  flux de pièces animé. Streamlit natif ne fait pas ça.

## Limites connues

- L'animation tourne dans un iframe isolé : changer un slider Streamlit pendant
  l'animation ne la met pas à jour. Il faut relancer.
- Pas de persistance : fermer l'onglet = perdre la simulation.
- Le générateur de pannes est aléatoire : deux runs successifs donnent des nombres
  d'arrêts différents (c'est volontaire — c'est de la simulation).
