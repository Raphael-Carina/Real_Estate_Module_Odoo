from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged
from odoo import Command
import logging

_logger = logging.getLogger(__name__)

"""
Fonctionnement des tests :
__________________________

setUpClass() :
C'est une méthode lancée une fois par classe de test.
C'est à dire que pour une classe donnée, elle s'exécute une fois avant tous les tests, c'est tout.
Les données qu'elle crée sont partagées par tous les tests de la classe.
Chaque test s'exécute ensuite dans un savepoint, annulé (rollback) à la fin du test.
Chaque test repart donc des données de setUpClass(), sans les modifications des tests précédents.
A la fin de la classe, toute la transaction est annulée.

setUp() :
C'est une méthode lancée avant chaque test.

tearDown() :
C'est une méthode lancée après chaque test.

Exemple :
_________

setUpClass()        ← 1 fois pour la classe
  setUp()           ← avant test_1
  test_1()
  tearDown()        ← après test_1 (puis rollback du savepoint)
  setUp()           ← avant test_2
  test_2()
  tearDown()
tearDownClass()     ← 1 fois, puis rollback de la transaction
"""

"""
Les tags :
__________

Il existe plusieurs tags existants qui permettent de définir le moment d'exécution des tests.
ATTENTION : les tags s'appliquent à la classe de test, pas aux méthodes directement!

- standard
Par défaut, TOUS les tests ont le tag 'standard'. Pour le retirer, il faut indiquer '-standard',
alors le test ne se lancera que si on l'appelle explicitement.

- at_install
Par défaut, TOUS les tests ont ce tag 'at_install'. Il signifie que le test s'exécutera juste après
l'installation/mise à jour de SON module. Les dépendances sont déjà installées car les dépendances d'un
module s'installe avant le module lui-même, mais les modules qui dépendraient de CE module ne sont pas
encore installés/mis à jour.

- post_install
Avec ce tag, les tests s'exécutent après l'installation/mise à jour de TOUS les modules.
C'est utile quand les tests dépendent de module installés après le notre, ou pour les tests d'interface HttpCase.
Comme at_install est appliqué par défaut, il est nécessaire de le retirer pour passer en post_install.

- tags personnalisés
Il est tout à fait possible de créer ses propres tags afin de pouvoir regrouper ses classes de tests.
"""

"""
Lancement des tests :
_____________________

Il y a plusieurs façon de cibler les tests à exécuter :

1) --test-enable
Lance tous les tests ayant le tag 'standard' des modules que l'on installe ou met à jour.

2) --test-file
Permet de cibler un fichier de tests précis.
Par exemple :

docker-compose exec od odoo -d real_restate --test-file=/mnt/extra-addons/estate/tests/test_correctly_sold.py --http-port 8888

3) --test-tags
Permet de cibler finement les tests à exécuter, soit en fonction du tag, soit du module, soit de la classe, soit de la méthode (du test lui-même).
C'est cette façon de faire qui est a privilégier.
Il est à utiliser avec la syntaxe suivante : tag/module:Classe.methode , dans laquelle chaque partie est optionnelle.
Exemples :

- Lance uniquement les tests des classes taggée 'estate'
docker-compose exec od odoo -d real_estate --test-tags estate_tag --http-port 8888

- Lance uniquement les tests du module estate :
docker-compose exec od odoo -d real_estate --test-tags estate --http-port 8888

- Lance uniquement les tests du module estate taggés 'estate_tag' :
docker-compose exec od odoo -d real_estate --test-tags estate_tag/estate --http-port 8888

- Lance uniquement les tests de la classe EstatePropertyTests du module estate :
docker-compose exec od odoo -d real_estate --test-tags estate:EstatePropertyTests --http-port 8888

- Lance uniquement le test 'test_property_with_not_accepted_offer_cant_be_sold' de la classe EstatePropertyTests du module estate :
docker-compose exec od odoo -d real_estate --test-tags estate:EstatePropertyTests.test_property_with_not_accepted_offer_cant_be_sold --http-port 8888
"""

@tagged('estate_tag', 'post_install', '-at_install')
class EstatePropertyTests(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """
        Cette méthode est appelée avant l'exécution des tests.
        On y crée les données dont on aura besoin pour nos tests.
        """

        super().setUpClass()

        # On crée un recorset d'annonces
        cls.properties = cls.env['estate.property'].create([

            # Annonce 1
            {
                'name': 'Test 1',
                'expected_price': 100000.0,
                'state': 'new',
            },

            # Annonce 2
            {
                'name': 'Test 2',
                'expected_price': 100000.0,
                'state':'new',
                'offers_ids': [Command.create(
                    {
                        'price': 99999.0,
                        'status': 'accepted',
                        'partner_id': cls.env.ref('base.res_partner_2').id, # 'Acme Corporation' du module base
                    })
                ]
            },

            # Annonce 3
            {
                'name': 'Test 3',
                'expected_price': 100000.0,
                'state': 'sold',
            }

        ])

        _logger.info('Test property created successfully with id: %s', cls.properties.ids)

    def test_property_with_not_accepted_offer_cant_be_sold(self):
        """
        Test qu'une propriété sans offre acceptée ne puisse pas être vendue.
        """
        with self.assertRaises(UserError):
            self.properties[0].action_sold()

    def test_property_with_accepted_offer_can_be_sold(self):
        """
        Test qu'une propriété avec une annonce acceptée liée puisse être vendue.
        """
        self.assertEqual(self.properties[1].action_sold(), True)

    def test_offer_creation_on_solded_property(self):
        """
        Test qu'on ne puisse pas créer d'offre sur une propriété vendue.
        """
        offer_vals = {
            'price' : 100000.0,
            'partner_id': self.env.ref('base.res_partner_2').id,
            'property_id': self.properties[2].id
        }

        with self.assertRaises(ValidationError):
            self.env['estate.property.offers'].create(offer_vals)


    """
    Utilisation de odoo.tests.Form :
    ________________________________

    Form permet de simuler ce que fait le client web sur une vue formulaire, mais en Python, sans navigateur.
    Il permet :
    - de déclencher les onchanges à chaque affectation, comme quand l'utilisateur modifie un champ.
    - de respecter la vue : unn champ readonly ou invisible ne peut pas être modifié, et les champs required sont vérifiés à l'enregistrement.

    On enregistre un enregistrement à la sortie du with ou en appelant .save() .

    On a donc deux façons d’obtenir l’enregistrement :

    - avec with : lire f.record après le bloc.
    - sans with : récupérer ce que renvoie save(), avec record = f.save() .
    """

    def test_reset_garden_values_when_uncheck_garden_box(self):
        """
        Test du onchange '_onchange_garden' des propriétés.
        """
        # On émule une vue Form d'annonce pour créer une annonce et lui indiquer un jardin.
        with Form(self.env['estate.property']) as p:
            p.name = 'Test garden values'
            p.expected_price = 100000
            p.garden = True

        # On récupère l'enregistrement crée.
        record = p.record

        # Vérification que les valeurs par défaut sont respectées.
        self.assertEqual(record.garden_area, 10)
        self.assertEqual(record.garden_orientation, 'north')

        # On ré-ouvre la vue Form de l'enregistrement pour lui décocher le jardin.
        with Form(record) as p:
            p.garden = False

        # Vérification que les valeurs pour le jardin soient bien reset.
        self.assertEqual(record.garden_area, 0)
        self.assertFalse(record.garden_orientation)
