from abc import ABC

import networkx as nx


class BaseCode(ABC):
    """ Abstract base coding system """

    def __init__(
            self,
            data
    ):
        # TODO: move code info out of graph
        self.graph = nx.DiGraph()
        for k, v in data.items():
            self.graph.add_node(k, **v)
        for k, v in data.items():
            self.graph.add_edge(v['parent_code'], k)
        return
