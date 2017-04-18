#!/usr/bin/python
from optparse import OptionParser
import logging
import math
import networkx as nx
import matplotlib.pyplot as plt
import pygraphviz as pgv
from book import *

# to calculate Pearson correlation
from scipy.stats.stats import pearsonr

# INIT
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

## Hapax Legomena
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

                ln = book.name + " & "
                ln += '{0:02d}'.format(nr_hapaxes) + "/"
                ln += '{0:02d}'.format(nr_chars) + " = "
                ln += '{0:.3f}'.format(float(nr_hapaxes)/nr_chars) + " \\\\\n"
                
		f.write(ln)

	f.write("\end{tabular}\n")
	f.close()

# Calculate the average degree and the standard deviation degree
# Source: http://holanda.xyz/files/mean.c
def degree_stat(G):
        avg_prev = float(G.degree(0))
        var_prev = 0
        for i in range(1, G.number_of_nodes()):
                deg = float(G.degree(i))
                avg_curr = avg_prev + (deg - avg_prev)/(i + 1)
                var_curr = var_prev + (deg - avg_prev) * (deg - avg_curr)

                avg_prev = avg_curr
                var_prev = var_curr
                        
        stdev = math.sqrt(var_curr/(G.number_of_nodes() - 1))

        return (avg_curr, stdev)
        
## Writing global measures
# Global measures for each character network are written as a table and
# included in a LaTeX file named `global.tex` to be included in the
# manuscript.
# Clustering coefficient is calculated using _NetworkX_ library
# [transitivity](https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.algorithms.cluster.transitivity.html#networkx.algorithms.cluster.transitivity)
# routine.  We also calculate
# [density](https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.classes.function.density.html)
# and
# [diameter](https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.algorithms.distance_measures.diameter.html)
# of the graph.
def write_global_measures(books):
        logging.info('Writing global measures...')
        
	fn = 'global.tex'

	f = open(fn, "w")

	f.write('{\small\\begin{tabular}{l|c|c|c|c|c}\\hline\n')
	f.write('\\bf\\hfil book\\hfil '
                + ' & \\bf\\hfil nodes\hfil '
                + ' & \\bf\\hfil edges\hfil '
                + ' & \\bf\\hfil avg. degree\hfil '
                + ' & \\bf\\hfil clustering coeff.\hfil '
		+ ' & \\bf\\hfil density\\hfil '
                #+ ' & \\bf\\hfil diameter\\hfil '
                + ' \\\\ \\hline\n '
        )
	for book in books:
                G = book.G
	        G.graph['clustering'] = nx.transitivity(book.G)
	        G.graph['density'] = nx.density(book.G)

                #if (nx.is_connected(G)==True):
                #        G.graph['diameter'] = nx.diameter(book.G)
                #else:
                #        G.graph['diameter'] = '$\infty$'

                (deg_avg, deg_stdev) = degree_stat(G)
                
                # OUTPUT
                ln = book.name + ' & '
                ln += str(G.number_of_nodes()) + ' & '
                ln += str(G.number_of_edges()) + ' & '
                ln += '{0:.2f}'.format(deg_avg) + '$\\pm$' + '{0:.2f}'.format(deg_stdev) + ' & '
                ln += '{0:.3f}'.format(book.G.graph['clustering']) + ' & '
		ln += '{0:.3f}'.format(book.G.graph['density'])
                #ln +=  " & " + str(book.G.graph['diameter'])
                ln += "\\\\ \n"
                        
		f.write(ln)
                
	f.write("\\hline\\end{tabular}}\n")        
	f.close()
        logging.info('- Wrote %s'% fn)

## Ranking frequency
# Character appearance frequency is ranked in the y axis. The scale for
# y axis is logarithmic.
def plot_rank_frequency(books, normalize=True):
        logging.info('Plot rank x frequency...')
        
	fns = ['figure1a.png', 'figure1b.png']
	normalizes = [False, True]

	for k in range(len(fns)):
		fig, ax = plt.subplots()

		for book in books:
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
		ax.set_xlabel('Rank')
		plt.yscale('log')
		ax.set_ylabel('F(r)') # frequency

		plt.rc('legend',fontsize=10)
		ax.legend()
		ax.grid(True)

		plt.savefig(fns[k])
                logging.info('- Wrote %s' % fns[k] )

## Centralities
# Lobby index centrality is calculated using function defined in
# lobby.py.
# Degree, betweenness and closeness centralities are calculated
# using NetworkX. All measures are normalized.
##
def plot_centralities(books):
        logging.info('Plot centralities...')
        
	offset_fig_nr = 1 # figure number starts after 1
	centrs = ["Degree", "Betweenness", "Closeness"]
        
        # PRE-processing
        f = open('lobby.log', 'w') # log file, used to debug the results
	for book in books:
                book.calc_normalized_centralities()
		## Already do the assignment of lobby value to each vertex                
		book.calc_graph_vertex_lobby(f)
        f.close
        
        for book in books:
                G = book.G
                fn = book.name + '-centralities.csv'
                f = open(fn, "w")

                f.write("character;degree;betweenness,closeness;lobby\n");
                for i in range(G.number_of_nodes()):
                        ln = G.node[i]['name'] + ";"
                        ln += '{0:.3f}'.format(G.node[i]['Degree']) + ";"
                        ln += '{0:.3f}'.format(G.node[i]['Betweenness']) + ";"
		        ln += '{0:.3f}'.format(G.node[i]['Closeness']) + ";"
                        ln += '{0:.3f}'.format(G.node[i]['Lobby']) + "\n"
                        f.write(ln)
                f.close()
                logging.info('- Wrote data %s' % fn )
                        
	for c in centrs:
		fn = c + ".png"

		fig, ((ax0, ax1, ax2), (ax3, ax4, ax5), (ax6, ax7, ax8)) = plt.subplots(nrows=3, ncols=3, sharex=True, sharey=True)
                axes = [ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]

		for i in range(len(books)):
                        G = books[i].G
			name = books[i].name
			color = books[i].color
			marker = books[i].marker
			xs = []
			ys = []
                        left = bottom = 100000.0
                        right = top = 0.0
                        
			# load the centrality measures
			for j in range(G.number_of_nodes()):
				x = G.node[j][c]
                                y = G.node[j]['Lobby']

                                xs.append(x)
                                ys.append(y)

			marker_style = dict(linestyle='', color=color, markersize=6)
			axes[i].plot(xs, ys, c=color,
				    marker=marker,
				    label=name,
               			    alpha=0.3, 
				    **marker_style)
		        axes[i].grid(True)

                        if (i>=6 and i<9):
		                axes[i].set_xlabel(c)
                        if (i % 3==0):
		                axes[i].set_ylabel('Lobby')

                        axes[i].text(0.5, 1.1, name,
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=11, color='gray',
                        transform=axes[i].transAxes)

                        # calculate Pearson correlation
                        (r_row, p_value) = pearsonr(xs, ys)
                        print name, r_row, p_value
                        # write Pearson correlation in the plot
                        axes[i].text(.675, .875, '$r=$'+'{0:.3f}'.format(r_row),
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=10, color='black',
                        transform=axes[i].transAxes)
                        
		plt.xscale('log')   			       			       
		plt.yscale('log')
		#plt.legend()
                fig.subplots_adjust(hspace=0)
		plt.tight_layout()
		plt.savefig(fn)
                logging.info('- Wrote plot %s' % fn )

# Graphs for the characters' encounters are drawn for visualization only using
# matplotlib and NetworkX.
def draw_graphs(books):
        logging.info('Drawing graphs...')
        
        for book in books:
                G = book.G
                fn = "g-" + book.name + ".png"

                labels = {}
                for i in range(G.number_of_nodes()):
                        labels[i] = G.node[i]['name'].rstrip("\r")
                
                fig = plt.figure(figsize=(12,12))
                ax = plt.subplot(111)
                ax.set_title('Graph - ' + book.name, fontsize=16)
                pos = nx.spring_layout(G)
                nx.draw(G, pos, node_size=1500, node_color=book.color, font_size=14, font_weight='bold')
                nx.draw_networkx_labels(G, pos, labels, font_size=12)
                plt.tight_layout()
                plt.savefig(fn, format="PNG")
                logging.info('- Wrote %s' % fn )

# The main subroutine declares some attributes associated with the
# books. Those attributes are used to label the books and to
# standardize the pictorial elements properties like color and point
# marker in the plot.
if __name__ == "__main__":
        books = []
	color = {'bible': 'red', 'fiction': 'blue', 'biography': 'darkgreen'}
        flags = 0
        
	acts = {'name': 'acts', 'source':'data', 'color': color['bible'], 'marker': 's'}
	arthur = {'name': 'arthur', 'source':'data', 'color': color['fiction'], 'marker': '>'}
	david = {'name': 'david', 'source':'sgb', 'color': color['fiction'], 'marker': '8'}
	hobbit = {'name': 'hobbit', 'source':'data', 'color': color['fiction'], 'marker': 'p'}
	huck = {'name': 'huck', 'source':'sgb', 'color': color['fiction'], 'marker': 'H'}
	luke = {'name': 'luke', 'source':'data', 'color': color['bible'], 'marker': '8'}
	newton = {'name': 'newton', 'source':'data', 'color': color['biography'], 'marker': 'o'}
	pythagoras = {'name': 'pythagoras', 'source':'data', 'color': color['biography'], 'marker': '^'}
	tolkien = {'name': 'tolkien', 'source':'data', 'color': color['biography'], 'marker': 'd'}
	
	attrs = [acts, arthur, david, hobbit,
	      	 huck, luke, newton,
		 pythagoras, tolkien]

        # process command line arguments
        usage = "usage: %prog [options] arg"
        parser = OptionParser(usage)
        parser.add_option("-a", "--all",
                          help="execute all tasks",
                          action="store_true", dest="all_tasks")
        parser.add_option("-c", "--centralities",
                          help="plot the lobby and other centralities comparisons, generating PNG files",
                          action="store_true", dest="centralities")
        parser.add_option("-d", "--draw-graph",
                          help="draw the graph of characters encounters for visualization generating PNG files",
                          action="store_true", dest="draw_graph")
        parser.add_option("-g", "--global",
                          help="write global measures in a table in a LaTeX file",
                          action="store_true", dest="global_measures")
        parser.add_option("-l", "--legomena",
                          help="Write the frequency of hapax legomena, characters that "
                          +"appear only once in a table in a LaTeX file",
                          action="store_true", dest="hapax_legomena")
        parser.add_option("-r", "--rank",
                          help="plot the ranking of characters frequencies generating the figures 1a and 1b",
                          action="store_true", dest="rank")
        
        (options, args) = parser.parse_args()
        
	for i in range(len(attrs)):
	    cn = Book(attrs[i]['name'], attrs[i]['source'], attrs[i]['color'], attrs[i]['marker'])
	    books.append(cn)

        if options.all_tasks:
                write_global_measures(books)
                write_hapax_legomena_table(books)
                plot_rank_frequency(books)
                plot_centralities(books)
                draw_graphs(books)
        else:
                if options.centralities:
                        plot_centralities(books)
                if options.draw_graph:
                        draw_graphs(books)
                if options.global_measures:
                        write_global_measures(books)
                if options.hapax_legomena:
                        write_hapax_legomena_table(books)
                if options.rank:
                        plot_rank_frequency(books)
