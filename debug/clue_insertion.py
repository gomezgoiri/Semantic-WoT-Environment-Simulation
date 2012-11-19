from SimPy.Simulation import initialize, simulate

from testing.utils import TimeRecorder
from clueseval.clues.storage.sqlite import SQLiteClueStore


def insert_without_transactions(clues_json):
    recorder1 = TimeRecorder()
    store = SQLiteClueStore(database_path="/tmp")
    store.start()
    
    recorder1.start()
    store.fromJson(clues_json)
    recorder1.stop()
    
    print recorder1
    
    store.stop()
    
def insert_with_transactions(clues_json):
    recorder1 = TimeRecorder()
    store = SQLiteClueStore(database_path="/tmp")
    store.start()
    
    recorder1.start()
    store.fromJson2(clues_json)
    recorder1.stop()
    
    print recorder1
    
    store.stop()

def main():
    clues_json = """
    {"i": 1, "p": {"aemet/08272": {"_4": ["locatedIn", "indclim", "stationName", "indsinop"], "_8": ["location"]}, "knoesis/AR484": {"_3": ["ont/sensor-observation.owl#result", "ont/sensor-observation.owl#procedure", "ont/sensor-observation.owl#observedProperty", "ont/sensor-observation.owl#samplingTime"]}, "knoesis/AP048": {"_3": ["ont/sensor-observation.owl#result", "ont/sensor-observation.owl#samplingTime", "ont/sensor-observation.owl#observedProperty", "ont/sensor-observation.owl#procedure"]}, "morelab/janire-larranaga": {"_4": ["givenname", "primaryTopic", "mbox_sha1sum", "title", "name", "family_name", "workplaceHomepage"]}, "aemet/08095": {"_7": ["observedDataQuality", "valueOfObservedData", "observedInInterval"], "_4": ["featureOfInterest", "observedProperty", "observedBy"]}, "aemet/08022": {"_5": ["location"], "_4": ["stationName", "indclim", "indsinop"]}, "aemet/08180": {"_6": ["observedDataQuality", "valueOfObservedData", "observedInInterval"], "_4": ["featureOfInterest", "observedProperty", "observedBy"]}, "knoesis/AP117": {"_3": ["ont/sensor-observation.owl#result", "ont/sensor-observation.owl#procedure", "ont/sensor-observation.owl#observedProperty", "ont/sensor-observation.owl#samplingTime"]}, "knoesis/AR451": {"_6": ["alt", "long", "lat"], "_3": ["ont/sensor-observation.owl#distance", "ont/sensor-observation.owl#ID", "ont/sensor-observation.owl#uom", "ont/sensor-observation.owl#hasSourceURI", "ont/sensor-observation.owl#hasLocatedNearRel", "ont/sensor-observation.owl#parameter", "ont/sensor-observation.owl#processLocation", "ont/sensor-observation.owl#hasLocation"]}, "aemet/08051": {"_5": ["location"], "_4": ["stationName", "indclim", "indsinop"]}, "knoesis/AP192": {"_7": ["alt", "long", "lat"], "_3": ["ont/sensor-observation.owl#distance", "ont/sensor-observation.owl#ID", "ont/sensor-observation.owl#uom", "ont/sensor-observation.owl#hasSourceURI", "ont/sensor-observation.owl#hasLocatedNearRel", "ont/sensor-observation.owl#parameter", "ont/sensor-observation.owl#processLocation", "ont/sensor-observation.owl#hasLocation"]}, "knoesis/AGWC1": {"_3": ["ont/sensor-observation.owl#result", "ont/sensor-observation.owl#samplingTime", "ont/sensor-observation.owl#observedProperty", "ont/sensor-observation.owl#procedure"]}}, "s": [["_7", "http://www.w3.org/2003/01/geo/wgs84_pos#"], ["_4", "http://aemet.linkeddata.es/ontology/"], ["_4", "http://purl.oclc.org/NET/ssnx/ssn#"], ["_3", "http://knoesis.wright.edu/ssw/"], ["_4", "http://xmlns.com/foaf/0.1/"], ["_7", "http://aemet.linkeddata.es/ontology/"], ["_6", "http://www.w3.org/2003/01/geo/wgs84_pos#"], ["_6", "http://aemet.linkeddata.es/ontology/"], ["_5", "http://www.w3.org/2003/01/geo/wgs84_pos#"], ["_8", "http://www.w3.org/2003/01/geo/wgs84_pos#"]]}
    """
    insert_without_transactions(clues_json)
    insert_with_transactions(clues_json)


if __name__ == '__main__':
    main()