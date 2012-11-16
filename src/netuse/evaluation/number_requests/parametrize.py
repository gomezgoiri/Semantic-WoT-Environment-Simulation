'''
Created on Jan 30, 2012

@author: tulvur
'''
from rdflib import RDF, Namespace
from netuse.results import G
from netuse.evaluation.utils import ParametrizationUtils, Parameters
from netuse.database.parametrization import Parametrization
from netuse.database.results import RequestsResults


# Entry point for setup.py
def main():
    from netuse.sim_utils import OwnArgumentParser
    parser = OwnArgumentParser('Parametrization for number of requests measuring.')
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
    
    
    # Prepare constant independent parameters
    default_params = Parameters (
                             amountOfQueries = 1000,
                             writeFrequency = 10000,
                             simulateUntil = 3600000,  # 1h of simulation time
                             queries = templates,
                           )
    p = ParametrizationUtils('network_usage', G.dataset_path, default_params, repetitions=1)
    
    
    # Prepare variable independent parameters
    var_params = []
    
    var_params.append (
       Parameters(
          strategy = Parametrization.negative_broadcasting,
          numConsumers = 1 # no importa en NB, y en our_solution se sobreescribe
        )
    )
    
    for numConsumers in (1, 10, 100):
        var_params.append (
           Parameters(
              strategy = Parametrization.our_solution,
              numConsumers = numConsumers
            )
        )
    
    # Prepare and save executions (possibly repeating them)
    p.save_repeating_for_network_sizes( network_sizes=range(5,301,10), rest_variable_parameters=var_params)


if __name__ == '__main__':
    main()