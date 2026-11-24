import unittest
from engine import Investigation
from grammar import parse
from main import next_question, conclusion

class ImprovementTests(unittest.TestCase):
    def test_voice_aliases(self):
        for name in ('violette', 'le professeur violet', 'le professeur violette'):
            self.assertEqual(parse(f'{name} était dans la bibliothèque à 21 h'),
                             'Presence(Violet,Bibliotheque,Heure21)')
        self.assertEqual(parse('le colonel moutarde était dans la cuisine à vingt et une heures'),
                         'Presence(Moutarde,Cuisine,Heure21)')

    def test_question_priority(self):
        c = Investigation()
        c.add('Presence(Violet,Bibliotheque,Heure21)', 'test')
        self.assertEqual(next_question(c,'Bibliotheque',set())[0], 'ArmePresente(Corde,Bibliotheque,Heure21)')
        c.add('ArmePresente(Corde,Bibliotheque,Heure21)', 'test')
        self.assertEqual(next_question(c,'Bibliotheque',set())[0], 'Trace(Violet,Corde)')
        c.add('Trace(Violet,Corde)', 'test')
        self.assertEqual(next_question(c,'Bibliotheque',set())[0], 'Temoin(Violet,Bibliotheque,Heure21)')

    def test_negative(self):
        c = Investigation()
        f = 'Presence(Moutarde,Cuisine,Heure21)'
        c.reject(f)
        self.assertNotEqual(next_question(c,'Cuisine',set())[0], f)
        with self.assertRaises(ValueError): c.add(f,'test')
        with self.assertRaises(ValueError): c.add('Temoin(Moutarde,Cuisine,Heure21)','test')
        self.assertFalse(c.query(f))
        self.assertFalse(Investigation().is_denied(f))

    def test_conflicting_locations(self):
        c = Investigation()
        c.add('Presence(Violet,Bibliotheque,Heure21)','test')
        for f in ('Presence(Violet,Cuisine,Heure21)', 'Temoin(Violet,Cuisine,Heure21)', 'Scene(Cuisine)', 'HeureCrime(Heure8)'):
            with self.assertRaises(ValueError): c.add(f,'test')
        c.add('Presence(Violet,Cuisine,Heure20)','test')
        c.add('ArmePresente(Corde,Bibliotheque,Heure21)','test')
        with self.assertRaises(ValueError): c.add('ArmePresente(Corde,Cuisine,Heure21)','test')

    def test_invalid_fact(self):
        c = Investigation()
        with self.assertRaises(ValueError): c.add('Coupable(Violet,Corde,Bibliotheque,Heure21)','test')
        with self.assertRaises(ValueError): c.add('Presence(Violet,Cuisine,Heure25)','test')

    def test_french_conclusion(self):
        self.assertIn('Le professeur Violet a tué Monsieur Black dans la bibliothèque avec la corde',
                      conclusion(('Violet','Corde','Bibliotheque','Heure21')))
