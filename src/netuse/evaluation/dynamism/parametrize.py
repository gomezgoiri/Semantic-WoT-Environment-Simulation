# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
''' 

from rdflib import RDF, Namespace
from netuse.results import G
from netuse.evaluation.utils import ParametrizationUtils, Parameters
from netuse.database.parametrization import Parametrization, ParametrizableNetworkModel
from netuse.network_models import NetworkModelManager
from netuse.devices import XBee, SamsungGalaxyTab, FoxG20, Server
from netuse.triplespace.network.discovery.discovery import DiscoveryFactory


def add_baseline_simulations(var_params):
    """Adds simulation without nodes going up and down (normal network model)."""
    var_params.append (
       Parameters(
          strategy = Parametrization.negative_broadcasting,
          numConsumers = 1, # no importa en NB, y en our_solution se sobreescribe
          # normal network_model
        )
    )
    
    var_params.append (
       Parameters(
          strategy = Parametrization.our_solution,
          numConsumers = 100 # TODO somehow, we should define that Galaxy Tabs have more chances to be consumers than XBees
        )
    )
    

def add_simulations_with_dynamic_network_models(var_params, drop_down_period):
    for change_mean in drop_down_period:
        change_std_dev = 5000
        
        # chaotic network model to assess our solution
        chaotic_nm = ParametrizableNetworkModel (
                                type = NetworkModelManager.chaotic_netmodel,
                                state_change_mean = change_mean,
                                state_change_std_devdefault = change_std_dev
                        )
        chaotic_nm.save()
        
        var_params.append (
            Parameters(
              strategy = Parametrization.our_solution,
              numConsumers = 100, # TODO somehow, we should define that Galaxy Tabs have more chances to be consumers than XBees
              network_model = chaotic_nm
            )
        )
        
        # equivalent network model for "negative broadcasting"
        onedown_nm = ParametrizableNetworkModel (
                                type = NetworkModelManager.onedown_netmodel,
                                state_change_mean = change_mean,
                                state_change_std_devdefault = change_std_dev
                        )
        onedown_nm.save()
        
        var_params.append (
           Parameters(
                strategy = Parametrization.negative_broadcasting,
                numConsumers = 1, # no importa en NB, y en our_solution se sobreescribe
                network_model = onedown_nm
           )
        )

# Entry point for setup.py
def main():
    from commons.utils import OwnArgumentParser
    parser = OwnArgumentParser('Parametrization for energy consumption measuring.')
    parser.parse_args()
    
    
    SSN = Namespace('http://purl.oclc.org/NET/ssnx/ssn#')
    SSN_OBSERV = Namespace('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#')
    SSN_WEATHER = Namespace('http://knoesis.wright.edu/ssw/ont/weather.owl#')
    WGS84 = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
    CF = Namespace('http://purl.oclc.org/NET/ssnx/cf/cf-property#')
    CF_FEATURE = Namespace('http://purl.oclc.org/NET/ssnx/cf/cf-feature#')
    SMART_KNIFE = Namespace('http://purl.oclc.org/NET/ssnx/product/smart-knife#')
    BIZKAI_STATION = Namespace('http://dev.morelab.deusto.es/bizkaisense/resource/station/')
    
    
    templates = (
      # based on type
      (None, RDF.type, SSN_WEATHER.RainfallObservation), # in 43 nodes
      (None, RDF.type, SSN_OBSERV.Observation), # in many nodes, but, without inference?
      # predicate based
      (None, SSN_OBSERV.hasLocation, None), # domain LocatedNearRel
      (None, WGS84.long, None), # 155 objects (long belongs to SpatialThing, Point is subclass of SpatialThing and does not have range)
      (None, SSN_OBSERV.observedProperty, None), # observedProperty's range is Observation, but we have just subclasses of Observation (e.g. TemperatureObservation)
      (None, SMART_KNIFE.hasMeasurementPropertyValue, None), # domain ssn:MeasurementProperty child of ssn:Property
      (BIZKAI_STATION.ABANTO, None, None), # given an instance, we cannot predict anything
    )
    
    
    numNodes = 300
    
    # 1 server, 10% of galaxys, 25% of FoxG20
    nodeTypes = (Server.TYPE_ID,)*1
    nodeTypes += (SamsungGalaxyTab.TYPE_ID,)*((int)(numNodes*1.0))
    nodeTypes += (FoxG20.TYPE_ID,)*((int)(numNodes*0.25))
    # Remaining devices, are XBees
    nodeTypes += (XBee.TYPE_ID,)*(numNodes-len(nodeTypes))
    
    
    # Prepare constant independent parameters
    default_params = Parameters (
                         discovery = DiscoveryFactory.SIMPLE_DISCOVERY, #SIMPLE_DISCOVERY MDNS_DISCOVERY
                         amountOfQueries = 1000,
                         writeFrequency = 10000,
                         simulateUntil = 60*60000,  # 1h of simulation time
                         queries = templates,
                         nodeTypes = nodeTypes
                     )
    
    # Prepare variable independent parameters
    var_params = []
    add_baseline_simulations(var_params)
    add_simulations_with_dynamic_network_models(var_params, (45*60000, 30*60000, 20*60000, 10*60000, 5*60000, 60000, 30000)) # 45 mins, 30 mins, 20 mins, 10 mins, 5 mins, 1min, 30 secs
    
    # Prepare and save executions (possibly repeating them)
    p = ParametrizationUtils('dynamism', G.dataset_path, default_params, repetitions=1)
    p.save_repeating( network_size=numNodes, rest_variable_parameters=var_params )


if __name__ == '__main__':
    main()