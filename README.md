# Belief Net Independence Solver

This little toy program accepts as input a belief net and then determines if
two nodes are independent, subject to a list of given values.

It uses subgraph monomorphisms to determine a list of "forbidden" triples
through which information cannot flow. It then enumerates a list of all paths
between the two nodes, and checks for the forbidden triples in each path. If
ANY path survives after removing the forbidden triples, then the nodes can
"share" information, and are not independent.

For example, in the following belief net:

```
A -> B;
B -> C;
```

<img src='https://g.gravizo.com/svg?
  digraph G {
    A -> B;
    B -> C;
  }'/>

A and C are NOT independent.

But if B is given then A and C _are_ independent:

<img src='https://g.gravizo.com/svg?
  digraph G {
    A -> B;
    B -> C;
    B [fillcolor=grey, style=filled];
  }'/>

```
A -> B;
B -> C;
B.given = True;
```

In code, this would look like:

```python
>>> import networkx as nx
>>> from beliefnetsolver import BeliefNetIndependenceSolver

>>> graph = nx.DiGraph()
>>> graph.add_edge("A", "B")
>>> graph.add_edge("B", "C")

>>> solver = BayesNetIndependenceSolver(graph)
>>> solver.is_independent("A", "C", givens=[])
False

>>> solver = BayesNetIndependenceSolver(graph)
>>> solver.is_independent("A", "C", givens=["B"])
True
```

This is computed using ["Bayes-ball" rules](https://arxiv.org/ftp/arxiv/papers/1301/1301.7412.pdf).

---

"Forbidden triple" subgraphs are computed using the
[GrandIso](https://github.com/aplbrain/grandiso-networkx) library.
