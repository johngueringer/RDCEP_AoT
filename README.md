DEPENDENCIES
	datetime
	matplotlib
	numpy
	scipy
	urllib2

FILES
	sensor.py   : Defines Sensor class and necessary functions for encapsulating
			      data from individual AoT sensors
	node.py     : Defines Node class and necessary functions for encapsulating 
			      data from entire AoT nodes
	aot.py      : Defines AoT class and necessary functions for encapsulating data 
			      from multiple AoT nodes
	constants.py: contains any static information such as sensor codes, and urls
	
FUNCTIONALITY
	Sensor	
		The sensor class is broken up into three classes based on the three 
		types of sensors in the AoT nodes:
		
			Sensor (superclass)  : Sensors that only collect one type of data
			DualSensor (subclass): Sensors that collect two types of data
			GridSensor (subclass): 4x4 IR grid sensor
		
		Each Sensor has a add_point(line) method (adds a datapoint to the sensor 
		from a formatted string), and a plot_timeseries() method which generates 
		a timeseries of the data within the sensor object.
		
		Additionally, the DualSensor class has a plot_correlation() function that 
		generates a grph showing the correlation between the two types of data in 
		the sensor.
		
		The Grid sensor class also includes a plot_heatmap(hrs) method which 
		generates a heatmap of the pixels in the IR grid. The "hrs" parameter 
		determines how the grid data is averaged (every hour, 2 hours, 3 hours,
		etc.). The GridSensor also includes a view_grid() method that generates a
		figure with 2 hour averaged heatmaps of the grid, a 24 hour averaged 
		heatmap, and a timeseries of the grid data.
	
	Node
		The Node class is dependent on the classes in the sensor.py file. The Node
		class contains a plot_timeseries() method that will generate a figure 
		containg timeseries of each sensor in the node. The Node class also includes
		a sensor(code) method which selects an individual sensor given its model. This
		allows the user to work with individual sensors rather than the whole node.
		
	AoT
		The AoT class is dependent on the classes in the node.py and sensor.py 
		files. The AoT class contains an add_node(node) method that adds a Node 
		object to the AoT object.
		
USE
	The previously mentioned files are not sommand line executable, and are 
	meant to be used within other programs. As such, to use the sensor, node, and
	aot classes they must first be imported into the program.
	Generally, one would start by instantiating a Node object so that the user has 
	data to work with.