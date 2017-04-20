from igraph import *

def lobby(G, log_file=None):
    """Lobby or h index
    ================
    
    All graph vertices are traversed and Lobby index is calculated and stored in the lobby macro-field.
    
    If a node has the following list of neighbors sorted by degree:

    ==========  ========
    neighbor     degree
    ==========  ========
    1          21 
    2          18 
    3           4 
    4           3 
    ==========  ========
    
    the Lobby index is 3 because degree $\leq$ neighbor_position. 
    
    """
    lobbies = []

    if (log_file!=None):
        log_file.write('* ' + G.graph['name'] + '\n')
    
    for u in range(G.number_of_nodes()):

        if (log_file):
            log_file.write(G.node[u]['name'] + "\tdegree=" + str(G.degree(u)) + '\n')

        G.node[u]['Lobby'] = lobby = 1 # initialize lobby
        degs = [] # neighbors' degree

        for v in G.neighbors(u):
            degs.append(G.degree(v))
                            
	degs.sort()
        degs.reverse()
	old_idx = idx = 0
        for deg in degs:
            lobby = idx = idx + 1

            if (log_file!=None):
                log_file.write("\t" + str(idx) + "\t" + str(deg) + '\n')

            if (deg < idx):
                lobby = old_idx
                break
            old_idx = idx

            if (log_file!=None):
                log_file.write("Lobby=" + str(lobby) + '\n')

        G.node[u]['Lobby'] = float(lobby) / G.number_of_nodes() # normalize by N vertices
        
        lobbies.append(G.node[u]['Lobby'])

    log_file.flush()
    return lobbies
            
