import pm4py
from pm4py.algo.filtering.log.variants import variants_filter
import pandas as pd
from datetime import datetime, timedelta

def getNumberCases(log):
    num_cases = log['case:concept:name'].nunique()
    return num_cases

def getActivityCount(log):
    complete_activities = log[log['lifecycle:transition'] == 'complete']
    activity_counts = complete_activities.groupby('concept:name').size().reset_index(name='count')
    return activity_counts

def getDurationsCases(log):
    all_case_durations = pm4py.get_all_case_durations(log)
    return all_case_durations

def getTotalDuration(log):
    log['time:timestamp'] = pd.to_datetime(log['time:timestamp'])

    lowest_timestamp = log['time:timestamp'].min()
    highest_timestamp = log['time:timestamp'].max()
    duration = highest_timestamp - lowest_timestamp

    return duration

def getResources(log):
    resources = log["org:resource"].dropna().unique()
    return resources

def getCostByActivity(log):
    # This give the total cost for every activity. For the avg, divide it for the number of traces with this activity
    # Group by "concept:name" and sum the "resourceCost"
    log["resourceCost"] = pd.to_numeric(log["resourceCost"], errors="coerce")
    cost_by_activity = round(log.groupby("concept:name")["resourceCost"].sum(),2)

    # Filter out rows with missing or NaN "resourceCost", if needed
    cost_by_activity = cost_by_activity.dropna()
    return(cost_by_activity)

def getCostByResource(log):
    resource_costs = round(log.groupby('org:resource')['resourceCost'].sum(),2)
    return resource_costs

def getAvgArrivalTime(log):
    start_activity = pm4py.get_start_activities(log, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')  
    start_activity = next(iter(start_activity))
    cases_starts = log[log['concept:name'] == start_activity]
    cases_starts = cases_starts[cases_starts['lifecycle:transition'] == "assign"]
    cases_starts.sort_values('time:timestamp', inplace=True)
    
    """
    print(cases_starts[['concept:name','time:timestamp']])
    interarrival_times = []
    timestamps = cases_starts['time:timestamp'].tolist()
    print(timestamps)
    interarrival_times += [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
    
    average_interarrival_time = sum(interarrival_times) / len(interarrival_times)
    
    return round(average_interarrival_time,2)
    """
    cases_starts['date'] = cases_starts['time:timestamp'].dt.date
    avg_interarrival_times = []
    unique_dates = cases_starts['date'].unique()
    for date in unique_dates:
        timestamps = cases_starts[cases_starts['date'] == date]['time:timestamp'].tolist()
        interarrival_times = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
        avg_interarrival_time = sum(interarrival_times) / len(interarrival_times)
        avg_interarrival_times.append(avg_interarrival_time)
    
    overall_average_interarrival_time = sum(avg_interarrival_times) / len(avg_interarrival_times)
    
    return round(overall_average_interarrival_time, 2)

def getProcessingTimes(log):
    log['time:timestamp'] = pd.to_datetime(log['time:timestamp'], format="%Y-%m-%dT%H:%M:%S.%f%z")

    # Filter rows with lifecycle:transition 'start' or 'complete'
    start_rows = log[log['lifecycle:transition'] == 'start']
    complete_rows = log[log['lifecycle:transition'] == 'complete']

    # Group 'start' and 'complete' rows by concept:name
    start_groups = start_rows.groupby('concept:name')
    complete_groups = complete_rows.groupby('concept:name')

    # Compute processing time for each activity
    processing_times = {}
    for name, start_group in start_groups:
        complete_group = complete_groups.get_group(name)
        start_times = start_group['time:timestamp'].reset_index(drop=True)
        complete_times = complete_group['time:timestamp'].reset_index(drop=True)
        #print(f"Start Times for '{name}':\n{start_times}\n")
        #print(f"Complete Times for '{name}':\n{complete_times}\n")
        processing_time = (complete_times - start_times).mean()
        processing_times[name] = processing_time.total_seconds()

    return(processing_times)

def getWaitingTimes(log):
    log['time:timestamp'] = pd.to_datetime(log['time:timestamp'], format="%Y-%m-%dT%H:%M:%S.%f%z")

    # Filter rows with lifecycle:transition 'start' or 'complete'
    assign_rows = log[log['lifecycle:transition'] == 'assign']
    start_rows = log[log['lifecycle:transition'] == 'start']

    # Group 'assign' and 'start' rows by concept:name
    assign_groups = assign_rows.groupby('concept:name')
    start_groups = start_rows.groupby('concept:name')

    # Compute processing time for each activity
    waiting_times = {}
    for name, assign_group in assign_groups:
        start_group = start_groups.get_group(name)
        assign_times = assign_group['time:timestamp'].reset_index(drop=True)
        start_times = start_group['time:timestamp'].reset_index(drop=True)
        #print(f"assign Times for '{name}':\n{assign_times}\n")
        #print(f"start Times for '{name}':\n{start_times}\n")
        waiting_time = (start_times - assign_times).mean()
        waiting_times[name] = waiting_time.total_seconds()

    return(waiting_times)

def getResourceCalendar(log):
    log = log[log['lifecycle:transition'] == 'complete']
    log['time:timestamp'] = pd.to_datetime(log['time:timestamp'])

    log['org:resource'] = log['org:resource'].str.split('-').str[0]
    log['dayname'] = log['time:timestamp'].dt.day_name()
    log['weekday'] = log['time:timestamp'].dt.weekday
    log['time'] = log['time:timestamp']
    min_times = log.groupby(['org:resource', log['time:timestamp'].dt.weekday])['time'].min().dt.round('30min').dt.time
    max_times = log.groupby(['org:resource', log['time:timestamp'].dt.weekday])['time'].max().dt.round('30min').dt.time

    resourceTimes = pd.DataFrame({'min_time': min_times, 'max_time': max_times})
    with open('output.txt', 'w') as file:
        # Write the variable to the file
        file.write(log[['org:resource','time:timestamp']].to_string())
    return resourceTimes    # TAKE FROM THIS ONLY THE MIN AND MAX OF THE DAYS AND RETURN IN THE OUTPUT THE DAYS IN WHICH THE RESOURCE WORKS WITH MIN AND MAX HOURS

def discover_xor_probabilities(log):
    log = log[log['lifecycle:transition'] == 'complete']
    discovered_bpmn = pm4py.discover_bpmn_inductive(log)
    #pm4py.view_bpmn(discovered_bpmn)
    
    xor_probabilities = {}
    #print(discovered_bpmn.get_nodes())
    
    for node in discovered_bpmn.get_nodes():
        if isinstance(node, pm4py.objects.bpmn.obj.BPMN.ExclusiveGateway) and (node.get_gateway_direction() == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.DIVERGING):
            #print(node.get_out_arcs())
            #print(node.get_gateway_direction())
            outgoing_arcs = node.get_out_arcs()
            total_count = 0
            counts = {}
            probabilities = {}

            for arc in outgoing_arcs:
                target = arc.get_target()
                #print(arc.get_target())
                #print(target.name)
                logTarget = log[log['concept:name'] == target.name]
                count = len(logTarget)
                counts[target.name] = count
                total_count += count
            
            probabilities = {target: round(count / total_count, 2) for target, count in counts.items()}
            xor_probabilities[node.name] = probabilities

    return xor_probabilities

if __name__ == "__main__":
    log = pm4py.read_xes('Logs/test_23-06-23/test_23-06-23.xes')    # Read the event log in a pandas dataframe

    num_cases = getNumberCases(log)
    print(f"Number of Processed Instances: {num_cases}")
 
    activities = getActivityCount(log)
    resources = getResources(log)
    print(f"Count for Activities: {activities}")
    print(f"Resources: {resources}")
    #start_activity = pm4py.get_start_activities(log, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    #end_activitiy = pm4py.get_end_activities(log, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')

    duration = getTotalDuration(log)
    print(f"Total process duration: {duration}")


    cost_by_activity = getCostByActivity(log)
    print(f"Cost by Activity: {cost_by_activity}")

    resource_costs = getCostByResource(log)
    print(f"Cost by Resources: {resource_costs}")

    case_arrival_ratio = getAvgArrivalTime(log)
    print(f"Average Arrival Time between Cases: {case_arrival_ratio}")

    processingTimes = getProcessingTimes(log)
    print(f"Processing Times:\n {processingTimes}")
    
    waitingTimes = getWaitingTimes(log)
    print(f"Waiting Times:\n {waitingTimes}")
    
    print(f"Resources Calendar:\n {getResourceCalendar(log)}")

    print(f"XOR Split Probabilities:\n {discover_xor_probabilities(log)}")

