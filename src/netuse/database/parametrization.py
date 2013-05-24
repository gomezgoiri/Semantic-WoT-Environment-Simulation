'''
Created on Nov 27, 2011

@author: tulvur
'''
import pickle
from mongoengine import Document, StringField, FloatField, IntField, ListField, ReferenceField, NULLIFY
from netuse.network_models import NetworkModelManager
from netuse.triplespace.network.discovery.discovery import DiscoveryFactory


class NetworkModel(Document):
    meta = {'collection': 'parametrization',
            'allow_inheritance': True }
    
    type = StringField(
                required = True,
                default = NetworkModelManager.normal_netmodel,
                choices = ( NetworkModelManager.normal_netmodel,
                            NetworkModelManager.dynamic_netmodel,
                            NetworkModelManager.onedown_netmodel,
                            NetworkModelManager.chaotic_netmodel, )
            )


class ParametrizableNetworkModel(NetworkModel):
    state_change_mean = IntField(required=True, default=5000)
    state_change_std_dev = IntField(required=True, default=3000)


class Parametrization(Document):
    meta = { 'collection': 'parametrization',
             'cascade': True } # to save the 1:1 network model associated with the parametrization
    
    # valid strategies
    negative_broadcasting = "negative broadcasting"
    negative_broadcasting_caching = "negative broadcasting caching"
    centralized = "centralized"
    our_solution = "our"
    
    # To reference a document that has not yet been defined, use the name of the undefined document as the constructor's argument.
    network_model = ReferenceField(NetworkModel, reverse_delete_rule=NULLIFY) # TODO give a default value
    discovery = StringField( required = True,
                                      default = DiscoveryFactory.SIMPLE_DISCOVERY,
                                      choices = ( DiscoveryFactory.SIMPLE_DISCOVERY,
                                                  DiscoveryFactory.MDNS_DISCOVERY, )
                                     )
    strategy = StringField( required = True,
                            default = negative_broadcasting )
                           #don't know why stopped working :-S
                           #choices=(negative_broadcasting, centralized, our_solution,))
    simulateUntil = FloatField(required=True, default=60000.0)
    nodes = ListField(StringField(), required=True, default=[""])
    nodeTypes = ListField(StringField(), required=True, default=[""])
    amountOfQueries = IntField(required=True, default=0)
    numConsumers = IntField(required=True, default=0)
    writeFrequency = IntField(required=True, default=100)
    
    _queries = StringField(required=True, default=pickle.dumps([('*', '*', '*'),]))
    #queries = property(getQueries, setQueries, None, "queries!")
    
    @property
    def queries(self):
        return pickle.loads( str(self._queries) )
    
    @queries.setter
    def queries(self, queries):
        self._queries = pickle.dumps( queries )
    
    @queries.deleter
    def queries(self):
        del self._queries
            
    @property
    def numberOfNodes(self):
        return len(self.nodes)
    
    def __repr__(self):
        return 'Parametrization(strat: %s, nodes: %i, write_freq: %i, #queries: %i)'%(self.strategy, len(self.nodes), self.writeFrequency, self.amountOfQueries)
    
    def __str__(self):
        return self.__repr__()
    
    def save(self, *args, **kwargs):
        if self.network_model is None:
            self.network_model = NetworkModel()
            self.network_model.save(*args, **kwargs)

        super(Parametrization, self).save(*args, **kwargs)
        
    def delete(self, safe=False):
        self.network_model.delete(safe)
        super(Parametrization, self).delete(safe)