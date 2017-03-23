from igraph import *

"""Local class is used to process data of books gathered by the
authors of this project.
"""
class Book(object):

        def __init__(self, name, source='local'):
                """
                Parameter
                ---------
                name: alias assigned to book
                """
                self.name = name

                self.source = source

                self.code_names = None # map code to character names

                self.name_freqs = {} # map character names and their frequencies
                
                self.data_directory = 'data/'
                self.data_file_extension = '.csv'
                self.comment_token = '#'

                if (source=="sgb"):
                        self.data_directory = 'sgb/'
	                self.data_file_extension = '.dat'
                        self.comment_token = '*'

        def create_graph(self):
                if (self.source=="sgb"):
                        return Book.create_graph_from_sgb(self)
                else:
                        return Book.create_graph_from_local_data(self)

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

                return graph
                                
        def create_graph_from_local_data(self):
                """
                Read the SGB file containning characters encounters of a book 
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
                            
			    # add characters encounters linked (adjacency list) in a dictionary
		    for i in range(len(vs)):
			u = vs[i]
                        if (arcs.has_key(u)==False):
			    arcs[u] = []
                                    
			for j in range(i+1, len(vs)):
			    v = vs[j]
			    arcs[u].append(v)
		f.close()

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
                                        
                return Book.fill_graph(self, arcs, name_idxs, next_idx)
        
        
if __name__ == "__main__":
        l = Book('anna', 'sgb')
        g = l.create_graph()
        print(g)
