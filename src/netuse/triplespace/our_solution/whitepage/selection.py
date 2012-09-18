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
        if unit=='KB':
            return 1024*value
        elif unit=='MB':
            return 1024*1024*value
        elif unit=='GB':
            return 1024*1024*1024*value
        else:
            return value
            
    @staticmethod
    def _filter_less_memory_than(candidates, min_memory_limit):
        # a) Filtra a los que no tengan al menos X memoria.
        limit = WhitepageSelector._to_bytes(min_memory_limit)
        for node in candidates:
            mem = WhitepageSelector._to_bytes(node.discovery_record.memory)
            if mem<limit:
                candidates.remove(node)
        return candidates
    
    @staticmethod
    def _filter_less_storage_than(candidates, total_num_nodes):
        # b) Filtra a los que no tengan al menos X almacenamiento.
        #    Se estima en base a las medidas tomadas en la evaluación de clues y el número de nodos en ese espacio.
        required = WhitepageSelector._to_bytes(total_num_nodes, 'KB') # supose 1KB per node
        for node in candidates:
            sto = WhitepageSelector._to_bytes(node.discovery_record.storage)
            if sto<required:
                candidates.remove(node)
        return candidates
    
    @staticmethod
    def _any_with_full_batery(nodes):
        for node in nodes:
            if node.discovery_record.batery_lifetime==DiscoveryRecord.INFINITE_BATERY:
                return True
        return False
    
    @staticmethod
    def _choose_within_full_battery_nodes(candidates):
        # d1) Selecciona al que tenga mejores características: Memoria
        best_memory_node = None
        
        for node in candidates:
            # c1) Filtra los que tienen batería a 1
            if node.discovery_record.batery_lifetime==DiscoveryRecord.INFINITE_BATERY:
                if best_memory_node==None:
                    best_memory_node = node
                elif best_memory_node.discovery_record.memory < node.discovery_record.memory:
                    best_memory_node = node
                    
        return best_memory_node
    
    
    @staticmethod
    def _filter_unsteady_nodes(candidates):
        # c2) filtra a aquellos que han demostrado inestabilidad (no se puede confiar en ellos)
        #    Si la media es mayor de 1h, (así si inicias la red de 0, te evitas este filtro)
        joins = [node.discovery_record.joined_since for node in candidates]
        joins_mean = mean( joins )
        if joins_mean>2: # measured in slots of 30 mins
            #  Eliges a todos aquellos que tengan un z-score mayor que 1.
            new_candidates = list(candidates)
            zsco = WhitepageSelector._zscores( joins )
            for node, zsco in zip(new_candidates, zsco):
                if zsco<1:
                    new_candidates.remove(node)
            
            # Si no hay ninguno por encima de 1, eliges los que estén por encima de la media (z-score>0)
            if not new_candidates:
                new_candidates = []
                for node in candidates:
                    if node.discovery_record.joined_since >= joins_mean:
                        new_candidates.append(node)
                        
            return new_candidates
        
        return candidates
    
    
    @staticmethod
    def _filter_nodes_with_more_battery(candidates):
        # d2) De entre aquellos con z-score de batería de 1 o más: el que tenga más memoria.
        batery = [node.discovery_record.batery_lifetime for node in candidates]

        new_candidates = list(candidates)
        zsco = WhitepageSelector._zscores( batery )
        for node, zsco in zip(new_candidates, zsco):
            if zsco<1:
                new_candidates.remove(node)
        
        # Si no hay ninguno por encima de 1, eliges los que estén por encima de la media (z-score>0)
        if not new_candidates:
            new_candidates = []
            batery_mean = mean( batery )
            for node in candidates:
                if node.discovery_record.batery_lifetime >= batery_mean:
                    new_candidates.append(node)
        return new_candidates        
    
    
    @staticmethod
    def _choose_the_one_with_most_batery(candidates):
        best_memory_node = None
            
        for node in candidates:
            # c1) Filtra los que tienen batería a 1
            if node.discovery_record.batery_lifetime==DiscoveryRecord.INFINITE_BATERY:
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
        
        # Si hubiese nodos que tienen batería a 1...
        if WhitepageSelector._any_with_full_batery():
            return WhitepageSelector._choose_within_full_battery_nodes(candidates)
        
        # Si no hubiese nodos con batería infinita
        else: 
            candidates = WhitepageSelector._filter_unsteady_nodes(candidates)
            candidates = WhitepageSelector._filter_nodes_with_more_battery(candidates)
            
            # De esta forma se da prioridad a los que tienen más batería y de entre ellos se elige al que tenga más memoria.
            return WhitepageSelector._choose_the_one_with_most_batery()


class WhitepageSelectionManager(object):
    
    def __init__(self, discovery):
        self.discovery = discovery
    
    def choose_whitepage(self):
        candidates = list(self.discovery.rest)
        wp_candidate = WhitepageSelector.select_whitepage(candidates)
        # TODO ask him
    