import networkx as nx

from typing import List, Tuple
import grandiso


def _is_subtuple(t: Tuple[str, ...], s: Tuple[str, ...]) -> bool:
    """
    Returns true if t is a subtuple of s.

    For example, ("A", "B", "E") is a subtuple of ("A", "B", "E", "D", "E"),
    but not of ("A", "B", "C", "D", "E").
    """
    # short-term hack: assume all items are single-character strings.
    return "".join(t) in "".join(s)


class BayesNetIndependenceSolver:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def is_independent(self, a: str, b: str, givens: List[str] = None) -> bool:
        """
        Returns True if a and b are independent given givens.
        """
        givens = givens or []

        # Determine if a and b are independent given a list of nodes:
        # There are rules (Bayes-ball) to determine if a and b are independent.

        # 1. If x->y and x->z and x,y,z are NOT given, info can flow from z to y and back.
        # 2. If x->y and x->z and x is given, info can NOT flow.
        # 3: If n->m and p->m and n,p,m are NOT given, info CANNOT flow from p to n and back.
        # 4: If n->m and p->m and n is given, info CAN flow from p to n and back.
        # 5: If d->e and e->f and d,e,f are NOT given, info CAN flow.
        # 6: If d->e and e->f and e is given, info CANOT flow.

        # So we need to get ALL paths from a to b, and then make sure we can
        # get from a to b without going through a forbidden triple.

        # Get all paths from a to b:
        paths = list(nx.all_simple_paths(nx.Graph(self.graph), a, b))

        # Get all forbidden triples:
        forbidden_triples = self.get_inactive_triples(givens)

        # Check if any forbidden triples show up in any of the paths:

        communicationable_path_count = 0
        for path in paths:
            for triple in forbidden_triples:
                if _is_subtuple(triple, path):
                    print(f"{path} not active, {triple} is forbidden.")
                    break
            else:
                # No forbidden triple found in this path.
                # So this path can communicate data. Tf, not indep.
                print(f"{path} is active because no forbidden triple found.")
                return False

        # If there are no valid paths, then a and b are independent.
        print(["".join(p) for p in paths])
        return True

    def get_inactive_triples(self, givens: List[str]) -> Tuple[str, str, str]:
        """
        Information cannot pass through an inactive triple.
        """
        # create a working copy of the graph:
        working_graph = self.graph.copy()

        # set all nodes' given attr:
        for node in working_graph.nodes:
            working_graph.nodes[node]["given"] = node in givens

        forbidden_triples = []

        # "givens" contains a list of given nodes.
        # there are three forbidden triple types:

        # 1. x->y and x->z and x is given
        motif = nx.DiGraph()
        motif.add_edge("x", "y")
        motif.add_edge("x", "z")
        motif.add_node("x", given=True)
        motif.add_node("y")
        motif.add_node("z")

        forbidden_triples.extend(
            [
                (motif["y"], motif["x"], motif["z"])
                for motif in grandiso.find_motifs(motif, working_graph)
            ]
        )

        # 3. x->y and y->z and y is Given
        motif = nx.DiGraph()
        motif.add_edge("x", "y")
        motif.add_edge("y", "z")
        # motif.add_node("x", given=False)
        motif.add_node("x")
        motif.add_node("y", given=True)
        # motif.add_node("z", given=False)
        motif.add_node("z")

        forbidden_triples.extend(
            [
                (motif["x"], motif["y"], motif["z"])
                for motif in grandiso.find_motifs(motif, working_graph)
            ]
        )
        forbidden_triples.extend(
            [
                (motif["z"], motif["y"], motif["x"])
                for motif in grandiso.find_motifs(motif, working_graph)
            ]
        )

        # 2. x->z and y->z and none are given
        # to do this one, backprop all descendants of z if they are given.

        # for all nodes in the graph;
        for node in working_graph.nodes:
            # if the node is given, then backprop its descendants:
            if working_graph.nodes[node]["given"]:
                # get the immediate predeceesors of this node:
                predecessors = list(working_graph.predecessors(node))
                # for each predecessor, set its given attr to True:
                for predecessor in predecessors:
                    working_graph.nodes[predecessor]["given"] = True

        motif = nx.DiGraph()
        motif.add_edge("x", "z")
        motif.add_edge("y", "z")
        motif.add_node("z", given=False)
        motif.add_node("x")
        motif.add_node("y")

        forbidden_triples.extend(
            [
                (motif["x"], motif["z"], motif["y"])
                for motif in grandiso.find_motifs(motif, working_graph)
            ]
        )

        return forbidden_triples
