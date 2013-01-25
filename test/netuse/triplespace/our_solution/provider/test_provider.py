import unittest
from mock import Mock, patch
from clueseval.clues.versions.management import Version 
from netuse.triplespace.network.discovery.record import DiscoveryRecord
from netuse.triplespace.our_solution.provider.provider import Provider, WPRequestNotifier

class ProviderTestCase(unittest.TestCase):
    
    def setUp(self):
        m = Mock()
        self.provider = Provider(None, m, None)
    
    def test_new_wp_in_the_neighborhood_with_upper_version(self):
        self.provider.last_contribution_to_aggregated_clue = Version(1, 1)
        new_wp_r = DiscoveryRecord("node1")
        new_wp_r.version = Version(3, 1)
        
        self.provider.sent_through_connector = Mock()
        self.provider.sent_through_connector.return_value = True # retry, unsuccessfully send
        self.assertEquals( Provider.UPDATE_TIME, self.provider._new_wp_in_the_neighborhood( new_wp_r, 0) )
        self.assertEquals( 12, self.provider._new_wp_in_the_neighborhood( new_wp_r, 12) )
    
    def test_new_wp_in_the_neighborhood_different_node_retrying(self):
        self.provider.last_contribution_to_aggregated_clue = Version(2, 1)
        new_wp_r = DiscoveryRecord("node1")
        new_wp_r.version = Version(1, 1)
        
        self.provider.sent_through_connector = Mock()
        self.provider.sent_through_connector.return_value = True # retry, unsuccessfully send
        self.assertEquals( Provider.RETRY_ON_FAILURE, self.provider._new_wp_in_the_neighborhood( new_wp_r, 0) )
        self.assertEquals( "node1", self.provider.last_wp_notification.wp_name )
        
        self.provider.sent_through_connector.return_value = False # no need to retry, successfully send
        self.assertEquals( Provider.UPDATE_TIME, self.provider._new_wp_in_the_neighborhood( new_wp_r, 0) )
        self.assertEquals( "node1", self.provider.last_wp_notification.wp_name )
    
    def test_new_wp_in_the_neighborhood_different_last_notification_went_ok(self):
        self.provider.last_contribution_to_aggregated_clue = Version(2, 1)
        new_wp_r = DiscoveryRecord("super_fake_node") # the provider had already sent him a message
        new_wp_r.version = Version(1, 1)
        
        self.provider.sent_through_connector = Mock()
        self.provider.sent_through_connector.return_value = False
        
        self.last_wp_notification = Mock()
        self.last_wp_notification.got_response.return_value = True
        self.last_wp_notification.successfully_sent.return_value = True
        
        self.assertEquals( Provider.UPDATE_TIME, self.provider._new_wp_in_the_neighborhood( new_wp_r, 0) )
        self.assertEquals( Provider.UPDATE_TIME, self.provider._new_wp_in_the_neighborhood( new_wp_r, 13) )
        
    def test_new_wp_in_the_neighborhood_different_last_notification_went_wrong(self):
        self.provider.last_contribution_to_aggregated_clue = Version(2, 1)
        new_wp_r = DiscoveryRecord("super_fake_node") # the provider had already sent him a message
        new_wp_r.version = Version(1, 1)
                
        self.last_wp_notification = Mock()
        self.last_wp_notification.got_response.return_value = True
        self.last_wp_notification.successfully_sent.return_value = False
        
        self.provider.sent_through_connector = Mock()
        self.provider.sent_through_connector.return_value = True # retry
        self.assertEquals( Provider.RETRY_ON_FAILURE, self.provider._new_wp_in_the_neighborhood( new_wp_r, 0) )
        self.provider.sent_through_connector.return_value = False # not retry
        self.assertEquals( Provider.UPDATE_TIME, self.provider._new_wp_in_the_neighborhood( new_wp_r, 13) )
    
    def test_new_wp_in_the_neighborhood_different_response_for_the_last_notification_not_received(self):
        self.provider.last_contribution_to_aggregated_clue = Version(2, 1)
        new_wp_r = DiscoveryRecord("super_fake_node") # the provider had already sent him a message
        new_wp_r.version = Version(1, 1)
                
        self.last_wp_notification = Mock()
        self.last_wp_notification.got_response.return_value = False
        self.provider.sent_through_connector = Mock()
        
        self.assertEquals( Provider.RETRY_ON_FAILURE, self.provider._new_wp_in_the_neighborhood( new_wp_r, 0) )

if __name__ == '__main__':
    unittest.main()