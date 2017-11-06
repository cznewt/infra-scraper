
=====================
Visualization Layouts
=====================

``Graph drawing`` or ``network diagram`` is a pictorial representation of the
vertices and edges of a graph. This drawing should not be confused with the
graph itself, very different layouts can correspond to the same graph. In the
abstract, all that matters is which pairs of vertices are connected by edges.
In the concrete, however, the arrangement of these vertices and edges within a
drawing affects its understandability, usability, fabrication cost, and
aesthetics.

The problem gets worse, if the graph changes over time by adding and deleting
edges (dynamic graph drawing) and the goal is to preserve the user's mental
map.


Conventions
===========

Graphs are frequently drawn as ``node-link diagrams`` in which the vertices
are represented as disks, boxes, or textual labels and the edges are
represented as line segments, polylines, or curves in the Euclidean plane.

Node-link diagrams can be traced back to the 13th century work of Ramon Llull,
who drew diagrams of this type for complete graphs in order to analyze all
pairwise combinations among sets of metaphysical concepts.

Alternative conventions to ``node-link diagrams`` include:

	``Adjacency representations`` such as ``circle packings``, in which vertices
	are represented by disjoint regions in the plane and edges are represented by
	adjacencies between regions.

	``Intersection representations`` in which vertices are represented by non-
	disjoint geometric objects and edges are represented by their intersections.


	``Visibility representations`` in which vertices are represented by regions in
	the plane and edges are represented by regions that have an unobstructed line
	of sight to each other.

	``Confluent drawings``, in which edges are represented as smooth curves within mathematical train tracks.

	``Fabrics``, in which nodes are represented as horizontal lines and edges as vertical lines.

	Visualizations of the ``adjacency matrix`` of the graph.


.. toctree::
   :maxdepth: 2

   layout-arc.rst
   layout-bundle.rst
   layout-force.represented
   layout-hive.rst
   layout-matrix.rst

..   layout-treemap.rst
