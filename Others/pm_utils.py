import pm4py

def visualizeBPMN(log):
    log = log[log['lifecycle:transition'] == 'complete']
    process_model = pm4py.discover_bpmn_inductive(log)
    pm4py.view_bpmn(process_model)
    #pm4py.write_bpmn(process_model, "model.bpmn")

def visualizePetriNet():
    process_model, m1, m2 = pm4py.discover_petri_net_inductive(log)
    pm4py.view_petri_net(process_model)

def getStartActivities(log):
    return pm4py.get_event_attribute_values(log, 'concept:name', case_id_key='case:concept:name')


if __name__ == "__main__":
    log = pm4py.read_xes('Logs/deliveroo23.xes')
    visualizeBPMN(log)
    #print(getStartActivities(log))
    #visualizePetriNet()