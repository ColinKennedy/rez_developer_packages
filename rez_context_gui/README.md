- Add default view when no tree item is selected
- CI changes
- Add conflict tree + graphs
 - If no conflict, make sure to still show the tree but with NO children and
   just display nothing

- Add arrow-key expansion

- Preferences
 - Select conflict if available on-start
  - Allow CLI option for that, too

- Implement the "Expand To Non-Conflict" action
- Change the graph to lay out vertically, not horizontally
 - Possibly a toggleable option

- Add color blindness option
- Add more styles - request outline, better visuals, etc

- Add search bar
 - Allow searching by requests, resolved

- Defer as much as possible
 - Do an audit through the code, for performance sake


- Move _gui/ and _generic/ to different Rez packages
- Make modules better named
- Match qtnodes interface (camelCase)
- Dependency trees need to be sensibly layed out so that when nodes are
  expanding, the user doesn't have to manually drag them around
- Fix view margin issue. The graph looks gross
- Need to refresh display after showing nodes - edges are somehow still hidden.
  Maybe the dges aren't showing as expected?

- Add LICENSE for whatever GUI that I use


Features
- graph
 - only show initial nodes
  - right click expand selection
  - expand all
- Add dynamic Qt binding selection, assuming it works
- Add style to the line draw
- Incorporate any other package styling
- Add filter line to auto-select matching package(s)

- https://www.qtcentre.org/threads/38497-QGraphicsItem-visible-in-only-one-QGraphicsView-and-hidden-in-the-other
    - Possibly have intersecting views?
		- Look into this if the GUI turns out to be really slow on big resolves


Todo
- CI changes
- Address all TODO notes
- Make a proper package for qtnodes (or whatever qt library I use)

- Add nice_pylint


node libraries
- https://github.com/cb109/qtnodes#code-example
- https://github.com/LeGoffLoic/Nodz
- https://github.com/dsideb/nodegraph-pyqt


http://www.mupuf.org/blog/2010/07/08/how_to_use_graphviz_to_draw_graphs_in_a_qt_graphics_scene/
https://stackoverflow.com/questions/1494492/graphviz-how-to-go-from-dot-to-a-graph
https://stackoverflow.com/questions/71009811/graphviz-implementation-in-qt
https://stackoverflow.com/questions/1494492/graphviz-how-to-go-from-dot-to-a-graph
https://stackoverflow.com/questions/12102224/drawing-graphs-ala-graphviz-in-qt-via-pyqt4
https://docs.huihoo.com/qt/4.2/graphicsview-elasticnodes.html
http://www.mupuf.org/blog/2010/07/08/how_to_use_graphviz_to_draw_graphs_in_a_qt_graphics_scene/
https://stackoverflow.com/questions/11227115/create-directed-graph-with-movable-nodes-with-qt-boost
http://www.graphviz.org/pdf/cgraph.pdf
https://github.com/nbergont/qgv
