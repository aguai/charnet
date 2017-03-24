from igraph import *

def lobby(graph):
    lobbies = []

    for u in graph.vs:
        lobby = 1 # initialize lobby
        vdegs = [] # neighbors' degree

        edges = graph.es.select(_source=u.index)
        for e in edges:
            v = graph.vs[e.target]
            vdegs.append(v.degree(mode='out'))
                            
	vdegs.sort()
        vdegs.reverse()
	old_vdeg = -1
	idx = 0
        for vdeg in vdegs:
            # Ignore repetition of degrees
            if (vdeg != old_vdeg):
                idx = idx + 1
            	if (vdeg <= idx):
                    u['lobby'] = lobby = vdeg
                    break
            old_deg = vdeg

	    lobbies.append(lobby)

    return lobbies
            
            
