import seaborn as sns
from matplotlib import pyplot
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import glob
from weasyprint import HTML,CSS
from jinja2 import Environment, FileSystemLoader

path = os.getcwd()
report_path = path + "/report"
output_path = path + "/output"
config_path = path + "/config"


env = Environment(loader=FileSystemLoader(report_path))
template = env.get_template( "reportTemplate.html")

dfIssue = pd.read_csv(output_path + "/Problematic.csv")
dfSuspect = pd.read_csv(output_path + "/suspectedProblematic.csv")


os.chdir(config_path)
variables = glob.glob('*.txt')
i=0
for fileName in variables:
   file = open(fileName, "r")
   varname = str.replace(fileName, ".txt", "")
   varname = str.lower(varname)
   variables[i]=varname+'_t'
   i = i+ 1
variables.append('Cluster')


issuedetails = dfIssue.groupby(variables).size().reset_index(name='count')
issuedetails = issuedetails[issuedetails['Cluster'] != -1]
issuedetails.sort_values(by=['Cluster'], inplace=True, ascending=False)

suspectdetails = dfSuspect.groupby(variables).size().reset_index(name='count')
suspectdetails = suspectdetails[suspectdetails['Cluster'] != -1]
suspectdetails.sort_values(by=['Cluster'], inplace=True, ascending=False)


dims = (5, 8)
plt.axis('off')

val=dfIssue.groupby(['Cluster']).size().reset_index(name='count')
val['percentage']=(pd.to_numeric(val['count'])/pd.to_numeric(val['count']).sum())*100
val.sort_values(by=['percentage'], inplace=True,ascending=False)
val = val.head(5)
fig, ax = pyplot.subplots(figsize=dims)
wedges, texts = ax.pie(val['percentage'], wedgeprops=dict(width=0.5), startangle=-40)
ax.set_title("Discovered Problematic clusters")
bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")

names = val['Cluster'].tolist()
for i, p in enumerate(wedges):
    ang = (p.theta2 - p.theta1)/2. + p.theta1
    y = np.sin(np.deg2rad(ang))
    x = np.cos(np.deg2rad(ang))
    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    connectionstyle = "angle,angleA=0,angleB={}".format(ang)
    kw["arrowprops"].update({"connectionstyle": connectionstyle})
    ax.annotate(names[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),horizontalalignment=horizontalalignment, **kw)
plt.savefig(report_path + "/graphs/problematicDonet.png")

val=dfIssue.groupby(['ProblematicArea']).size().reset_index(name='count')
val['percentage']=(pd.to_numeric(val['count'])/pd.to_numeric(val['count']).sum())*100
val.sort_values(by=['percentage'], inplace=True,ascending=False)
val = val.head(5)
fig, ax = pyplot.subplots(figsize=(8,6))
sns.barplot(ax=ax, x='percentage', y='ProblematicArea', data=val, label='small').set_title('percentage of alerts by Problematic lable')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(report_path + "/graphs/problematicBar.png")


val=dfSuspect.groupby(['Cluster']).size().reset_index(name='count')
val['percentage']=(pd.to_numeric(val['count'])/pd.to_numeric(val['count']).sum())*100
val.sort_values(by=['percentage'], inplace=True,ascending=False)
val = val.head(5)
fig, ax = pyplot.subplots(figsize=dims)
wedges, texts = ax.pie(val['percentage'], wedgeprops=dict(width=0.5), startangle=-40)
ax.set_title("Discovered Suspecting clusters")
bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")

names = val['Cluster'].tolist()
for i, p in enumerate(wedges):
    ang = (p.theta2 - p.theta1)/2. + p.theta1
    y = np.sin(np.deg2rad(ang))
    x = np.cos(np.deg2rad(ang))
    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    connectionstyle = "angle,angleA=0,angleB={}".format(ang)
    kw["arrowprops"].update({"connectionstyle": connectionstyle})
    ax.annotate(names[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),horizontalalignment=horizontalalignment, **kw)
plt.savefig(report_path+ "/graphs/suspectedDonet.png")

val=dfSuspect.groupby(['ProblematicArea']).size().reset_index(name='count')
val['percentage']=(pd.to_numeric(val['count'])/pd.to_numeric(val['count']).sum())*100
val.sort_values(by=['percentage'], inplace=True,ascending=False)
val = val.head(5)
fig, ax = pyplot.subplots(figsize=(8,6))
sns.barplot(ax=ax, x='percentage', y='ProblematicArea', data=val, label='small').set_title('percentage of alerts by suspected lable')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(report_path + "/graphs/suspectedBar.png")
plt.close()

val=dfIssue.groupby(['ProblematicArea','live_range']).size().reset_index(name='count')
val['percentage']=(pd.to_numeric(val['count'])/pd.to_numeric(val['count']).sum())*100
val.sort_values(by=['percentage'], inplace=True,ascending=False)


fig, ax = pyplot.subplots(figsize=(18,12))
sns.scatterplot(x = "live_range", y = "percentage",data=val, hue='ProblematicArea',s=450,alpha=0.8).set_title('percentage of problematic lablel alerts by time stayed')
sns.set(style='whitegrid')
#plt.tight_layout()
plt.savefig(report_path + "/graphs/issueTimeline.png")
plt.close()

val=dfSuspect.groupby(['ProblematicArea','live_range']).size().reset_index(name='count')
val['percentage']=(pd.to_numeric(val['count'])/pd.to_numeric(val['count']).sum())*100
val.sort_values(by=['percentage'], inplace=True,ascending=False)


fig, ax = pyplot.subplots(figsize=(18,12))
sns.scatterplot(x = "live_range", y = "percentage",data=val, hue='ProblematicArea',s=450,alpha=0.8).set_title('percentage of suspected lablel alerts by time stayed')
sns.set(style='whitegrid')
#plt.tight_layout()
plt.savefig(report_path + "/graphs/suspectedalertsTimeline.png")
plt.close()


issuedetails.drop(columns=['count'],inplace=True)
suspectdetails.drop(columns=['count'],inplace=True)
template_vars = {
                 "dfNegativeDetails" : issuedetails.to_html(index=False),
                 "dfSuspectDetails" : suspectdetails.to_html(index=False)
                 }
# Render our file and create the PDF using our css style file
html_out = template.render(template_vars)

with open(report_path + "/finalReport.html", "w") as fh:
    fh.write(html_out)
css=CSS(string='@page { size: A4; margin: 1cm } img { border: 1px solid #ddd; border-radius: 4px; padding: 1px; width: 270px; }')
HTML(string=html_out,base_url=report_path).write_pdf(report_path + "/report.pdf", stylesheets=[css],presentational_hints=True, zoom=.1,optimize_images=True)