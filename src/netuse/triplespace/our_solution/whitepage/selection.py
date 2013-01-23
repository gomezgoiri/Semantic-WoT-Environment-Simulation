import weakref
from numpy import mean, std
from abc import ABCMeta, abstractmethod
from netuse.nodes import NodeManager
from netuse.triplespace.network.discovery.record import DiscoveryRecord
from netuse.triplespace.network.client import RequestInstance, RequestManager, RequestObserver       

class WhitepageSelector(object):
    
    MEMORY_LIMIT = (16,'MB') # e.g. say the limit is 16MB
    
    @staticmethod
    def _zscores(elements): # to avoid importing the whole scipy
        std_dev = std(elements)
        meaN = mean(elements)
        
        zscores = []
        for e in elements:
            zscores.append( (e-meaN) / std_dev )
            
        return zscores
    
    @staticmethod
    def _to_bytes(value, unit):
        #print args
        #value = args[0]
        #unit = args[1]
        
        if unit=='KB':
            return 1024*value
        elif unit=='MB':
            return 1024*1024*value
        elif unit=='GB':
            return 1024*1024*1024*value
        elif unit=='TB':
            return 1024*1024*1024*1024*value
        else:
            return value
    
    #def memory_is_less_than(record, min_memory_limit):
    #    mem = WhitepageSelector._to_bytes(*record.memory)
    #    return mem<min_memory_limit
    
    @staticmethod
    def _filter_less_memory_than(candidates, min_memory_limit):
        # a) Filtra a los que no tengan al menos X memoria.        
        minm = WhitepageSelector._to_bytes(*min_memory_limit) # supose 1KB per node
        greater_than_min = lambda record: WhitepageSelector._to_bytes(*record.memory) >= minm
        return filter(greater_than_min, candidates)
    
    @staticmethod
    def _filter_less_storage_than(candidates, total_num_nodes):
        # b) Filtra a los que no tengan al menos X almacenamiento.
        #    Se estima en base a las medidas tomadas en la evaluacion de clues y el numero de nodos en ese espacio.
        required = WhitepageSelector._to_bytes(total_num_nodes, 'KB') # supose 1KB per node
        greater_than_required = lambda record: WhitepageSelector._to_bytes(*record.storage) >= required
        return filter(greater_than_required, candidates)
    
    @staticmethod
    def _any_with_full_battery(records):
        for record in records:
            if record.battery_lifetime==DiscoveryRecord.INFINITE_BATTERY:
                return True
        return False
    
    @staticmethod
    def _choose_within_full_battery_nodes(candidates):        
        # c1) Filtra los que tienen bateria a 1
        additional_filter = lambda record: record.battery_lifetime==DiscoveryRecord.INFINITE_BATTERY
        
        # d1) Selecciona al que tenga mejores caracteristicas: Memoria
        return WhitepageSelector._choose_the_one_with_most_memory(candidates, additional_filter)    
    
    @staticmethod
    def _choose_the_one_with_most_memory(candidates, additionalFilter=lambda n: True):
        best_memory_record = None
            
        for record in candidates:
            if additionalFilter(record):
                if best_memory_record is None:
                    best_memory_record = record
                elif best_memory_record.memory < record.memory:
                    best_memory_record = record
                    
        return best_memory_record
    
    @staticmethod
    def _filter_unsteady_nodes(candidates):
        # c2) filtra a aquellos que han demostrado inestabilidad (no se puede confiar en ellos)
        #    Si la media es mayor de 1h, (asi si inicias la red de 0, te evitas este filtro)
        joins = [record.joined_since for record in candidates]
        joins_mean = mean( joins )
        if joins_mean>2: # measured in slots of 30 mins
            #  Eliges a todos aquellos que tengan un z-score mayor que 1.
            new_candidates = list(candidates)
            zsco = WhitepageSelector._zscores( joins )
            for node, zsco in zip(candidates, zsco):
                if zsco<1:
                    new_candidates.remove(node)
            
            # Si no hay ninguno por encima de 1, eliges los que esten por encima de la media (z-score>0)
            if not new_candidates:
                new_candidates = []
                for record in candidates:
                    if record.joined_since >= joins_mean:
                        new_candidates.append(node)
                        
            return new_candidates
        
        return candidates
    
    @staticmethod
    def _filter_nodes_with_more_battery(candidates):
        # d2) De entre aquellos con z-score de bateria de 1 o mas: el que tenga mas memoria.
        battery = [record.battery_lifetime for record in candidates]

        new_candidates = list(candidates)
        zsco = WhitepageSelector._zscores( battery )
        for node, zsco in zip(candidates, zsco):
            if zsco<1:
                new_candidates.remove(node)
        
        # Si no hay ninguno por encima de 1, eliges los que esten por encima de la media (z-score>0)
        if not new_candidates:
            new_candidates = []
            battery_mean = mean( battery )
            for record in candidates:
                if record.battery_lifetime >= battery_mean:
                    new_candidates.append(node)
        return new_candidates                
    
    @staticmethod
    def select_whitepage(candidate_records):
        candidates = list(candidate_records)
        total_len = len(candidates)
        
        candidates = WhitepageSelector._filter_less_memory_than(candidates, WhitepageSelector.MEMORY_LIMIT)
        candidates = WhitepageSelector._filter_less_storage_than(candidates, total_len)
        
        # Si hubiese nodos que tienen bateria a 1...
        if WhitepageSelector._any_with_full_battery(candidates):
            return WhitepageSelector._choose_within_full_battery_nodes(candidates)
        
        # Si no hubiese nodos con bateria infinita
        else: 
            candidates = WhitepageSelector._filter_unsteady_nodes(candidates)
            candidates = WhitepageSelector._filter_nodes_with_more_battery(candidates)
            
            # De esta forma se da prioridad a los que tienen mas bateria y de entre ellos se elige al que tenga mas memoria.
            return WhitepageSelector._choose_the_one_with_most_memory(candidates)


class SelectionProcessObserver(object):    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def wp_selection_finished(self, wp_node):
        pass


class WhitepageSelectionManager(RequestObserver):
    
    def __init__(self, simulation, discovery):
        self.simulation = simulation
        self.discovery = discovery
        self.refused = []
        self.observer = None
        self.last_choosen = None # contains the name of the last choosen node
        
    def set_observer(self, observer):
        self.observer = weakref.proxy(observer)
    
    def choose_whitepage(self, clue_store):
        # TODO consider that I can choose myself as a WP
        candidates = [item for item in self.discovery.get_discovered_records() if item.node_name not in self.refused]
        self.last_choosen = WhitepageSelector.select_whitepage(candidates)
        if self.last_choosen==None:
            # somehow, transmit that no node could be chosen
            pass
        else:
            RequestManager.launchNormalRequest( self._get_choose_request( clue_store ) )
    
    def _get_choose_request(self, clue_store):
        data = '' if clue_store is None else clue_store.toJson()
        req = RequestInstance( self.discovery.me,
                               [ NodeManager.getNodeByName(self.last_choosen.node_name) ],
                               '/whitepage/choose', data = data,
                               sim = self.simulation ) # it has data => POST
        req.addObserver(self)
        return req
    
    def notifyRequestFinished(self, request_instance):
        for unique_response in request_instance.responses:
            if unique_response.getstatus()==200:
                self.observer.wp_selection_finished( NodeManager.getNodeByName(self.last_choosen.node_name) )
            else: # has refused being whitepage!
                self.refused.append(self.last_choosen)
                self.choose_whitepage()