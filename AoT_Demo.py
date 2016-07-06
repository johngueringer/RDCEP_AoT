#import classes
from sensor import Sensor, DualSensor, GridSensor
from node import Node
from aot import AoT

nodes = ['ucaot01', 'ucaot02']                   #Nodes to pull from
strt = "03-20-16"                                #Date to pull from
dtypes = ['Temperature', 'Luminous_Intensity']   #Data to pull
print 'Pulling Aot Data...'
aot = AoT(nodes, dtypes, strt)                   #Instantiate AoT Object

#Pull out the nodes
print 'Pulling nodes from AoT object...'
ucaot01 = aot.nodes['ucaot01']
ucaot02 = aot.nodes['ucaot02']

#View node data
print "Plotting Node data..."
ucaot01.plot_timeseries()
ucaot02.plot_timeseries()

#Pull out individual sensors
print 'Pulling sensor from nodes...'
grid01 = ucaot01.sensor('D6T-44L-06')
grid02 = ucaot01.sensor('D6T-44L-06')

#view sensor data
print 'Plotting sensor data'
grid01.view_grid()
grid02.plot_heatmap(1)

print 'Done! \nCheck in this directory for plots'