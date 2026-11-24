"""Grammaire à traits NLTK : la sémantique est construite pendant l'analyse."""
import re
from pathlib import Path
from nltk import grammar, FeatureChartParser

SUSPECTS = dict(zip(['moutarde','rose','violet','pervenche','olive','leblanc'], ['Moutarde','Rose','Violet','Pervenche','Olive','Leblanc']))
ROOMS = dict(zip(['cuisine','salon','bureau','bibliothèque','hall','cave'], ['Cuisine','Salon','Bureau','Bibliotheque','Hall','Cave']))
WEAPONS = dict(zip(['corde','poignard','revolver','chandelier','matraque','clé anglaise'], ['Corde','Poignard','Revolver','Chandelier','Matraque','CleAnglaise']))

def lex(category, entries):
    return '\n'.join(f'{category}[SEM=<{value}>] -> ' + ' '.join(repr(w) for w in key.split()) for key,value in entries.items())

def source():
    return '''% start S
S[SEM=<Presence(?p,?r,?h)>] -> Person[SEM=?p] Verb PP[SEM=?r] Time[SEM=?h]
S[SEM=<ArmePresente(?a,?r,?h)>] -> Det Weapon[SEM=?a] Verb PP[SEM=?r] Time[SEM=?h]
S[SEM=<Scene(?r)>] -> Victime 'a' 'été' 'trouvé' PP[SEM=?r]
S[SEM=<HeureCrime(?h)>] -> Victime 'est' 'mort' Time[SEM=?h]
S[SEM=<Compatible(?a)>] -> 'le' 'rapport' 'désigne' Det Weapon[SEM=?a]
S[SEM=<Trace(?p,?a)>] -> 'une' 'trace' 'de' Person[SEM=?p] 'est' 'sur' Det Weapon[SEM=?a]
S[SEM=<Mobile(?p)>] -> Person[SEM=?p] 'avait' 'un' 'mobile'
S[SEM=<Alibi(?p,?h)>] -> Person[SEM=?p] 'avait' 'un' 'alibi' Time[SEM=?h]
S[SEM=<SansAlibi(?p,?h)>] -> Person[SEM=?p] 'n' 'avait' 'pas' 'd' 'alibi' Time[SEM=?h]
S[SEM=<Temoin(?p,?r,?h)>] -> 'un' 'témoin' 'a' 'vu' Person[SEM=?p] PP[SEM=?r] Time[SEM=?h]
S[SEM=<Oui>] -> 'oui'
S[SEM=<Non>] -> 'non'
Person[SEM=?p] -> Name[SEM=?p] | Title Name[SEM=?p]
Title -> 'colonel' | 'madame' | 'professeur' | 'docteur' | 'mademoiselle'
Victime -> 'monsieur' 'black'
Verb -> 'était' | 'est' | 'se' 'trouvait'
PP[SEM=?r] -> 'dans' Det Room[SEM=?r]
Time[SEM=?h] -> 'à' Hour[SEM=?h]
Det -> 'le' | 'la' | 'un' | 'une'
''' + '\n' + '\n'.join([lex('Name',SUSPECTS),lex('Room',ROOMS),lex('Weapon',WEAPONS),lex('Hour',{f'{i}h':f'Heure{i}' for i in range(24)})])

PARSER = FeatureChartParser(grammar.FeatureGrammar.fromstring((Path(__file__).resolve().parent / "data/francais.fcfg").read_text(encoding="utf8")))

def parse(sentence):
    sentence = sentence.lower().replace('’', "'")
    # Normaliser uniquement les noms et titres connus du jeu.
    aliases = {
        'violet': r'(?:(?:le\s+)?professeur\s+)?(?:violet|violette)',
        'moutarde': r'(?:(?:le\s+)?colonel\s+)?moutarde',
        'rose': r'(?:mademoiselle|mlle)\s+rose',
        'pervenche': r'(?:madame|mme)\s+pervenche',
        'olive': r'(?:le\s+)?docteur\s+olive',
        'leblanc': r'(?:madame|mme)\s+leblanc',
    }
    for name, pattern in aliases.items():
        sentence = re.sub(r'\b' + pattern + r'\b', name, sentence)
    sentence = re.sub(r'\b(\d{1,2})\s*(?:heures?|h)(?:\s*00)?\b',lambda m:f'{int(m[1])}h',sentence)
    sentence = re.sub(r'\bvingt et une heures?\b', '21h', sentence)
    tokens = re.findall(r'[\w]+',sentence)
    try:
        meanings = {str(t.label()['SEM']) for t in PARSER.parse(tokens)}
    except ValueError:
        meanings = set()
    if len(meanings)!=1:
        raise ValueError('Phrase inconnue ou ambiguë : '+sentence)
    return meanings.pop()
