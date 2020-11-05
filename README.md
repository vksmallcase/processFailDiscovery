Netcool alert processing issue classification:-

Semi-supervised machine learning to derive actionable insight by reading historic data from Netcool reporter database and Intuition of auto classifying alerts based on event processing state it resulted previously and predicting it over real-time alarms for proactive actions.

![concept](https://github.com/vishnuk88/processFailDiscovery/blob/master/img/concept.png)

Solution description:-

- A python code takes input from the CSV file of the alert dump and generates labeled clusters automatically using machine learning models. 
- Affected clusters will be showcased under separate output files  suspectedProblematic.csv and Problematic.csv
- Discovered problematic alerts will be shown at summary.csv further it can be given with alias names for reference.
- predictive model generated with this solution which can be accessed using API interface.
- Predicting for underlying process failures at live alerts via restful API query.  
- Machine learning Algorithms used DBSCAN and Decision tree

![flow](https://github.com/vishnuk88/processFailDiscovery/blob/master/img/flow.png)

Deployment Instructions:-

1. Installation – Download the code and setup env locally using the command 
    pip install -r notes/requirements.txt.

2. Configuration - Place the alert dump taken from reporter DB at folder input file name should be export.csv
  Must have omnibus fields related to timestamps and columns holding alert processing status updates.
Eg:-'Serial','FirstOccurrence','LastOccurrence','Deletedat','ZProcessState',,'ZTicketState','ZTicketSeverity','TicketNumber','ZHNotifyState','ZGenericActionState'

3.  Configuration - Open a file in the name of the status update column, which must be included at the alert dump, and update it with information of possible numbers into the status field and its human-readable conversion text. 
  Eg:- {1: "Needed", 2: "InProgress"}

4.  Configuration - Add a respective column name entry at fieldIndicator.map with alias name to indicate the status column.
    Eg:- ZticketState=AutoTicket

5.  All set ready to use now.

Usage Instructions:-

1. Discovery – Run the failureDiscovery.py code.
    Output  – generates CSV files at the output directory where it contains cluster information and problematic areas description.

2. Reporting  - Run the reportGeneration.py code.
    Output  – A HTML file report with discovered information description and visualization. 

3.  Predictive model generation – Run the failurePredectionModel.py code.
     Output  – Generates a predictive model and saves it for API interaction.

4.  Restful API  - Run the code api4Prediction.py at the back end.
     Output  – It listens at port 5001 you can interact with a predictive model like below. 
     (Modification is required as per input fields used and update alias filed at summary.csv file under output folder for better output)

5.  All set to use now, this can now be integrated to Netcool real-time alarms via Netcool impact policy.

6. Example output - curl -k -u vk:hi https://127.0.0.1:5001/predict/5,312,1,40
{
  "ProblemType": "Timeout Ticketing issue",
  "Cluster": 16,
  "predicted": “Ok”
}
