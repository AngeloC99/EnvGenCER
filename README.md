# DataAnalysis
Script for the Data Analysis step of the CER's Big Data pipeline.
This work is part of my MSc thesis.

## About The Project
TThis script implements a Process Mining technique to extract simulation parameters for subsequent pipeline stages. It starts by reading the contents of the XES event log into a dataframe for allowing a more intuitive and conscious data processing by leveraging pandas, the well-established data manipulation library, alongside the state-of-the-art process mining functionalities and algorithms made available by PM4PY. Notably, the parameters derived from this analysis are the count of processed instances, activity and resource counts, total process duration in time, activity-related costs, resource-related costs, average arrival times between cases, average processing and waiting times for activities, resource calendars, and XOR split branching probabilities.
It is worth noticing that, for tasks like calculating XOR split branching probabilities, the script also foresees the discovery of the process model in BPMN format underlying the input log. This process leverages the Inductive Miner algorithm supported by PM4PY.


## Requirements
To run the project, the requirements are the following:
- [Python 3](https://www.python.org/) (>= v.3.10.12)
- [pandas](https://pandas.pydata.org/) (>= v.2.0.3)
- [PM4Py](https://pm4py.fit.fraunhofer.de/) (>= v.2.7.5)

## Running The Project
Go in the DataAnalysis directory and run the following command by specifying the path of the input event log:
```bash
python3 data_analysis.py "<input_directory_path>"
```
