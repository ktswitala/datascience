
import matplotlib
matplotlib.use('qt5agg')
import matplotlib.pyplot as plt
import scipy

import pandas as pd
import numpy as np
import seaborn

counties = [
	"wayne", "oakland", "macomb", "kent", 
	"genesee", "washtenaw", "ingham", "ottawa", 
	"kalamazoo", "livingston", "saginaw", "muskegon",
	"stclair", "jackson", "berrien", "monroe",
	"calhoun", "allegan", "eaton", "bay"
]

df_income = pd.DataFrame()
df_pop = pd.DataFrame()
df_unemp = pd.DataFrame()
df_house = pd.DataFrame()

for county in counties:
	df_csv = pd.read_csv(".\\data\\income - {0}.csv".format(county))
	df_csv.index = pd.to_datetime(df_csv["DATE"])
	del df_csv["DATE"]
	df_csv.columns = [county]
	df_income[county] = df_csv[county]
	
	df_csv = pd.read_csv(".\\data\\pop - {0}.csv".format(county))
	df_csv.index = pd.to_datetime(df_csv["DATE"])
	del df_csv["DATE"]
	df_csv.columns = [county]
	df_pop[county] = df_csv[county]

	df_csv = pd.read_csv(".\\data\\unemp - {0}.csv".format(county))
	df_csv.index = pd.to_datetime(df_csv["DATE"])
	del df_csv["DATE"]
	df_csv.columns = [county]
	df_unemp[county] = df_csv[county]

	df_csv = pd.read_csv(".\\data\\house - {0}.csv".format(county))
	df_csv.index = pd.to_datetime(df_csv["DATE"])
	del df_csv["DATE"]
	df_csv.columns = [county]
	df_house[county] = df_csv[county]
	
year_start = '1998-01-01'
year_end = '2018-01-01'	

series_pop = 100*(df_pop.loc[year_end, :] - df_pop.loc[year_start, :]) / df_pop.loc[year_end, :]
series_income = 100*(df_income.loc[year_end, :] - df_income.loc[year_start, :]) / df_income.loc[year_end, :]
series_unemp = df_unemp.loc[year_start:year_end, :].mean()
series_house = df_house.loc[year_start:year_end, :].mean()
df = pd.DataFrame({
	'% population change':series_pop, '% per capita income change':series_income, 
	'mean unemployment %':series_unemp, "mean housing index":series_house}, index=series_pop.index)
	
grid = seaborn.PairGrid(data=df, vars = ['% population change', '% per capita income change', 'mean unemployment %', 'mean housing index'])
sizes = df_pop.loc[year_start:year_end, :].mean() / 30

plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.85)

def corr_line(x, y, **kwargs):
	regress = scipy.stats.linregress(x, y)

	xmin, xmax = plt.gca().get_xlim()
	ymin, ymax = plt.gca().get_ylim()
	
	xs = np.linspace(xmin, xmax)
	ys = regress.slope * xs + regress.intercept
	
	plt.gca().plot(xs, ys)
	
def density(x, y, **kwargs):
	xmin, xmax = plt.gca().get_xlim()
	ymin, ymax = plt.gca().get_ylim()

	kernel = scipy.stats.gaussian_kde(np.vstack([x,y]), weights=sizes)
	X, Y = np.mgrid[xmin:xmax:50j, ymin:ymax:50j]
	positions = np.vstack([X.ravel(), Y.ravel()])
	Z = np.reshape(kernel(positions).T, X.shape)
	plt.gca().imshow(np.rot90(Z), cmap=plt.cm.Blues, aspect='auto', extent=[xmin, xmax, ymin, ymax])
		
grid = grid.map_upper(plt.scatter, s=2)
grid = grid.map_upper(corr_line)
grid = grid.map_lower(plt.scatter, s=sizes, color='black')
grid = grid.map_lower(density)

grid.fig.suptitle('Economic summary for the 20 most populous counties in \nMichigan, United States from years 1998-2018')
grid.fig.text(.1,.01,'Density plot weighted by population, dot area proportional to mean county population')

for i in [0,1,2,3]:
	for j in [0,1,2,3]:
		if j > i:
			grid.axes[i,j].spines["top"].set_visible(True)
			grid.axes[i,j].spines["right"].set_visible(True)
			grid.axes[i,j].spines["bottom"].set_visible(False)
			grid.axes[i,j].spines["left"].set_visible(False)
			grid.axes[i,j].tick_params(bottom=False, left=False, right=True, top=True)
		if i == 0:
			grid.axes[i,j].xaxis.set_ticks_position("top")
			grid.axes[i,j].xaxis.set_label_position("top")
			grid.axes[i,j].xaxis.set_label_text( grid.axes[3,j].xaxis.get_label_text() )
		if j == 3:
			grid.axes[i,j].yaxis.set_ticks_position("right")
			grid.axes[i,j].yaxis.set_label_position("right")
			grid.axes[i,j].yaxis.set_label_text( grid.axes[i,0].yaxis.get_label_text() )

for i in range(0, 4):
	grid.axes[i,i].spines['top'].set_visible(False)
	grid.axes[i,i].spines['right'].set_visible(False)
	grid.axes[i,i].spines['left'].set_visible(False)
	grid.axes[i,i].spines['bottom'].set_visible(False)
	grid.axes[i,i].tick_params(bottom=False, left=False, right=False, top=False)
	grid.axes[i,i].tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False)
	grid.axes[i,i].xaxis.set_label_text("")
	grid.axes[i,i].yaxis.set_label_text("")

#plt.show()
plt.savefig('scatter.png')

