import pandas as pd
pd.options.mode.chained_assignment = None
import ast
import glob
import os
from sklearn.cluster import DBSCAN
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import joblib

path = os.getcwd()
input_path = path + "/input"
config_path = path + "/config"
output_path = path + "/output"
model_file = path + "/savedmodel/dbscan.pkl"

ts_format='%Y-%m-%d-%H.%M.%S.%f'
ttl = {
0: "Less than 30 mins",
1: "30-60 mins",
2: "60-120 mins",
3: "120 - 240 mins",
4: "240 - 480 mins",
5: "480 - 960 mins",
6: "960 - 1920 mins",
7: "1920 - 3840 mins"
}

df = pd.read_csv(input_path + "/export.csv")
df.columns= df.columns.str.lower()

os.chdir(config_path)
variables = glob.glob('*.txt')
i=0
for fileName in variables:
   file = open(fileName, "r")
   contents = file.read()
   dictionary = ast.literal_eval(contents)
   file.close()
   varname = str.replace(fileName, ".txt", "")
   varname = str.lower(varname)
   exec("%s = %s" % (varname, dictionary))
   variables[i]=varname
   i = i+ 1

file = open('fieldIndicator.map', "r")
Lines = file.readlines()
for line in Lines:
    mapping=str.lower(line).strip().split('=')
    #print(mapping)
    exec("%s = '%s'" % (mapping[0]+'_str', mapping[1]))
file.close()


df['deletedat'] = pd.to_datetime(df['deletedat'], format=ts_format,)
df['lastoccurrence'] = pd.to_datetime(df['lastoccurrence'], format=ts_format,)
df['mins'] = (df.deletedat - df.lastoccurrence).astype('timedelta64[m]')
df['mins'].fillna(0, inplace=True)

for statusField in variables:
   df[statusField].fillna(0, inplace=True)
   qry=statusField+" in @"+statusField+".keys()"
   df = df.query(qry)
   df[statusField+'_t']= df[statusField].map(eval(statusField))

#print(df.count())

df['live_range'] = pd.cut(df.mins, [0,30,60,120,240,480,960,1920,3840], include_lowest=True)
df['live_range'] = df['live_range'].cat.codes
df['live_range'] = df['live_range'].map(ttl)
#print(df.count())

db = DBSCAN( min_samples=8)
df['Cluster'] = db.fit_predict(df[variables])
#print(variables)
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)
#
print('Estimated number of clusters: %d' % n_clusters_)
print('Estimated number of noise points: %d' % n_noise_)
joblib.dump(db, model_file)

list_o = []
for i in range(len(variables)):
    dict_name=eval(variables[i])
    for kw in dict_name:
     list_o.append(dict_name[kw])

newlist = set(list_o)
list_o = list(newlist)
df_state = pd.DataFrame(list_o)
analyzer = SentimentIntensityAnalyzer()

df_state['sentiment'] = df_state[0].apply(lambda state: analyzer.polarity_scores(state)['compound'])
df_state['sentiment'].astype('int32').dtypes
df_state.loc[df_state.sentiment > 0, 'sentiment_result'] = 'Positive'
df_state.loc[df_state.sentiment < 0, 'sentiment_result'] = 'negative'
df_state.loc[df_state.sentiment == 0, 'sentiment_result'] = 'neutral'

dfSentiment = {}
for row in df_state.iterrows():
    dfSentiment[row[1][0]] = row[1]['sentiment_result']

for statusField in variables:
   df[statusField+'_s']= df[statusField+'_t'].map(dfSentiment)

df['ProblematicArea'] = ''
for statusField in variables:
 exec("%s = %s" % ('field', 'df.'+statusField+'_s'))
 exec("%s = %s" % ('value', statusField + '_str'))
 varname = str.replace(statusField, ".txt", "")
 if df.loc[field.str.contains('negative')]['ProblematicArea'].to_string() == '':
     df.loc[field.str.contains('negative'), 'ProblematicArea'] = 'ne-'+value
 elif df.loc[field.str.contains('neutral')]['ProblematicArea'].to_string() == '':
     df.loc[field.str.contains('neutral'), 'ProblematicArea'] = 'n-' + value
 elif len(df.loc[field.str.contains('neutral')]['ProblematicArea'].to_string()) > 1 or len(df.loc[field.str.contains('negative')]['ProblematicArea'].to_string()) > 1:
     df.loc[field.str.contains('neutral'), 'ProblematicArea'] = 'n-'+ value + ':' + df.loc[field.str.contains('neutral')]['ProblematicArea']
     df.loc[field.str.contains('negative'), 'ProblematicArea'] = 'ne-'+ value + ':' + df.loc[field.str.contains('negative')]['ProblematicArea']
 else:
  pass

unprocessedpartition=round(len(variables)/2)
filters= "(.*?n-[a-z]+){"+ str(unprocessedpartition)+"}"
df_unknown = df[df['ProblematicArea'].str.contains(filters)]
df_negative = df[df['ProblematicArea'].str.contains('(ne-[a-z]+)')]

val=df.groupby(['Cluster','ProblematicArea']).size().reset_index(name='count')
val['percentage']=(pd.to_numeric(val['count'])/pd.to_numeric(val['count']).sum())*100
val.sort_values(by=['percentage'], inplace=True,ascending=False)
val['ProblematicArea'].fillna('All-Good',inplace = True)
val['alias'] = ''

df.to_csv(output_path + "/alertsAnalyzed.csv",index=False)
df_negative.to_csv(output_path + "/Problematic.csv",index=False)
df_unknown.to_csv(output_path + "/suspectedProblematic.csv",index=False)
val.to_csv(output_path + '/summary.csv',index=False)

