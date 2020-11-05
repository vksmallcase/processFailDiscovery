import pandas as pd
import glob
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
import joblib
from sklearn.tree import DecisionTreeClassifier


path = os.getcwd()
report_path = path + "/report"
output_path = path + "/output"
config_path = path + "/config"
model_file = path + "/savedmodel/DTree.pkl"

df = pd.read_csv(output_path + "/alertsAnalyzed.csv")

os.chdir(config_path)
variables = glob.glob('*.txt')
i=0
for fileName in variables:
   file = open(fileName, "r")
   varname = str.replace(fileName, ".txt", "")
   varname = str.lower(varname)
   variables[i]=varname
   i = i+ 1
variables.append('Cluster')

dfClassify = df[variables]
variables.pop()

X_train, X_test, y_train, y_test = train_test_split(dfClassify[variables], dfClassify['Cluster'], test_size=0.3,random_state=109)

tree = DecisionTreeClassifier()
DTModel = tree.fit(X_train, y_train)
DTPred = tree.predict(X_test)
joblib.dump(DTModel, model_file)

# model accuracy for X_test
accuracy = DTModel.score(X_test, y_test)
print(accuracy)

score=f1_score(y_test, DTPred,average='weighted')
print(score)