import matplotlib.pyplot as plt
from igraph import *
from lobby import lobby

"""Local class is used to process data of books gathered by the
authors of this project.
"""
class Book(object):
        FREQ_EXTENSION = ".freq"
        DATA_FILE_EXTENSION = ".dat"
        COMMENT_TOKEN = '*'
        
        def __init__(self, name,
                     data_directory='data',
                     color='black', marker='o',
                     generative_model=True):
                """
                Parameter
                ---------
                name: alias assigned to book
                nr_chars: number of characters
                source: where the project of gathering data for book, 
                        options are: 'local' and 'sgb'
                color: color to be used in the graphics to plot
                marker: marker used in the graphics to differentiate the book data
                """
                # book attributes
                self.name = name
                self.nr_chars = 0

                # data attributes
                self.has_frequency_file = False
                if (self.name == 'hawking'
                    or self.name == 'newton'
                    or self.name == 'pythagoras'):
                        self.has_frequency_file = True
                
                # plot attributes
                self.color = color
                self.marker = marker

                # model properties
                self.generative_model = generative_model
                
                # system properties
                self.data_directory = data_directory

                # data structures
                self.code_names = None # map code to character names
                self.name_freqs = {} # map character names and their frequencies
                self.graph = None

                # graph properties
                self.degs_componentSizes = []
                
                self.create_graph()
                        
        def get_number_characters(self):
                return self.nr_chars

        # _Hapax_ _Legomena_ are words with occurrence frequency equals to one.
        def get_number_hapax_legomenas(self):
                nr_hapaxes = 0
                for name, freq in self.name_freqs.items():
		       	if (freq == 1):
		   		nr_hapaxes += 1

                return nr_hapaxes
        
        def get_graph(self):
                return self.graph
        
        def create_graph(self):
                """
                Read the file containning characters encounters of a book 
                and return a graph.
                Returns
                -------
                igraph graph
                """
                self.code_names = {}
                name_idxs = {}
                next_idx = 0
                arcs = {}
                are_edges = False
                
                fn = self.data_directory+ "/" + self.name + Book.DATA_FILE_EXTENSION
                f = open(fn, "r")
                for ln in f:
		        if (ln.startswith(Book.COMMENT_TOKEN)): # ignore comments
			        continue

                        if (ln.startswith('\n') or ln.startswith('\r')): # edges start after empty line
                                are_edges = True
                                continue
                                
                        if (are_edges==False):
                                (code, charname) = ln.split(' ', 1)
                                self.code_names[code] = charname
                                continue

                        # edges region from here
                        # eg., split "1.2:ST,MR;ST,PH,MA;MA,DO" => ["1.2" , "ST,MR;ST,PH,MA;MA,DO"]
                        (chapter, edges_list) = ln.split(':', 1)

                        # eg., split "ST,MR;ST,PH,MA;MA,DO" => ["ST,MR", "ST,PH,MA", "MA,DO"]
                        edges = edges_list.rstrip("\n").split(';')

                        for e in edges:
                                # eg., split "ST,PH,MA" => ["ST", "PH", "MA"]
                                vs = e.split(',')  # vertices

                                # assign an index to label, if does not exist
                                # otherwise, increment frequency
                                for v in vs:
			                if (name_idxs.has_key(v)==False):
			                        name_idxs[v] = next_idx
			                        next_idx += 1
                                                self.name_freqs[v] = 1
                                        else:
                                                self.name_freqs[v] += 1
                                                
                                # add characters encounters linked (adjacency list) in a dictionary
		                for i in range(len(vs)):
                                        u = vs[i]
                                        if (arcs.has_key(u)==False):
			                        arcs[u] = []
                                    
			                for j in range(i+1, len(vs)):
			                        v = vs[j]
			                        arcs[u].append(v)
		f.close()
                
                self.nr_chars = next_idx

                # Some files in `data/` directory with ".freq" extension contains characters'
                # frequency already counted during data compilation. For the books that
                # don't have this file in `data/`, this file are generated and written
                # in a file with the same extension. The file has the following format:
                
                # ````
                # Sir Isaac Newton;4
                # ````
                
                # where "`;`" is the separator, the first column is the character name and
                # the second the frequency.
                if (self.has_frequency_file==True):
		        self.name_freqs = {}
		        fn = self.data_directory + "/" + self.name + Book.FREQ_EXTENSION

		        f = open(fn, "r")
    	    	        for ln in f:
            		        (vname, freq) = ln.rstrip("\n").split(';')
			        self.name_freqs[vname] = int(freq)
		        f.close()                        

                graph = Graph()

                graph.add_vertices(self.nr_chars)
		
		# name the vertices
		for name, idx in name_idxs.items():
		    	graph.vs[idx]['name'] = name
			
		# add the edges
		for u, vs in arcs.items():
			src = name_idxs[u]
			for v in vs:
			 	dest = name_idxs[v]
				graph.add_edges([(src, dest)]) # TODO: check weights

                                if (self.generative_model==True):
                                        Book.Tick(self, graph)

                self.graph = graph
 

        def calc_graph_vertex_lobby(self):
                lobby(self.graph)

        def Tick(self, graph):
                graph
                deg = 0

                for v in graph.vs:
                        deg += v.degree(mode="out")
                avg = float(deg)/graph.vcount()

                self.degs_componentSizes.append([avg, graph.components().size(0)])

        def calc_normalized_centralities(self):
        	self.graph.as_undirected()

		# DEGREE
		for i in range(len(self.graph.vs)):
            		self.graph.vs[i]["degree"] = float(self.graph.vs[i].degree(mode="out")) / self.graph.vcount()

		# BETWEENNESS
#		cents   = g.betweenness(vertices=None, directed=False, weights='weight')
		self.graph.vs["betweenness"]   = self.graph.betweenness(vertices=None, directed=False)
		for i in range(len(self.graph.vs)):
			self.graph.vs[i]["betweenness"] = float(self.graph.vs[i]["betweenness"] / ((self.graph.vcount()-1)*(self.graph.vcount()-2)/2.0))

		# CLOSENESS
#		cents   = g.closeness(vertices=None, weights='weight')
		self.graph.vs["closeness"]   = self.graph.closeness(vertices=None)
		for i in range(len(self.graph.vs)):
			self.graph.vs[i]["closeness"] = self.graph.vs[i]["closeness"]
                
def plot_degree_componentSize(books):
        fn = 'giant.png'
        
	fig, ax = plt.subplots()

	for book in books:
	    	g = book.graph
		name = book.name
		color = book.color
		marker = book.marker
		xs = []
		ys = []
	                
                for elem in book.degs_componentSizes:
                        xs.append(elem[0])
			ys.append(elem[1])
		
			marker_style = dict(linestyle=':', color=color, markersize=6)
                ax.plot(xs, ys, c=color,
			marker=marker,
                        label=name,
               		alpha=0.3, 
                        **marker_style)

 #       plt.xscale('log')
        ax.set_xlabel('w')
 #       plt.yscale('log')
	ax.set_ylabel('size') # frequency

	plt.rc('legend',fontsize=10)
	ax.legend()
	ax.grid(True)

	plt.savefig(fn)
	print("INFO: Wrote plot in " + fn)

                
if __name__ == "__main__":
        anna = Book('anna', 'sgb', '.dat', 'blue')
        acts = Book('acts', 'data', '.dat', 'red')
        david = Book('david', 'sgb', '.dat', 'cyan')
        huck = Book('huck', 'sgb', '.dat', 'brown')
        luke = Book('luke', 'data', '.dat', 'green')
        books = [acts, anna, david, huck, luke]
        plot_degree_componentSize(books)
