import matplotlib.pyplot as plt
import networkx as nx
from lobby import lobby

class Book(object):
        """Local class is used to process data of books gathered by the
        authors of this project.
        
        """
        FREQ_EXTENSION = ".freq"
        DATA_FILE_EXTENSION = ".dat"
        COMMENT_TOKEN = '*'
        color = {'bible': 'black', 'fiction': 'grey', 'biography': 'black'}
        
        @classmethod
        def get_books(cls):
                acts = Book('acts', 'data', cls.color['bible'], '+')
                arthur = Book('arthur', 'data',  cls.color['fiction'], '^')
                david = Book('david', 'sgb', cls.color['fiction'], 'v')
                dick = Book('dick', 'data', cls.color['biography'], 'o')
                hawking = Book('hawking', 'data', cls.color['biography'], 'o')
                hobbit = Book('hobbit', 'data',  cls.color['fiction'], 'p')
                huck = Book('huck', 'sgb', cls.color['fiction'], 's')
                luke = Book('luke', 'data', cls.color['bible'], 'x')
                newton = Book('newton', 'data',  cls.color['biography'],  '.')
                pythagoras = Book('pythagoras', 'data',  cls.color['biography'], '*')
                tolkien = Book('tolkien', 'data', cls.color['biography'], 'd')
                
                books = [acts, arthur, david, dick, hawking, hobbit, huck, luke, newton, pythagoras, tolkien]

                return books
        
        def __init__(self, name,
                     data_directory='data',
                     color='black', marker='o',
                     generative_model=True):
                """
                Parameter
                ---------
                name: alias assigned to book
                data_directory: where data file is stored
                nr_chars: number of characters
                color: color to be used in the graphic to plot
                marker: marker used in the graphic to distinguish the book data
                generative_model: as nodes are added to graph, compute some measures
                on-the-fly and store them.
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
                self.G = None

                # load the average
                self.avg = {}
                
                # graph properties
                self.degs_componentSizes = []
                
                self.create_graph()
                        
        def get_number_characters(self):
                return self.nr_chars

        def get_number_hapax_legomenas(self):
                """
                _Hapax_ _Legomena_ are words with occurrence frequency equals to one.
                """
                nr_hapaxes = 0
                for name, freq in self.name_freqs.items():
		       	if (freq == 1):
		   		nr_hapaxes += 1

                return nr_hapaxes

        def get_number_dis_legomenas(self):
                """
                _Dis_ _Legomena_ are words with occurrence frequency equals to two.
                """
                nr_dis = 0
                for name, freq in self.name_freqs.items():
		       	if (freq == 2):
		   		nr_dis += 1

                return nr_dis
        
        def get_graph(self):
                return self.G
        
        def create_graph(self):
                """
                Read the file containning characters encounters of a book 
                and return a graph.
                
                Returns
                -------
                networkx graph
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

                G = nx.Graph()
                G.graph['name'] = self.name
                
		# name the vertices
		for name, idx in name_idxs.items():
		    	G.add_node(idx, name=name)
			
		# add the edges
		for u_name, vs in arcs.items():
			u = name_idxs[u_name]
			for v_name in vs:
			 	v = name_idxs[v_name]

                                if (G.has_edge(u, v)==True): # increase weight
                                        G[u][v]['weight'] += 1
                                else: # add edge with weight = 1
                                        G.add_edge(u, v, weight=1)
                                
                                if (self.generative_model==True):
                                        Book.Tick(self, G)

                self.G = G

        def calc_graph_vertex_lobby(self, log_file=None):
                lobby(self.G, log_file)

        def get_avg_lobby(self, log_file=None):
                '''Return the average Lobby index of the book characters'''
                lobby(self.G, log_file)
                acc = 0.0
                N = self.G.number_of_nodes()
		for i in range(N):
                        acc = acc + self.G.node[i]['Lobby']

                return float(acc) / N

        def get_avg_degree(self):
                '''Return the average degree of the book characters'''
                acc = 0.0
                N = self.G.number_of_nodes()
                degs = nx.degree_centrality(self.G)
		for i in range(N):
                        acc = acc + degs[i]

                return float(acc) / N

        def get_avg_betweenness(self):
                '''Return the average betweenness of the book characters'''
                acc = 0.0
                N = self.G.number_of_nodes()
		bets = nx.betweenness_centrality(self.G)
		for i in range(N):
			acc =  acc + bets[i]

                return acc / N

        def get_avg_closeness(self):
                '''Return the average closeness of the book characters'''
                acc = 0.0
                N = self.G.number_of_nodes()
                closes = nx.closeness_centrality(self.G)
                for i in range(N):
		        acc = acc + closes[i]

                return acc / N
        
        def calc_normalized_centralities(self):
		# DEGREE
                degs = nx.degree_centrality(self.G)                
		for i in range(self.G.number_of_nodes()):
                        self.G.node[i]['Degree'] = degs[i]

		# BETWEENNESS
		bets = nx.betweenness_centrality(self.G)
		for i in range(self.G.number_of_nodes()):
			self.G.node[i]['Betweenness'] = bets[i]

		# CLOSENESS - already normalized
                closes = nx.closeness_centrality(self.G)
                for i in range(self.G.number_of_nodes()):
		        self.G.node[i]['Closeness']   = closes[i]
                        
        def Tick(self, G):
                G
                deg = 0

                for i in range(G.number_of_nodes()):
                        deg += G.degree(i)
                avg = float(deg)/G.number_of_nodes()

                # TODO COMPONENT
                #self.degs_componentSizes.append([avg, G.components().size(0)])

