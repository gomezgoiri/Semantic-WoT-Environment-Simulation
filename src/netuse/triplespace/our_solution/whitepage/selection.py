from numpy import mean, std
from abc import ABCMeta, abstractmethod
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
    
    #def memory_is_less_than(node, min_memory_limit):
    #    mem = WhitepageSelector._to_bytes(*node.discovery_record.memory)
    #    return mem<min_memory_limit
    
    @staticmethod
    def _filter_less_memory_than(candidates, min_memory_limit):
        # a) Filtra a los que no tengan al menos X memoria.        
        min = WhitepageSelector._to_bytes(*min_memory_limit) # supose 1KB per node
        greater_than_min = lambda node: WhitepageSelector._to_bytes(*node.discovery_record.memory) >= min
        return filter(greater_than_min, candidates)
    
    @staticmethod
    def _filter_less_storage_than(candidates, total_num_nodes):
        # b) Filtra a los que no tengan al menos X almacenamiento.
        #    Se estima en base a las medidas tomadas en la evaluacion de clues y el numero de nodos en ese espacio.
        required = WhitepageSelector._to_bytes(total_num_nodes, 'KB') # supose 1KB per node
        greater_than_required = lambda node: WhitepageSelector._to_bytes(*node.discovery_record.storage) >= required
        return filter(greater_than_required, candidates)
    
    @staticmethod
    def _any_with_full_battery(nodes):
        for node in nodes:
            if node.discovery_record.battery_lifetime==DiscoveryRecord.INFINITE_BATTERY:
                return True
        return False
    
    @staticmethod
    def _choose_within_full_battery_nodes(candidates):        
        # c1) Filtra los que tienen bateria a 1
        additional_filter = lambda node: node.discovery_record.battery_lifetime==DiscoveryRecord.INFINITE_BATTERY
        
        # d1) Selecciona al que tenga mejores caracteristicas: Memoria
        return WhitepageSelector._choose_the_one_with_most_memory(candidates, additional_filter)    
    
    @staticmethod
    def _choose_the_one_with_most_memory(candidates, additionalFilter=lambda n: True):
        best_memory_node = None
            
        for node in candidates:
            if additionalFilter(node):
                if best_memory_node==None:
                    best_memory_node = node
                elif best_memory_node.discovery_record.memory < node.discovery_record.memory:
                    best_memory_node = node
                    
        return best_memory_node
    
    @staticmethod
    def _filter_unsteady_nodes(candidates):
        # c2) filtra a aquellos que han demostrado inestabilidad (no se puede confiar en ellos)
        #    Si la media es mayor de 1h, (asi si inicias la red de 0, te evitas este filtro)
        joins = [node.discovery_record.joined_since for node in candidates]
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
                for node in candidates:
                    if node.discovery_record.joined_since >= joins_mean:
                        new_candidates.append(node)
                        
            return new_candidates
        
        return candidates
    
    @staticmethod
    def _filter_nodes_with_more_battery(candidates):
        # d2) De entre aquellos con z-score de bateria de 1 o mas: el que tenga mas memoria.
        battery = [node.discovery_record.battery_lifetime for node in candidates]

        new_candidates = list(candidates)
        zsco = WhitepageSelector._zscores( battery )
        for node, zsco in zip(candidates, zsco):
            if zsco<1:
                new_candidates.remove(node)
        
        # Si no hay ninguno por encima de 1, eliges los que esten por encima de la media (z-score>0)
        if not new_candidates:
            new_candidates = []
            battery_mean = mean( battery )
            for node in candidates:
                if node.discovery_record.battery_lifetime >= battery_mean:
                    new_candidates.append(node)
        return new_candidates                
    
    @staticmethod
    def select_whitepage(candidate_nodes):
        candidates = list(candidate_nodes)
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
        self.last_choosen = None
        
    def set_observer(self, observer):
        self.observer = observer
    
    def choose_whitepage(self):
        candidates = [item for item in self.discovery.get_nodes() if item not in self.refused]
        self.last_choosen = WhitepageSelector.select_whitepage(candidates)
        if self.last_choosen==None:
            # somehow, transmit that no node could have been chosen
            pass
        else:
            RequestManager.launchNormalRequest(self._get_choose_request())
    
    def _get_choose_request(self):
        req = RequestInstance( self.discovery.me,
                               [self.last_choosen],
                               '/whitepage/choose', data = '',
                               sim = self.simulation ) # it has data => POST
        req.addObserver(self)
        return req
    
    def notifyRequestFinished(self, request_instance):
        for unique_response in request_instance.responses:
            if unique_response.getstatus()==200:
                self.observer.wp_selection_finished(self.last_choosen)
            else: # has refused being whitepage!
                self.refused.append(self.last_choosen)
                self.choose_whitepage()