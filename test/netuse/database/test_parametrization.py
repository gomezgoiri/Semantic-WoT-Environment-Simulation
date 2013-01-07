'''
Created on Jan 4, 2012

@author: tulvur
'''

import unittest
import datetime

from testing.utils import connect_to_testing_db
c = connect_to_testing_db()

from netuse.database.parametrization import Parametrization, NetworkModel, ParametrizableNetworkModel
from netuse.network_models import NetworkModelManager


class TestParametrization(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        c.drop_database('tests')
    
    def test_create_default_network_model(self):
        sp = Parametrization()
        for sp in Parametrization.objects:
            self.assertIsNone(p.network_model)
        sp.save()
        
        self.assertEquals(1, len(Parametrization.objects))
        for p in Parametrization.objects:
            net_model = p.network_model
            self.assertIsInstance(net_model, NetworkModel)
            self.assertEquals( NetworkModelManager.normal_netmodel, net_model.type )
    
    def test_create_different_network_model(self):
        nm = ParametrizableNetworkModel(
                    type=NetworkModelManager.dynamic_netmodel,
                    state_change_mean = 10,
                    state_change_std_dev = 5
        )
        # MongoDB forces you to save it. Otherwise it raises the following ValidationError:
        # "You can only reference documents once they have been saved to the database"
        nm.save()
        sp = Parametrization( network_model = nm )
        sp.save()
        
        self.assertEquals(1, len(Parametrization.objects))
        for p in Parametrization.objects:
            net_model = p.network_model
            self.assertIsInstance(net_model, ParametrizableNetworkModel)
            self.assertEquals( NetworkModelManager.dynamic_netmodel, net_model.type )
            self.assertEquals( 10, net_model.state_change_mean )
            self.assertEquals( 5, net_model.state_change_std_dev )
    
    def test_deletion_of_network_model(self):
        nm = ParametrizableNetworkModel(
                    type=NetworkModelManager.chaotic_netmodel,
                    state_change_mean = 15,
                    state_change_std_dev = 20
        )
        nm.save()
        sp = Parametrization( network_model = nm )
        sp.save()
        sp.delete() # should delete also "nm"
        
        self.assertEquals( 0, len(NetworkModel.objects), msg="The created 'NetworkModel' object should not longer exist in the database." ) 


if __name__ == '__main__':
    unittest.main()