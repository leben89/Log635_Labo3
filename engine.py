"""Base de connaissances et requêtes AIMA; aucune identité codée en dur."""
from pathlib import Path
from aima.logic import FolKB, expr
from grammar import parse, SUSPECTS, ROOMS, WEAPONS
ROOT = Path(__file__).resolve().parent

class Investigation:
    def __init__(self, initial=True):
        self.kb = FolKB()
        self.facts = []
        self.denied = set()  # réponses négatives explicites, distinctes des faits inconnus
        for line in (ROOT/'data/rules.txt').read_text(encoding='utf8').splitlines():
            if line.strip() and not line.startswith('#'):
                self.kb.tell(expr(line))
        if initial:
            for line in (ROOT/'data/initial.txt').read_text(encoding='utf8').splitlines():
                if line.strip() and not line.startswith('#'):
                    self.add_sentence(line,'fichier')

    def add_sentence(self, sentence, channel='console'):
        return self.add(parse(sentence),channel)

    def add(self, fact, channel):
        e = expr(fact)
        # Seuls les faits élémentaires bien typés sont acceptés en entrée.
        people, rooms, weapons = map(lambda d: set(d.values()), (SUSPECTS, ROOMS, WEAPONS))
        hours = {f'Heure{i}' for i in range(24)}
        signatures = {'Presence': (people, rooms, hours),
                      'ArmePresente': (weapons, rooms, hours),
                      'Temoin': (people, rooms, hours), 'Trace': (people, weapons),
                      'Mobile': (people,), 'Alibi': (people, hours),
                      'SansAlibi': (people, hours), 'Scene': (rooms,),
                      'HeureCrime': (hours,), 'Compatible': (weapons,)}
        signature = signatures.get(e.op)
        if signature is None or len(e.args) != len(signature) or any(
                str(arg) not in domain for arg, domain in zip(e.args, signature)):
            raise ValueError('Fait non autorisé ou mal formé.')
        if str(e) in self.denied:
            raise ValueError('Ce fait contredit une réponse négative antérieure.')
        if e.op in ('Alibi', 'SansAlibi'):
            other = 'SansAlibi' if e.op == 'Alibi' else 'Alibi'
            if self.query(f'{other}({e.args[0]},{e.args[1]})'):
                raise ValueError('Alibi contradictoire.')
        # Hypothèse du jeu : une personne ou une arme ne peut être dans
        # deux pièces au même instant; un seul lieu et une seule heure du crime.
        for old, _ in self.facts:
            prior = expr(old)
            if prior.op != e.op:
                continue
            if e.op in ('Presence', 'ArmePresente', 'Temoin') and (
                    prior.args[0] == e.args[0] and prior.args[2] == e.args[2]
                    and prior.args[1] != e.args[1]):
                raise ValueError('Localisation contradictoire au même instant.')
            if e.op in ('Scene', 'HeureCrime') and prior != e:
                raise ValueError('Rapport initial contradictoire.')
        if e.op in ('Presence', 'Temoin'):
            other = 'Temoin' if e.op == 'Presence' else 'Presence'
            for old, _ in self.facts:
                prior = expr(old)
                if (prior.op == other and prior.args[0] == e.args[0]
                        and prior.args[2] == e.args[2] and prior.args[1] != e.args[1]):
                    raise ValueError('Le témoignage contredit la localisation connue.')
            if e.op == 'Temoin' and str(expr(f'Presence({e.args[0]},{e.args[1]},{e.args[2]})')) in self.denied:
                raise ValueError('Le témoignage contredit une absence déclarée.')
        if e not in self.kb.clauses:
            self.kb.tell(e)
            self.facts.append((str(e),channel))
        return str(e)

    def reject(self, fact):
        """Mémoriser une réponse non sans utiliser une négation par défaut."""
        if self.query(fact):
            raise ValueError('La réponse contredit un fait connu.')
        e = expr(fact)
        if e.op == 'Presence' and self.query(f'Temoin({e.args[0]},{e.args[1]},{e.args[2]})'):
            raise ValueError('La réponse contredit un témoignage connu.')
        self.denied.add(str(e))

    def is_denied(self, fact):
        return str(expr(fact)) in self.denied

    def query(self, predicate):
        q=expr(predicate)
        return sorted(set(tuple(str(s.get(v,v)) for v in q.args) for s in self.kb.ask_generator(q)))

    def verdict(self):
        results=self.query('Coupable(p,a,r,h)')
        return results[0] if len(results)==1 else None
