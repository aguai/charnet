from igraph import *
from lobby import lobby

"""Local class is used to process data of books gathered by the
authors of this project.
"""
class Book(object):
        def __init__(self, name, source='local', color='black', marker='o', generative_model=True):
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
                self.source = source

                # data attributes
                self.has_frequency_file = False
                if (self.source == 'hawking'
                    or self.source == 'newton'
                    or self.source == 'pythagoras'):
                        self.has_frequency_file = True
                
                # plot attributes
                self.color = color
                self.marker = marker

                # model properties
                self.generative_model = generative_model
                
                # system properties
                self.data_directory = 'data/'
                self.data_file_extension = '.csv'
                self.comment_token = '#'

                # data structures
                self.code_names = None # map code to character names
                self.name_freqs = {} # map character names and their frequencies
                self.graph = None
                
                if (source=="sgb"):
                        self.data_directory = 'sgb/'
	                self.data_file_extension = '.dat'
                        self.comment_token = '*'

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
                if (self.source=="sgb"):
                        self.graph = Book.create_graph_from_sgb(self)
                else:
                        self.graph = Book.create_graph_from_local_data(self)

        def fill_graph(self, arcs, name_idxs, nr_vertices):
                graph = Graph()

                graph.add_vertices(nr_vertices)
		
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

                return graph
                                
        def create_graph_from_local_data(self):
                """
                Read the authors file containning characters encounters of a book 
                and return a graph.
                Returns
                -------
                igraph graph
                """
                arcs = {}
                name_idxs = {}
                next_idx = 0
                
                fn = self.data_directory + self.name + self.data_file_extension
		f = open(fn, "r")
    	    	for ln in f:
		        if (ln.startswith(self.comment_token)): # ignore comments
			        continue
		    
		        vs = ln.rstrip("\n").split(';')

		        # Trim quotation marks and assign an index to character's name
		        for v in vs:
			        v = v.strip("\"")
			        if (name_idxs.has_key(v)==False):
			                name_idxs[v] = next_idx
			                next_idx += 1
                                print(v)
                                # count the characters
                                if(self.name_freqs.has_key(v)==False):
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
		        fn = self.data_directory + self.name + FREQ_EXTENSION

		        f = open(fn, "r")
    	    	        for ln in f:
            		        (vname, freq) = ln.rstrip("\n").split(';')
			        self.freqs[vname] = int(freq)
		        f.close()                        

                self.nr_chars = next_idx
                
                return Book.fill_graph(self, arcs, name_idxs, next_idx)

        def create_graph_from_sgb(self):
                """
                Read the SGB file containning characters encounters of a book 
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
                
                fn = self.data_directory + self.name + self.data_file_extension
                f = open(fn, "r")
                for ln in f:
		        if (ln.startswith(self.comment_token)): # ignore comments
			        continue

                        if (ln.startswith('\n')): # edges start after empty line
                                are_edges = True
                                continue
                                
                        if (are_edges==False):
                                (code, charname) = ln.split(' ', 1)
                                self.code_names[code] = name
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
                
                return Book.fill_graph(self, arcs, name_idxs, next_idx)

        def calc_graph_vertex_lobby(self):
                lobby(self.graph)


        def Tick(self, graph):
                graph
                deg = 0

                for v in graph.vs:
                        deg += v.degree(mode="out")
                avg = float(deg)/graph.vcount()

                print(str(avg) + "\t" + str(graph.components().size(0)))
                
if __name__ == "__main__":
#        l = Book('anna', 'sgb')
        l = Book('acts')
        g = l.get_graph()
        #print(g)
