"""Console interactive Windows/Linux. Exécuter dans un vrai terminal VS Code."""
import argparse
from pathlib import Path
from engine import Investigation, ROOT
from grammar import ROOMS, SUSPECTS, WEAPONS, parse

def key():
    """Lecture directe des flèches et chiffres, sans touche Entrée."""
    import os
    if os.name=='nt':
        import msvcrt
        k=msvcrt.getwch()
        return {'H':'up','P':'down','K':'left','M':'right'}.get(msvcrt.getwch(),'') if k in ('\x00','\xe0') else k.lower()
    import sys, tty, termios
    fd=sys.stdin.fileno(); old=termios.tcgetattr(fd)
    try:
        tty.setraw(fd); k=sys.stdin.read(1)
        if k=='\x1b':
            return {'[A':'up','[B':'down','[C':'right','[D':'left'}.get(sys.stdin.read(2),'')
        return k.lower()
    finally: termios.tcsetattr(fd,termios.TCSADRAIN,old)

def speak(text):
    import pyttsx3
    voice=pyttsx3.init()
    for v in voice.getProperty('voices'):
        if any(x in (v.name+' '+v.id).lower() for x in ('french','français','fr-fr','fr-ca','hortense')):
            voice.setProperty('voice',v.id); break
    voice.say(text); voice.runAndWait()

def listen():
    import speech_recognition as sr
    recognizer=sr.Recognizer()
    with sr.Microphone() as mic:
        print('Parlez maintenant...'); recognizer.adjust_for_ambient_noise(mic,duration=.5)
        audio=recognizer.listen(mic,timeout=8,phrase_time_limit=12)
    return recognizer.recognize_google(audio,language='fr-CA')

# Libellés humains indépendants des constantes logiques.
NAMES = dict(zip(SUSPECTS.values(), ['le colonel Moutarde', 'Mademoiselle Rose',
    'le professeur Violet', 'Madame Pervenche', 'le docteur Olive', 'Madame Leblanc']))
ROOM_NAMES = {v: k for k, v in ROOMS.items()}
WEAPON_NAMES = {v: k for k, v in WEAPONS.items()}

def article(name):
    return ('la ' if name in ('corde', 'matraque', 'clé anglaise', 'cuisine', 'bibliothèque', 'cave') else 'le ') + name

def questions(case, room, asked):
    """Produire les questions candidates; les priorités ne déduisent aucun fait."""
    for (h,) in case.query('HeureCrime(h)'):
        hour = h[5:] + 'h'
        scene = bool(case.query(f'Scene({room})'))
        compatible = {a for (a,) in case.query('Compatible(a)')}
        for p in SUSPECTS.values():
            name = NAMES[p]
            name_de = ('de ' + name[3:] if name.startswith('le ') else 'de ' + name)
            presence = f'Presence({p},{room},{h})'
            known = bool(case.query(presence))
            elsewhere = any(r != room for _,r,_ in case.query(f'Presence({p},r,{h})'))
            if not elsewhere:
                yield 30 if scene else 10, presence, f'{name[0].upper() + name[1:]} se trouvait dans cette pièce à {hour} ?', None
            if known:
                suspect = any(x[0] == p for x in case.query('Suspect(p,a,r,h)'))
                priority = 100 if suspect else 60 if scene else 20
                yield priority+3, f'Temoin({p},{room},{h})', f'Un témoin a-t-il vu {name} ici à {hour} ?', None
                yield priority+2, f'Mobile({p})', f'{name[0].upper() + name[1:]} avait un mobile ?', None
                yield priority+1, f'SansAlibi({p},{h})', f'{name[0].upper() + name[1:]} était sans alibi à {hour} ?', f'Alibi({p},{h})'
                for a in WEAPONS.values():
                    if a in compatible:
                        yield priority+4, f'Trace({p},{a})', f'Une trace {name} a-t-elle été trouvée sur {article(WEAPON_NAMES[a])} ?', None
        for a in WEAPONS.values():
            if any(r != room for _,r,_ in case.query(f'ArmePresente({a},r,{h})')):
                continue
            priority = 90 if scene and a in compatible else 5
            yield priority, f'ArmePresente({a},{room},{h})', f'{article(WEAPON_NAMES[a]).capitalize()} se trouvait ici à {hour} ?', None

def next_question(case, room, asked):
    candidates = [(score, f, question, opposite) for score, f, question, opposite in questions(case, room, asked)
                  if f not in asked and not case.is_denied(f) and not case.query(f)
                  and not (opposite and case.query(opposite))]
    best = max(candidates, key=lambda q: q[0], default=None)
    return best[1:] if best else None

def conclusion(result):
    p,a,r,h = result
    return (f'{NAMES[p][0].upper() + NAMES[p][1:]} a tué Monsieur Black dans {article(ROOM_NAMES[r])} '
            f'avec {article(WEAPON_NAMES[a])} à {h[5:]}h (selon les règles du jeu).')

def show(case):
    for label in ('Acces(p,a,r,h)','Suspect(p,a,r,h)','Disculpe(p,h)','Coupable(p,a,r,h)'):
        print(label, ':', case.query(label))
    result = case.verdict()
    if result:
        print('CONCLUSION :', conclusion(result))
    elif len(case.query('Coupable(p,a,r,h)')) > 1:
        print('Plusieurs conclusions possibles : enquête non résolue.')
    else:
        print('Aucune conclusion unique pour le moment.')

def demo():
    c=Investigation()
    for s in (ROOT/'data/demo.txt').read_text(encoding='utf8').splitlines():
        if s.strip(): print(s,'=>',c.add_sentence(s,'simulation'))
    show(c)

def run():
    c=Investigation(); rooms=list(ROOMS.values()); i=0; asked=set()
    print('DÉTECTIVE IA — Monsieur Black | Rapport initial chargé.')
    for f,ch in c.facts: print(ch, f)
    while True:
        room=rooms[i]; print(f'\nPièce {i+1}/{len(rooms)} : {ROOM_NAMES[room].capitalize()}')
        result = c.verdict()
        q = None if result else next_question(c,room,asked)
        if result: print('Enquête résolue. r : bilan | s : lire la conclusion | n : nouvelle enquête | q : quitter')
        elif not q: print('Aucune question restante dans cette pièce.')
        if q: print('IA :',q[1])
        print('← → ↑ ↓ déplacement | 1 oui | 2 non | t texte | v voix | s parler | r raisonnement | n recommencer | q quitter')
        k=key()
        try:
            if k=='q': break
            if k=='n':
                c=Investigation(); i=0; asked.clear()
                print('Nouvelle enquête. Faits initiaux rechargés.')
                for f,ch in c.facts: print(ch,f)
                continue
            if k in ('left','right','up','down'):
                i={'left':max(0,i-1),'right':min(len(rooms)-1,i+1),'up':0,'down':len(rooms)-1}[k]
            elif k=='s': speak(conclusion(result) if result else q[1] if q else f'Je suis dans {article(ROOM_NAMES[room])}')
            elif k=='r': show(c)
            elif k in ('1','2','t','v'):
                ch={'1':'touche','2':'touche','t':'console','v':'microphone'}[k]
                if k in ('t','v'):
                    sentence=input('Fait ou réponse : ') if k=='t' else listen(); print('Reçu :',sentence)
                    meaning=parse(sentence)
                else: meaning='Oui' if k=='1' else 'Non'
                if meaning in ('Oui','Non'):
                    if not q: raise ValueError('Aucune question en cours.')
                    if meaning=='Oui': print(c.add(q[0],ch))
                    elif q[2]: print(c.add(q[2],ch))
                    else:
                        c.reject(q[0])
                        print('Réponse négative enregistrée; aucun fait positif ajouté.')
                    asked.add(q[0])
                else: print('Fait :',c.add(meaning,ch))
                if c.verdict(): show(c)
        except Exception as e: print('Interaction non enregistrée :',e)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--demo',action='store_true'); args=ap.parse_args()
    demo() if args.demo else run()
