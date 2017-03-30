from igraph import *

def lobby(graph):
    lobbies = []

    for u in graph.vs:
        print(u['name'] + "\tdegree=" + str(u.degree(mode='out')))

        u['lobby'] = lobby = 1 # initialize lobby
        degs = [] # neighbors' degree

        edges = graph.es.select(_source=u.index)
        for e in edges:
            v = graph.vs[e.target]
            degs.append(v.degree(mode='out'))
                            
	degs.sort()
        degs.reverse()
	old_idx = idx = 0
        for deg in degs:
            lobby = idx = idx + 1
            print("\t" + str(idx) + "\t" + str(deg))

            if (deg < idx):
                u['lobby'] = lobby = old_idx
                break
            old_idx = idx

        print("lobby=" + str(lobby))

        lobbies.append(lobby)

    return lobbies
            
