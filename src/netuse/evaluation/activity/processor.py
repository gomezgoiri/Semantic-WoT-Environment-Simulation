'''
Created on Sep 22, 2012

@author: tulvur
'''

class RawDataProcessor(object):

    def __init__(self):
        self.data = {}
    
    def _select_overlaping_periods(self, activity_periods, new_activity):
        overlaping = []
        for older_activity in activity_periods: # activity_periods are sorted by init time
            #   |----|            (new_activity)
            #           |----|    (older_activity)
            # Since the next activities won't overlap with the new one, skip the search
            if new_activity[1]<older_activity[0]:
                break
            #           |----|    (new_activity)
            #   |----|            (older_activity)
            # We are approaching to the overlaping areas, but not there yet...
            elif older_activity[1]>=new_activity[0]:
                #   |----------|      (new_activity)
                #        |----------| (older_activity)
                if new_activity[0]<=older_activity[0] and new_activity[1]<=older_activity[1]:
                    overlaping.append(older_activity)
                
                #        |----------| (new_activity)
                #   |----------|      (older_activity)
                elif new_activity[0]>=older_activity[0] and new_activity[1]>=older_activity[1]:
                    overlaping.append(older_activity)
                
                #      |----|         (new_activity)
                #   |----------|      (older_activity)
                elif new_activity[0]>older_activity[0] and new_activity[1]<older_activity[1]:
                    overlaping.append(older_activity)
                
                #   |----------|      (new_activity)
                #      |----|         (older_activity)
                elif new_activity[0]<older_activity[0] and new_activity[1]>older_activity[1]:
                    overlaping.append(older_activity)

        return overlaping
    
    # Changes activity_periods without creating a new list
    def _merge_periods_and_add(self, activity_periods, new_activity, overlaping_periods):
        delete_activities = []
        merged_activity = new_activity
        
        for older_activity in overlaping_periods:
            # is the new_activity subsumed by any other existing activity: don't touch the final list!
            #      |----|         (new_activity)
            #   |----------|      (older_activity)
            if new_activity[0]>older_activity[0] and new_activity[1]<older_activity[1]:
                return
            else:
                # does the new_activity subsume any other existing activity: remove it and add the new period to the final list
                #   |----------|   (new_activity [possibly previously merged with others])
                #      |----|      (older_activity)
                if merged_activity[0]<older_activity[0] and merged_activity[1]>older_activity[1]:
                    delete_activities.append(older_activity)
                
                #        |----------| (new_activity [possibly previously merged with others])
                #   |----------|      (older_activity)
                #   |---------------| (merged_activity)
                elif merged_activity[0]>=older_activity[0] and merged_activity[1]>=older_activity[1]:
                    delete_activities.append(older_activity)
                    merged_activity = (older_activity[0], merged_activity[1])
                
                #   |----------|      (new_activity [possibly previously merged with others])
                #        |----------| (older_activity)
                #   |---------------| (merged_activity)
                elif new_activity[0]<=older_activity[0] and new_activity[1]<=older_activity[1]:
                    delete_activities.append(older_activity)
                    merged_activity = (merged_activity[0], older_activity[1])
        
        # Remove and add
        for del_period in delete_activities:
            activity_periods.remove(del_period)
        activity_periods.append(merged_activity)
        
        # sorted(list) creates a new list
        # To avoid memory consumption, we modify the current list
        activity_periods.sort()
    
    
    def _add_activity_period(self, activities, node_name, init, finish):
        if node_name not in activities:
            activities[node_name] = []
        
        new_activity = (init, finish)
        overlaping = self._select_overlaping_periods(activities[node_name], new_activity)
        if not overlaping:
            activities[node_name].append((init, finish))
            activities[node_name].sort()
        else:
            self._merge_periods_and_add(activities, new_activity, overlaping)
    
    
    def _load(self, traces):
        '''
        "traces" is a list of NetworkTrace instances.
        
        This method uses the following fields of NetworkTrace. Therefore they should contain a value:
            - timestamp = FloatField(default=0.0)
            - client = StringField()
            - server = StringField()
            - response_time = FloatField(default=0.0)
            
        The method returns a dictionary with the names of the nodes and the time they have been processing something
        (both sending a request and waiting for the response (consumer) or receiving and processing it (provider)
        '''
        temp = {} # a dictionary containing a sorted list of activity periods (elements are tuples: (init, finish))
        for trace in traces:
            self._add_activity_period(temp, trace.client, trace.timestamp-trace.response_time, trace.timestamp)
            self._add_activity_period(temp, trace.server, trace.timestamp-trace.response_time, trace.timestamp)
        
        # sort by num_nodes
        results = {}
        
        for node_name, activity_periods in results.iteritems():
            busy_time = 0
            for activity in activity_periods:
                busy_time += (activity[1] - activity[0])
            results[node_name] = busy_time
            
        return results


# Entry point for setup.py
def main():
    rdp = RawDataProcessor()


if __name__ == '__main__':
    main()