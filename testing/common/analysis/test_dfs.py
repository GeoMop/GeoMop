import pytest
from common.analysis import dfs

class GraphDFS:
    def __init__(self, n_vtx):
        self.time = 0
        self.time_in = [-1]*n_vtx
        self.time_out = [-1]*n_vtx

    def previsit(self, vtx):
        self.time_in[vtx] = self.time
        self.time += 1

    def postvisit(self, vtx):
        self.time_out[vtx] = self.time
        self.time += 1


def test_dfs():
    graph = [
        [1, 2],     #0
        [3, 2, 4],     #1
        [3],        #2
        [5],        #3
        [5],        #4
        []          #5
    ]



    graph_dfs = GraphDFS(len(graph))
    is_dag = dfs.DFS(neighbours=lambda vtx, g=graph: iter(g[vtx]),
                     previsit=graph_dfs.previsit,
                     postvisit=graph_dfs.postvisit).run([0])
    assert is_dag
    print(graph_dfs.time_in)
    print(graph_dfs.time_out)
    ref_in = [0,1,6,2,8,3]
    assert graph_dfs.time_in == ref_in
    ref_out = [11,10,7,5,9,4]
    assert graph_dfs.time_out == ref_out