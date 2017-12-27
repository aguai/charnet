#!/usr/bin/python
from optparse import OptionParser
import logging
import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pygraphviz as pgv

from book import *

# to calculate Pearson correlation
from scipy.stats.stats import pearsonr

# INIT
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

def __raw_format_book_label(name):
        return name.title()
        
def __format_book_label(name):
        """Format the label of the book to print in table or plot.
        """
        return '\emph{' + name.title() + '}'

def __pre_process_centralities(books):
        """
        Calculate centralities and store in associative array.
        """
        # PRE-processing
        f = open('lobby.log', 'w') # log file, used to debug the results
	for book in books:
                book.calc_normalized_centralities()
		## Already do the assignment of lobby value to each vertex                
		book.calc_graph_vertex_lobby(f)
        f.close

def write_hapax_legomena_table(books):
        """"Hapax Legomena The write_hapax_legomena_table() function write the
        _Hapax_ frequency to be included in the paper using LaTeX
        syntax for tables.
        """
	fn = 'legomenas.tex'

	f = open(fn, "w")
	f.write("\\begin{tabular}{l|c|c}\hline \n")
	f.write("\\bf Book &  $\\bf HL^N=H/N$ & $\\bf DL^N=DL/N$ \\\\ \hline \n")
	
	# count the lapaxes for each book
	for book in books:
		nr_hapaxes = book.get_number_hapax_legomenas()
                nr_dis = book.get_number_dis_legomenas()                
                nr_chars = book.get_number_characters()

                ln = __format_book_label(book.name) + " & "
                ln += '{0:02d}'.format(nr_hapaxes) + "/"
                ln += '{0:02d}'.format(nr_chars) + " = "
                ln += '{0:.3f}'.format(float(nr_hapaxes)/nr_chars) 
                ln += ' & '
                ln += '{0:02d}'.format(nr_dis) + "/"
                ln += '{0:02d}'.format(nr_chars) + " = "
                ln += '{0:.3f}'.format(float(nr_dis)/nr_chars) 
                ln +=" \\\\\n"
                
		f.write(ln)

	f.write("\hline\end{tabular}\n")
	f.close()
        logging.info('- Wrote %s'% fn)

def __degree_stat(G):
        """Calculate the average degree and the standard deviation degree.
        Source: http://holanda.xyz/files/mean.c
        """
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

def _plot_density(books):
        fn = 'fig_density.pdf'
        Ds = []
        xticklabels = []
        
        f = open(fn, "w")

        for book in books:
                G = book.G

                D = nx.density(G)

                # OUTPUT
                xticklabels.append(__raw_format_book_label(book.name))
                Ds.append(D)

        fig, ax = plt.subplots()
        N = len(books)
        ind = np.arange(N)  # the x locations for the groups
        width = 0.35       # the width of the bars
        rects = ax.bar(ind, tuple(Ds), width, color='0')


        # add some text for labels, title and axes ticks
        ax.set_ylabel('Density')
        ax.set_title('')
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(tuple(xticklabels), fontsize=6)
        plt.savefig(fn)

        logging.info('- Wrote %s'% fn)


def write_global_measures(books):
        """Global measures for each character network are written as a table and
        included in a LaTeX file named `global.tex` to be included in the
        manuscript.
        Clustering coefficient is calculated using _NetworkX_ library
        [average clustaring]https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.algorithms.cluster.average_clustering.html#networkx.algorithms.cluster.average_clustering
        routine.  We also calculate
        [density](https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.classes.function.density.html).
        """
        logging.info('Writing global measures...')
        
	fn = 'global.tex'

	f = open(fn, "w")

	f.write('{\small\\begin{tabular}{l|c|c|c|c|c}\\hline\n')
	f.write('\\bf\\hfil Book\\hfil '
                + ' & \\bf\\hfil N\hfil '
                + ' & \\bf\\hfil Links\hfil '
                + ' & \\hfil $\\bf K  $\\hfil '
                + ' & \\hfil $\\bf CC $\\hfil '
		+ ' \\\\ \\hline\n '
        )
	for book in books:
                G = book.G
	        G.graph['clustering'] = nx.average_clustering(book.G)
	        G.graph['density'] = nx.density(book.G)

                (deg_avg, deg_stdev) = __degree_stat(G)
                
                # OUTPUT
                ln = __format_book_label(book.name) + ' & '
                ln += str(G.number_of_nodes()) + ' & '
                ln += str(G.number_of_edges()) + ' & '
                ln += '{0:.2f}'.format(deg_avg) + '$\\pm$' + '{0:.2f}'.format(deg_stdev) + ' & '
                ln += '{0:.3f}'.format(book.G.graph['clustering']) + ' & '
                ln += "\\\\ \n"
                        
		f.write(ln)
                
	f.write("\\hline\\end{tabular}}\n")        
	f.close()
        logging.info('- Wrote %s'% fn)

        _plot_density(books)

def plot_rank_frequency(books, normalize=True):
        """Ranking frequency Character appearance frequency is ranked in the
        y axis. The scale for y axis is logarithmic.
        """
        logging.info('Plotting rank x frequency...')
        
	fns = ['figure1a.pdf', 'figure1b.pdf']
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
			        label=name.title(),
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

def plot_centralities(books):
        """Centralities Lobby index centrality is calculated using function
        defined in lobby.py.  Degree, betweenness and closeness centralities
        are calculated using NetworkX. All measures are normalized.
        """
        logging.info('Plotting centralities...')
        
	offset_fig_nr = 1 # figure number starts after 1
	centrs = ["Assortativity", "Betweenness", "Closeness", "Degree", "Lobby"]

        fn = "Figure1.pdf"
        
	fig, ((ax0, ax1, ax2), (ax3, ax4, ax5), (ax6, ax7, ax8)) = plt.subplots(nrows=3, ncols=3)
        axes = [ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]

        for b in books:
                b.avg['Assortativity'] = nx.degree_assortativity_coefficient(b.G)
                b.avg['Betweenness'] = b.get_avg_betweenness()
                b.avg['Closeness'] = b.get_avg_closeness()
                b.avg['Degree'] = b.get_avg_degree()
                b.avg['Lobby'] = b.get_avg_lobby()

        k = 0
	for i in range(len(centrs)-1):
                for j in range(i+1, len(centrs)):

                        #left = bottom = 100000.0
                        #right = top = 0.0

			marker_style = dict(linestyle='', markersize=6)
                        for b in books:
                                x = b.avg[centrs[i]]
                                y = b.avg[centrs[j]]
                        	axes[k].plot(x, y, c = b.color,
				     marker = b.marker,
				     label=b.name,
               			     alpha=0.3,
				    **marker_style)
		        axes[k].grid(True)
                        
		        axes[k].set_xlabel(centrs[i])
                        axes[k].set_ylabel(centrs[j])

                        axes[k].text(0.5, 1.1, '' ,
                                     style='italic',
                                     horizontalalignment='center',
                                     verticalalignment='center',
                                     fontsize=8, color='gray',
                                     transform=axes[i].transAxes)

                        if k==0:
                                axes[k].legend(loc='upper right', fontsize=4)
                        
                        # fix number colision problems
                        if centrs[i] == 'Assortativity':
                                start, end = axes[k].get_xlim()
                                axes[k].xaxis.set_ticks(numpy.arange(start, end, 0.1))
                        elif centrs[i] == 'Betweenness':
                                start, end = axes[k].get_xlim()
                                axes[k].xaxis.set_ticks(numpy.arange(start, end, 0.02))
                        elif centrs[i] == 'Closeness':
                                start, end = axes[k].get_xlim()
                                axes[k].xaxis.set_ticks(numpy.arange(start, end, 0.1))
                        else: # Degree
                                start, end = axes[k].get_xlim()
                                axes[k].xaxis.set_ticks(numpy.arange(start, end, 0.05))
                        # calculate Pearson correlation
                        #  (r_row, p_value) = pearsonr(xs, ys)
                        #  print name, r_row, p_value
                        # write Pearson correlation in the plot
                        # axes[i].text(.675, .875, '$r=$'+'{0:.3f}'.format(r_row),
                        # horizontalalignment='center',
                        # verticalalignment='center',
                        # fontsize=10, color='black',
                        # transform=axes[i].transAxes)
                        k = k + 1
                        if k == 8:
                                break
		#plt.xscale('log')   			       			       
		#plt.yscale('log')
		#plt.legend()
      
        fig.subplots_adjust(hspace=0)
	plt.tight_layout()
	plt.savefig(fn)
        logging.info('- Wrote plot %s', fn)

def stat_centralities(books):
        """
        Calculate the mean and deviation for centralities for each book.
        """
        fn = 'centr.tex'
        f = open(fn, "w")

        centrs = ['Degree', 'Betweenness', 'Closeness', 'Lobby']

        __pre_process_centralities(books)

        f.write("\\begin{tabular}{c|c|c|c|c}\hline\n")
        f.write("Book & Degree & Betweenness & Closeness & Lobby \\\ \hline \n");
        for book in books:
                f.write(__format_book_label(book.name) + ' & ')
                G = book.G
                for centr in centrs:
                        vals = []
                        for i in range(G.number_of_nodes()):
                                vals.append(G.node[i][centr])

                        m = numpy.mean(numpy.array(vals))
                        std = numpy.std(numpy.array(vals))
                        f.write('${0:.3f}'.format(m) + ' \pm ' '{0:.3f}'.format(std) + '$ ')
                        if centr != 'Lobby':
                                f.write(' & ')
                        else:
                                f.write(' \\\ ')
                                if book.name == 'tolkien' and centr == 'Lobby':
                                        f.write(' \hline')
                f.write('\n')
        f.write('\\end{tabular} \n')
        logging.info('- Wrote %s', fn)
        f.close()
                
def draw_graphs(books):
        """Graphs for the characters' encounters are drawn for visualization
        only using matplotlib and NetworkX.
        
        """
        logging.info('Drawing graphs...')
        
        for book in books:
                G = book.G
                fn = "g-" + book.name + ".png"

                labels = {}
                for i in range(G.number_of_nodes()):
                        labels[i] = G.node[i]['name'].rstrip("\r")
                
                fig = plt.figure(figsize=(12,12))
                ax = plt.subplot(111)
                ax.set_title('Graph - ' + book.name.title(), fontsize=16)
                pos = nx.spring_layout(G)
                nx.draw(G, pos, node_size=1500, node_color=book.color, font_size=14, font_weight='bold')
                nx.draw_networkx_labels(G, pos, labels, font_size=12)
                plt.tight_layout()
                plt.savefig(fn, format="PNG")
                logging.info('- Wrote %s' % fn )

if __name__ == "__main__":
        """The main subroutine declares some attributes associated with the
        books. Those attributes are used to label the books and to
        standardize the pictorial elements properties like color and point
        marker in the plot.
        
        """
        books = []
        flags = 0
        
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
        parser.add_option("-s", "--stat-centralities",
                          help="generate statistics from centralities",
                          action="store_true", dest="stat")
        
        (options, args) = parser.parse_args()
        
	books = Book.get_books()

        if options.all_tasks:
                write_global_measures(books)
                write_hapax_legomena_table(books)
                plot_rank_frequency(books)
                plot_centralities(books)
                draw_graphs(books)
                stat_centralities(books)
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
                if options.stat:
                        stat_centralities(books)
                        
