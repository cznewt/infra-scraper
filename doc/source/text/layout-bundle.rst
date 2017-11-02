
==========================
Hierarchical Edge Bundling
==========================

A compound graph is a frequently encountered type of data set. Relations are
given between items, and a hierarchy is defined on the items as well.
Hierarchical Edge Bundling is a new method for visualizing such compound
graphs. Our approach is based on visually bundling the adjacency edges, i.e.,
non-hierarchical edges, together. We realize this as follows. We assume that
the hierarchy is shown via a standard tree visualization method. Next, we bend
each adjacency edge, modeled as a B-spline curve, toward the polyline defined
by the path via the inclusion edges from one node to another. This
hierarchical bundling reduces visual clutter and also visualizes implicit
adjacency edges between parent nodes that are the result of explicit adjacency
edges between their respective child nodes. Furthermore, hierarchical edge
bundling is a generic method which can be used in conjunction with existing
tree visualization techniques.


Sample Visualizations
=====================

.. figure:: ../static/img/hiearchical-edge-bundling.png
    :width: 100%
    :figclass: align-center

    Hierarchical edge bundling of SaltStack services and their relations (cca 100 nodes)


More Information
================

* http://www.win.tue.nl/vis1/home/dholten/papers/bundles_infovis.pdf
* https://www.win.tue.nl/vis1/home/dholten/papers/forcebundles_eurovis.pdf
