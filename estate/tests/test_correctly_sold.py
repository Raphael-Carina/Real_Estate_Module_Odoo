from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tests import tagged
import logging

_logger = logging.getLogger(__name__)

class EstateTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """
        Cette méthode est appelée avant l'exécution des tests.
        On y crée les données dont on aura besoin pour nos tests.
        """

        super().setUpClass()
        cls.test_property = cls.env['estate.property'].create({'name': 'Test Property','expected_price': 100000.0,'state': 'new'})

        _logger.info('Test property created successfully with id: %s', cls.test_property.id)

    def test_property_sold_state(self):
        """
        Test que le state de l'annonce passe bien sur sold lorsqu'on clique sur le bouton SOLD
        """

        _logger.info('Testing property sale state change...')
        initial_state = self.test_property.state
        _logger.info('Initial state: %s', initial_state)

        # Appel de l'action action_sold() -> simulation du clic sur SOLD
        self.test_property.action_sold()
        _logger.info('action_sold() called')

        # Vérification que le state ait bien été mis à jour
        self.assertEqual(self.test_property.state, 'sold', "The property state should be 'sold' after clicking ond SOLD button !")
        _logger.info('Final state: %s', self.test_property.state)
        _logger.info('Test property_sold_state completed successfully')