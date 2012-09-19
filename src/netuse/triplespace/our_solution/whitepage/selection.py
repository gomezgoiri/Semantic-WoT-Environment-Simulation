from numpy import mean, std
from netuse.triplespace.network.discovery import DiscoveryRecord
        

class WhitepageSelector(object):
    
    @staticmethod
    def _zscores(elements): # to avoid importing the whole scipy
        std_dev = std(elements)
        mean = std(elements)
        
        zscores = []
        for e in elements:
            zscores.append( (e-mean) / std_dev )
            
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
        for node in candidates:
            sto = WhitepageSelector._to_bytes(*node.discovery_record.storage) # tuple to parameters
            if sto<required:
                candidates.remove(node)
        return candidates
    
    @staticmethod
    def _any_with_full_battery(nodes):
        for node in nodes:
            if node.discovery_record.battery_lifetime==DiscoveryRecord.INFINITE_BATTERY:
                return True
        return False
    
    @staticmethod
    def _choose_within_full_battery_nodes(candidates):
        # d1) Selecciona al que tenga mejores caracteristicas: Memoria
        best_memory_node = None
        
        for node in candidates:
            # c1) Filtra los que tienen bateria a 1
            if node.discovery_record.battery_lifetime==DiscoveryRecord.INFINITE_BATTERY:
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
            for node, zsco in zip(new_candidates, zsco):
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
        for node, zsco in zip(new_candidates, zsco):
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
    def _choose_the_one_with_most_battery(candidates):
        best_memory_node = None
            
        for node in candidates:
            # c1) Filtra los que tienen bateria a 1
            if node.discovery_record.battery_lifetime==DiscoveryRecord.INFINITE_BATTERY:
                if best_memory_node==None:
                    best_memory_node = node
                elif best_memory_node.discovery_record.memory < node.discovery_record.memory:
                    best_memory_node = node
                    
        return best_memory_node
                
    
    @staticmethod
    def select_whitepage(candidate_nodes):
        candidates = list(candidate_nodes)
        total_len = len(candidates)
        
        candidates = WhitepageSelector._filter_less_memory_than(candidates, (16,'MB')) # e.g. say the limit is 16MB
        candidates = WhitepageSelector._filter_less_storage_than(candidates, total_len)
        
        # Si hubiese nodos que tienen bateria a 1...
        if WhitepageSelector._any_with_full_battery(candidates):
            return WhitepageSelector._choose_within_full_battery_nodes(candidates)
        
        # Si no hubiese nodos con bateria infinita
        else: 
            candidates = WhitepageSelector._filter_unsteady_nodes(candidates)
            candidates = WhitepageSelector._filter_nodes_with_more_battery(candidates)
            
            # De esta forma se da prioridad a los que tienen mas bateria y de entre ellos se elige al que tenga mas memoria.
            return WhitepageSelector._choose_the_one_with_most_battery(candidates)


class WhitepageSelectionManager(object):
    
    def __init__(self, discovery):
        self.discovery = discovery
    
    def choose_whitepage(self):
        candidates = list(self.discovery.rest)
        wp_candidate = WhitepageSelector.select_whitepage(candidates)
        # TODO ask him
    