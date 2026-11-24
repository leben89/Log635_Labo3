# LOG635 — Laboratoire 3

## Installation Windows / VS Code
Ouvrir le dossier extrait dans VS Code. Dans PowerShell :

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py --demo
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe main.py
```
Python 3.11 recommandé (non testé ici sous Windows). Sélectionner `.venv\Scripts\python.exe` dans VS Code. Aucun téléchargement de corpus NLTK nécessaire. Google Speech Recognition requiert Internet et transmet l'audio au service Google. Autoriser le microphone et installer une voix française Windows si nécessaire. En cas d'échec audio, vérifier les périphériques et PyAudio; le mode texte reste disponible.

## Démonstration à filmer
1. Lancer `main.py` (pas --demo). Montrer les trois faits chargés du fichier initial.
2. Dans Cuisine, presser 1 pour confirmer Moutarde à 21h (première question). Presser 2 pour le témoin suivant si souhaité.
3. Presser droite trois fois pour Bibliotheque. Presser s pour entendre la question. Presser v et dire « Violet était dans la bibliothèque à vingt et une heures » (si transcription en chiffres non obtenue, dire « 21 heures » et vérifier le texte; la grammaire exige des chiffres).
4. Presser t et saisir successivement les autres phrases de data/demo.txt (une à la fois), sauf les faits déjà donnés. L'ordre peut varier. Pour une démonstration courte, commencer par les faits concernant les autres pièces, puis la corde, le témoin, la trace, le mobile et l'absence d'alibi de Violet. Presser r pour afficher les inférences.
5. Montrer le verdict et expliquer les règles de Horn. Presser q pour quitter.

Le mode --demo est une simulation de faits, pas une validation du microphone ni des touches physiques. Les réponses négatives ordinaires ne sont pas assimilées à des preuves positives; la question sur l'absence d'alibi a une alternative explicite. Le verdict n'est valable que dans le monde fictif et selon les hypothèses du jeu.

## Organisation
- main.py : console, touches, questions et audio
- grammar.py : grammaire NLTK à traits et lexique
- engine.py : moteur AIMA FolKB
- data/rules.txt : règles de Horn; initial.txt : faits de départ; demo.txt : scénario de simulation
- tests : tests automatisés et résultat réel
- aima : bibliothèque fournie avec le cours; grammars et notebook : exemples d'origine
