from igraph import *
import matplotlib.pyplot as plt
from book import *

#The `write_hapax_legomena_table()` function write the _Hapax_
#frequency to be included in the paper using LaTeX syntax for tables.

def write_hapax_legomena_table(books):
	fn = 'hapax.tex'

	f = open(fn, "w")
	f.write("\\begin{tabular}{l|c}\n")
	f.write("\\bf Book & number of {\\it Hapax Legomena} characters/number of characters \\\\\n")
	
	# count the lapaxes for each book
	for book in books:
		nr_hapaxes = book.get_number_hapax_legomenas()
		nr_chars = book.get_number_characters()

		f.write(book.name + "&" + str(nr_hapaxes) + "/" + str(nr_chars)+ "\\\\\n")

	f.write("\end{tabular}\n")
	f.close()

# Writing global measures

# Global measures for each character network are written as a table and
# included in a LaTeX file named `global.tex` to be included in the
# manuscript.

# Clustering coefficient is calculated using `igraph`
# [transitivity](http://igraph.org/r/doc/transitivity.html) routine.  We
# also calculate
# [density](http://igraph.org/python/doc/igraph.GraphBase-class.html#density)
# and
# [diameter](http://igraph.org/python/doc/igraph.GraphBase-class.html#diameter)
# of the graph.

def write_global_measures(books):
	fn = 'global.tex'

	f = open(fn, "w")

	f.write("\\begin{tabular}{l|c|c|c}\\hline\n")
	f.write("\\bf\\hfil book\\hfil & \\bf\\hfil clustering coefficient\hfil"
		 + "& \\bf\\hfil density\\hfil & \\bf\\hfil diameter\\hfil\\\\ \\hline\n")
	for book in books:
	        book.graph['clustering'] = book.graph.transitivity_undirected()
	        book.graph['density'] = book.graph.density()
	        book.graph['diameter'] = book.graph.diameter(directed=False)

		f.write(book.name + " & " + str(book.graph['clustering']) + " & "
				  + str(book.graph['density']) + " & "
				  + str(book.graph['diameter']) + "\\\\ \n")
	f.write("\\hline\\end{tabular}\n")
	f.close()

# Plotting

## Ranking frequency

# Character appearance frequency is ranked in the y axis. The scale for
# y axis is logarithmic.

def plot_rank_frequency(books, normalize=True):
	fns = ['figure1a.png', 'figure1b.png']
	normalizes = [False, True]

	for k in range(len(fns)):
		fig, ax = plt.subplots()

		for book in books:
	    		g = book.graph
			name = book.name
			color = book.color
			marker = book.marker
	    		freqs = {}		
			xs = []
			ys = []
			ys_normalized = []
			max_freq = 0.0

			x = 1
			for character, freq in book.name_freqs.items():
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

## Centralities

# [Betweenness](http://igraph.org/python/doc/igraph.GraphBase-class.html#betweenness),
# [closeness](http://igraph.org/python/doc/igraph.GraphBase-class.html#closeness)
# and
# [eigenvector](http://igraph.org/python/doc/igraph.GraphBase-class.html#eigenvector_centrality)
# centralities are calculated using `igraph`. The normalization of
# betweeness is obtained by dividing the value by $(N-1)(N-2)/2$, where $N$ is
# the number of vertices.

def plot_centralities(books):
	offset_fig_nr = 1 # figure number starts after 1

	for book in books:
        	g = book.graph.as_undirected()
		name = book.name

		# DEGREE
		for i in range(len(g.vs)):
            		g.vs[i]['Degree'] = g.vs[i].degree(mode="out")

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
		book.calc_graph_vertex_lobby()

	centrs = ["Degree", "Betweenness", "Closeness", "Lobby"] # Degree, Betweenness, Closeness, Lobby
	for c in centrs:
		fn = c + ".png"

		fig, ax = plt.subplots()

		for i in range(len(books)):
		        g = books[i].graph.as_undirected()
			name = books[i].name
			color = books[i].color
			marker = books[i].marker
			xs = []
			ys = []
			freqs = {}

			# calculate the centrality frequency
			for v in g.vs:
                                print(c+" "+v['name'])
                                
				val = v[c]
			    	if freqs.has_key(val):
                			freqs[val] = freqs[val] + 1
            			else:
					freqs[val] = 1

			# Normalize and add to points to plot
			for val, freq in freqs.items():
				x = val # val
				y = float(freq) / g.vcount()   # freq / N
				xs.append(x)
				ys.append(y)
									
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

# Graphs are drawing using
# [_igraph_](http://igraph.org/python/doc/tutorial/tutorial.html)
# library and written to output as png files. Graph drawings are not
# used in the paper but they are showed in the project page.

def draw_graphs(books):
	for book in books:
        	g = book.graph.as_undirected()
		fn = book.name+".png"

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

# The main subroutine declares some attributes associated with the
# books. Those attributes are used to label the books and to
# standardize the pictorial elements properties like color and point
# marker in the plot.

if __name__ == "__main__":
	color = {'bible': 'red', 'fiction': 'blue', 'biography': 'darkgreen'}

	acts = {'name': 'acts', 'source':'local', 'color': color['bible'], 'marker': 's'}
	arthur = {'name': 'arthur', 'source':'local', 'color': 'magenta', 'marker': '>'}
	david = {'name': 'david', 'source':'sgb', 'color': color['fiction'], 'marker': '8'}
	hobbit = {'name': 'hobbit', 'source':'local', 'color': color['fiction'], 'marker': 'p'}
	huck = {'name': 'huck', 'source':'sgb', 'color': color['fiction'], 'marker': 'H'}
	luke = {'name': 'luke', 'source':'local', 'color': color['bible'], 'marker': '8'}
	newton = {'name': 'newton', 'source':'local', 'color': color['biography'], 'marker': 'o'}
	pythagoras = {'name': 'pythagoras', 'source':'local', 'color': color['biography'], 'marker': '^'}
	tolkien = {'name': 'tolkien', 'source':'local', 'color': color['biography'], 'marker': 'd'}
	
#	attrs = [acts, arthur, david, hobbit,
#	      	      huck, luke, newton,
#		      pythagoras, tolkien]
	books = []

	attrs = [arthur]

	for i in range(len(attrs)):
	    cn = Book(attrs[i]['name'], attrs[i]['source'], attrs[i]['color'], attrs[i]['marker'])
	    books.append(cn)

	write_global_measures(books)
	write_hapax_legomena_table(books)
	plot_rank_frequency(books)
	plot_centralities(books)
	draw_graphs(books)

