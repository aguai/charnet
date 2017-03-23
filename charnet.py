from igraph import *
import matplotlib.pyplot as plt
import logging

# LOG helpers
logfn = 'charnet.log' # log file name
logf = None # log file
logger = logging.getLogger('charnet')
logger.setLevel(logging.INFO)
        
class CharNet(object):
        data_directory = 'data/'
        # Extension for data files
        data_file_extension = '.csv'	
        # Extension for files containing frequency of characters
	# appearance
	freq_file_extension = '.freq'

	def __init__(self, name=None, color=None, marker=None, source=None):
        	self.name = name
        	self.color = color
        	self.marker = marker
		self.source = source

		self.graph = None # igraph Graph

		# logging to standard output
		self.logger = logging.getLogger(self.name)
		## options: DEBUG, INFO, WARN, ERROR, CRITICAL
		self.logger.setLevel(logging.INFO)

		# read data file
		names_idx = {} # map names and indices
		next_idx = 0 # next free index
		arcs = {} # hash of array of arcs tips

		if (self.source == "charnet"):
                        b = Local(self.name)
                        self.graph = b.create_graph()
		else if (source=="sgb"):
                        sgb = SGB(self.name)
                        self.graph = sgb.create_graph()
		else
			logger.error("Data source parser not implemented: {0}", self.source)
			exit()

## Calculating Global measures

Clustering coefficient is calculated using `igraph`
[transitivity](http://igraph.org/r/doc/transitivity.html) routine.  We
also calculate
[density](http://igraph.org/python/doc/igraph.GraphBase-class.html#density)
and
[diameter](http://igraph.org/python/doc/igraph.GraphBase-class.html#diameter)
of the graph.

<<complete=False>>=
		self.graph['clustering'] = self.graph.transitivity_undirected()
		self.graph['density'] = self.graph.density()
		self.graph['diameter'] = self.graph.diameter(directed=False)
@


## Character frequency

Files in `data/` directory with ".freq" extension contains characters'
frequency already counted during data compilation. For the books that
don't have this file in `data/`, this file are generated and written
in a file with the same extension. The file has the following format:

````
Sir Isaac Newton;4
````

where "`;`" is the separator, the first column is the character name and
the second the frequency.

<<complete=False>>=
		self.freqs = {}
		fn = self.name + FREQ_EXTENSION

		self.logger.info("Read frequency for " + fn)
		f = open(fn, "r")
    	    	for ln in f:
            		(vname, freq) = ln.rstrip("\n").split(';')
			self.freqs[vname] = int(freq)
		f.close()
@

# Lobby or h index

All nodes are traversed and Lobby index is calculated and stored in
 the lobby macro-field.

If a node has the following list of neighbors sorted by degree:

<table>
<tr>
	<th> neighbor  </th><th>  degree </th>
</tr>
<tr>
<td>   1       </td><td>   21    </td>
</tr>
<tr>
<td>   2       </td><td>   18    </td>
</tr>
<tr>
<td>   3       </td><td>    4    </td>
</tr>
<tr>
<td>   4       </td><td>    3    </td>
</tr>
</table>

the Lobby index is 3 because degree $\leq$ neighbor_position.
 Degree repetitions are not accounted.

<<complete=False>>=
	def lobby(self):
		lobbies = []

		logf.write("Calculating lobby index for " + self.name + "\n")

	    	for u in self.graph.vs:
                	lobby = 1 # initialize lobby
                    	vdegs = [] # neighbors' degree

                    	edges = self.graph.es.select(_source=u.index)
                	for e in edges:
            	    		v = self.graph.vs[e.target]
            	    		vdegs.append(v.degree(mode='out'))
        
			vdegs.sort()
                	vdegs.reverse()
	       		old_vdeg = -1
	        	idx = 0
                	for vdeg in vdegs:
            	    		# Ignore repetition of degrees
            	    		if (vdeg != old_vdeg):
                       			idx = idx + 1
            	    		if (vdeg <= idx):
                       			u['lobby'] = lobby = vdeg
                       			break
             	    		old_deg = vdeg

			logf.write(" " + u['name'] + "\t" + str(lobby) + "\n")
			lobbies.append(lobby)

		return lobbies
@

# _Hapax_ _Legomena_

_Hapax_ _Legomena_ are words with occurrence frequency equals to one.
The `write_hapax_legomena_table()` function write the _Hapax_
frequency to be included in the paper using LaTeX syntax for tables.

<<complete=False>>=
def write_hapax_legomena_table(charnets):
	fn = 'hapax.tex'

	f = open(fn, "w")
	f.write("\\begin{tabular}{l|c}\n")
	f.write("\\bf Book & number of {\\it Hapax Legomena} characters/number of characters \\\\\n")
	
	# count the lapaxes for each book
	for charnet in charnets:
		nr_hapaxes = 0
		nr_chars = 0
		for name, freq in charnet.freqs.items():
		       	if (freq == 1):
		   		nr_hapaxes += 1

			nr_chars += 1

		f.write(charnet.name + "&" + str(nr_hapaxes) + "/" + str(nr_chars)+ "\\\\\n")

	f.write("\end{tabular}\n")
	f.close()
	logger.info("Wrote table in {0}", fn)
@

# Writing global measures

Glabal measures for each character network are written as a table and
included in a LaTeX file named `global.tex` to be included in the
manuscript.

<<complete=False>>=
def write_global_measures(charnets):
	fn = 'global.tex'

	f = open(fn, "w")

	f.write("\\begin{tabular}{l|c|c|c}\\hline\n")
	f.write("\\bf\\hfil book\\hfil & \\bf\\hfil clustering coefficient\hfil"
		 + "& \\bf\\hfil density\\hfil & \\bf\\hfil diameter\\hfil\\\\ \\hline\n")
	for charnet in charnets:
		f.write(charnet.name + " & " + str(charnet.graph['clustering']) + " & "
				  + str(charnet.graph['density']) + " & "
				  + str(charnet.graph['diameter']) + "\\\\ \n")
	f.write("\\hline\\end{tabular}\n")
	f.close()
	logger.info("Wrote table in {0}", fn)
@

# Plotting

## Ranking frequency

Character appearance frequency is ranked in the y axis. The scale for
y axis is logarithmic.

<<complete=False>>=
def plot_rank_frequency(charnets, normalize=True):
	fns = ['figure1a.png', 'figure1b.png']
	normalizes = [False, True]

	for k in range(len(fns)):
		fig, ax = plt.subplots()

		for charnet in charnets:
	    		g = charnet.graph
			name = charnet.name
			color = charnet.color
			marker = charnet.marker
	    		freqs = {}		
			xs = []
			ys = []
			ys_normalized = []
			max_freq = 0.0

			x = 1
			for character, freq in charnet.freqs.items():
			    	y = int(freq)
			    	xs.append(x)
				ys.append(y)
				x += 1

				if (y > max_freq): 
					max_freq = y 

			ys = sorted(ys, key=int, reverse=True)

			if (normalizes[k]==True):
				# normalize y (frequency)
				for i in range(len(ys)):
					ys[i] = float(ys[i]) / float(max_freq)

			marker_style = dict(linestyle=':', color=color, markersize=6)
			ax.plot(xs, ys, c=color,
			        marker=marker,
			        label=name,
               		        alpha=0.3, 
			        **marker_style)

		plt.xscale('log')
		ax.set_xlabel('rank')
		plt.yscale('log')
		ax.set_ylabel('F(r)') # frequency

		plt.rc('legend',fontsize=10)
		ax.legend()
		ax.grid(True)

		plt.savefig(fns[k])
		print("INFO: Wrote plot in " + fns[k])
@

## Centralities

[Betweenness](http://igraph.org/python/doc/igraph.GraphBase-class.html#betweenness),
[closeness](http://igraph.org/python/doc/igraph.GraphBase-class.html#closeness)
and
[eigenvector](http://igraph.org/python/doc/igraph.GraphBase-class.html#eigenvector_centrality)
centralities are calculated using `igraph`. The normalization of
betweeness is obtained by dividing the value by $(N-1)(N-2)/2$, where $N$ is
the number of vertices.

<<complete=False>>=
def plot_centralities(charnets):
	offset_fig_nr = 1 # figure number starts after 1

	for charnet in charnets:
        	g = charnet.graph.as_undirected()
		name = charnet.name

		# DEGREE
		for i in range(len(g.vs)):
            		g.vs[i]['Degree'] = v.degree(mode="out")

		# BETWEENNESS
#		cents   = g.betweenness(vertices=None, directed=False, weights='weight')
		cents   = g.betweenness(vertices=None, directed=False)
		for i in range(len(g.vs)):
			g.vs[i]['Betweenness'] = float(cents[i]) / ((g.vcount()-1)*(g.vcount()-2)/2.0)

		# CLOSENESS
#		cents   = g.closeness(vertices=None, weights='weight')
		cents   = g.closeness(vertices=None)
		for i in range(len(g.vs)):
			g.vs[i]['Closeness'] = cents[i]

		# LOBBY
		## Already do the assignment of lobby value to each vertex
		charnet.lobby()

	centrs = ["Degree", "Betweenness", "Closeness", "Lobby"] # Degree, Betweenness, Closeness, Lobby
	for c in centrs:
		fn = c + ".png"

		fig, ax = plt.subplots()

		for i in range(len(charnets)):
		        g = charnets[i].graph.as_undirected()
			name = charnets[i].name
			color = charnets[i].color
			marker = charnets[i].marker
			xs = []
			ys = []
			freqs = {}

			# calculate the centrality frequency
			for v in g.vs:
				val = v[i][c]
			    	if freqs.has_key(val):
                			freqs[val] = freqs[val] + 1
            			else:
					freqs[val] = 1

			# Normalize and add to points to plot
			logf.write("# "+ c " for " + name + ": " + str(g.vcount()) + " vertices\n")
			logf.write("  " + c + "\tnorm_" + c + "\tfrequency\tnorm_frequency\n")
			for val, freq in freqs.items():
				x = val # val
				y = float(freq) / g.vcount()   # freq / N
				xs.append(x)
				ys.append(y)
				logf.write("  " + str(deg) + "\t" + str(x) + "\t" + str(freq) + "\t" + str(y) + "\n")
					
			marker_style = dict(linestyle='', color=color, markersize=4)
			ax.plot(xs, ys, c=color,
				    marker=marker,
				    label=name,
               			    alpha=0.3, 
				    **marker_style)

		ax.grid(True)
		#plt.xscale('log')   			       			       
		ax.set_xlabel(c)
		plt.yscale('log')
		ax.set_ylabel('Frequency')
		#plt.legend()
		plt.tight_layout()
		plt.savefig(fn)
		logger.info("Wrote plot in {0}", fn)
@

# Graph drawing

Graphs are drawing using
[_igraph_](http://igraph.org/python/doc/tutorial/tutorial.html)
library and written to output as png files. Graph drawings are not
used in the paper but they are showed in the project page.

<<complete=False>>=
def draw_graphs(charnets):
	for charnet in charnets:
        	g = charnet.graph.as_undirected()
		fn = charnet.name+".png"

		visual_style = {} 
        	layout = g.layout("kk")
        	#layout = g.layout_reingold_tilford(root=2)

        	visual_style["vertex_size"] = 20
        	visual_style["vertex_label_size"] = 11
        	visual_style["vertex_color"] = "red"
        	visual_style["vertex_label"] = g.vs['name']
        	visual_style["edge_width"] = 1
        	visual_style["edge_curved"] = False
		#        visual_style["edge_width"] = [1 + 2 * int(is_formal) for is_formal in g.es["is_formal"]]
	        visual_style["layout"] = layout
	        visual_style["bbox"] = (800, 600)

	        plot(g, fn, **visual_style)
		logger.info("Wrote graph in {0}", fn)
@

# Main subroutine

The main subroutine declares some attributes associated with the
 books.  Those attributes are used to label the books and to
 standardize the pictorial elements properties like color and point
 marker in the plot.
 

<<complete=False>>=
if __name__ == "__main__":
	color = {'bible': 'red', 'fiction': 'blue', 'biography': 'darkgreen'}

	acts = {'name': 'acts', 'color': color['bible'], 'marker': 's'}
	arthur = {'name': 'arthur', 'color': 'magenta', 'marker': '>'}
	david = {'name': 'david', 'color': color['fiction'], 'marker': '8'}
	hobbit = {'name': 'hobbit', 'color': color['fiction'], 'marker': 'p'}
	huck = {'name': 'huck', 'color': color['fiction'], 'marker': 'H'}
	luke = {'name': 'luke', 'color': color['bible'], 'marker': '8'}
	newton = {'name': 'newton', 'color': color['biography'], 'marker': 'o'}
	pythagoras = {'name': 'pythagoras', 'color': color['biography'], 'marker': '^'}
	tolkien = {'name': 'tolkien', 'color': color['biography'], 'marker': 'd'}
	
#	attrs = [acts, arthur, david, hobbit,
#	      	      huck, luke, newton,
#		      pythagoras, tolkien]
	charnets = []

	attrs = [arthur]

	logf = open(logfn, "w")
	for i in range(len(attrs)):
	    cn = BookNet(attrs[i]['name'], attrs[i]['color'], attrs[i]['marker'])
	    charnets.append(cn)

	write_global_measures(charnets)
	write_hapax_legomena_table(charnets)
	plot_rank_frequency(charnets)
	plot_centralities(charnets)
	draw_graphs(charnets)

	logf.close()
@
