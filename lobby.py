from igraph import *

def lobby(G):
    lobbies = []

    for u in range(G.number_of_nodes()):
        #print(u['name'] + "\tdegree=" + str(u.degree(mode='out')))

        G.node[u]['lobby'] = lobby = 1 # initialize lobby
        degs = [] # neighbors' degree

        for v in G.neighbors(u):
            degs.append(G.degree(v))
                            
	degs.sort()
        degs.reverse()
	old_idx = idx = 0
        for deg in degs:
            lobby = idx = idx + 1
#            print("\t" + str(idx) + "\t" + str(deg))

            if (deg < idx):
                lobby = old_idx
                break
            old_idx = idx

        #print("lobby=" + str(lobby))

        G.node[u]['lobby'] = float(lobby) / G.number_of_nodes() # normalize by N vertices
        
        lobbies.append(G.node[u]['lobby'])

    return lobbies
            
