import unittest
from engine import Investigation, ROOT
from grammar import parse
from main import next_question

class LabTests(unittest.TestCase):
    def test_hours(self):
        for h in range(24): self.assertEqual(parse(f'Rose était dans le salon à {h}h'),f'Presence(Rose,Salon,Heure{h})')
    def test_invalid(self):
        with self.assertRaises(ValueError): parse('Rose vole dans le ciel')
    def test_demo(self):
        c=Investigation()
        self.assertIsNone(c.verdict())
        for s in (ROOT/'data/demo.txt').read_text(encoding='utf8').splitlines(): c.add_sentence(s)
        self.assertEqual(c.verdict(),('Violet','Corde','Bibliotheque','Heure21'))
    def test_alternative(self):
        c=Investigation(False)
        for f in ['Scene(Cuisine)','HeureCrime(Heure8)','Compatible(Poignard)','Presence(Rose,Cuisine,Heure8)','ArmePresente(Poignard,Cuisine,Heure8)','Trace(Rose,Poignard)','Temoin(Rose,Cuisine,Heure8)','Mobile(Rose)']: c.add(f,'test')
        self.assertIsNone(c.verdict())
        c.add('SansAlibi(Rose,Heure8)','test')
        self.assertEqual(c.verdict(),('Rose','Poignard','Cuisine','Heure8'))
        with self.assertRaises(ValueError): c.add('Alibi(Rose,Heure8)','test')
    def test_question(self):
        c=Investigation(); q=next_question(c,'Cuisine',set()); self.assertEqual(q[0],'Presence(Moutarde,Cuisine,Heure21)')
        c.add(q[0],'touche'); self.assertNotEqual(next_question(c,'Cuisine',set())[0],q[0])
    def test_multiple(self):
        c=Investigation()
        for p in ['Rose','Violet']:
            for f in [f'Presence({p},Bibliotheque,Heure21)',f'Trace({p},Corde)',f'Temoin({p},Bibliotheque,Heure21)',f'Mobile({p})',f'SansAlibi({p},Heure21)']: c.add(f,'test')
        c.add('ArmePresente(Corde,Bibliotheque,Heure21)','test'); self.assertIsNone(c.verdict())
if __name__=='__main__': unittest.main()
