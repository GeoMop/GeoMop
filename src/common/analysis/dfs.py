

class DFS:
    def __init__(self, neighbours, previsit=None, postvisit=None, edge_visit=None):
        """
        :param neighbours: callable(vertex) return generator of the vertex neighbours
        :param previsit: callable(vertex)
        :param postvisit: callable(vertex)
        :param edge_visit: callable(out_vtx, in_vtx, edge_index)
          edge_index - is index in the neigbours list of the out_vtx
        """
        self.neighbours = neighbours
        self.previsit = previsit or self.previsit
        self.postvisit = postvisit or self.postvisit
        self.edge_visit = edge_visit or self.edge_visit

    @staticmethod
    def previsit(vertex):
        pass

    @staticmethod
    def postvisit(vertex):
        pass

    @staticmethod
    def edge_visit(vtx_out, vtx_in, i_vtx_in):
        pass

    def run(self, root_list) -> bool:
        """
        Generic DFS. The graph is defined through the neighbours function.
        Vertices can be any objects.
        :param root_list: Main loop vertex iterable.
        :return: False in the case of found cycle.
        """
        closed_vtxs = {}


        neighbours = enumerate(root_list)
        vtx_stack = [(None, neighbours)]
        while vtx_stack:
            out_vtx, neighbours = vtx_stack.pop(-1)
            try:
                i_edge, in_vtx = next(neighbours)
                vtx_stack.append((out_vtx, neighbours))
                if in_vtx is None:
                    # TODO: possibly report missing input
                    continue
                self.edge_visit(out_vtx, in_vtx, i_edge)
                status = closed_vtxs.get(id(in_vtx), None)
                if status is None:
                    # unvisited vertex
                    closed_vtxs[id(in_vtx)] = False
                    self.previsit(in_vtx)
                    neighbours = enumerate(self.neighbours(in_vtx))
                    vtx_stack.append((in_vtx, neighbours))
                elif not status:
                    # open vertex (cycle detected)
                    return False
            except StopIteration:
                if out_vtx is not None:
                    self.postvisit(out_vtx)
                    closed_vtxs[id(out_vtx)] = True
        return True
