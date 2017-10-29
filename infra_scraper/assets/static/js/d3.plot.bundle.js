var RelationalPlot = function(RelationalPlot){
    /**
     * Hierarchical edge bundling rendering method
     * @param dataUrl - Data endpoint URL
     * @param graphSelector - Graph parent <div> CSS selector
     * @param refreshInterval - Refresh interval in seconds (null for disabled)
     */
    RelationalPlot.hierarchicalEdgeBundling = function(dataUrl, graphSelector, refreshInterval) {
        var contentWidth = $(graphSelector).innerWidth(),
            diameter = contentWidth,
            radius = diameter / 2,
            innerRadius = radius - 120;

        var line_color = function(d){
                var color = "#C7C7C7";
                if(d.hasOwnProperty("source") && d.hasOwnProperty("target")){
                    d.source.relations.forEach(function(item){
                        if(item.status === "success"){
                            color = "#00BB00";
                        }else if(item.status === "failed"){
                            color = "#FF0000";
                        }
                    });
                }
                return color;
            },
            cross = function(a, b) {
                return a[0] * b[1] - a[1] * b[0];
            },
            dot = function(a, b) {
                return a[0] * b[0] + a[1] * b[1];
            },
            mouseCoordinates = function(e) {
                return [e.pageX - rx, e.pageY - ry];
            },
            graph = this;

        this._data = {};

        this.init = function(alreadyRunning) {
            if(!dataUrl || !graphSelector){
                throw new Error("Cannot init graph, dataUrl or graphSelector not defined");
            }

            graph.cluster = d3.cluster()
                .size([360, innerRadius]);

            graph.line = d3.radialLine()
                .curve(d3.curveBundle.beta(0.85))
                .radius(function(d) { return d.y; })
                .angle(function(d) { return d.x / 180 * Math.PI; });

            if(alreadyRunning && graph.svg) {
//                graph.svg.remove();
            }

            graph.svg = d3.select(graphSelector).append("svg")
                .attr("width", diameter)
                .attr("height", diameter)
              .append("g")
                .attr("transform", "translate(" + radius + "," + radius + ")");

            graph.link = graph.svg.append("g").selectAll(".link");
            graph.node = graph.svg.append("g").selectAll(".node");

            if(!alreadyRunning){
                graph.requestData(dataUrl, graph.render);
                $(window).on('resize', function(ev){
                    graph.init(true);
                    graph.render();
                });

                if(refreshInterval){
                    setInterval(function(){
                        graph.requestData(dataUrl, function(){
                            graph.init(true);
                            graph.render();
                        });
                    }, refreshInterval * 1000);
                }
            }
        };

        this.render = function() {
            if(graph._data && graph._data.length > 0){

                var root = relationalPlotHelpers.nodeHierarchy(graph._data)
                    .sum(function(d) { return d.size; });

                graph.cluster(root);
                graph.link = graph.link
                  .data(relationalPlotHelpers.nodeRelations(root.leaves()))
                  .enter().append("path")
                    .each(function(d) { d.source = d[0], d.target = d[d.length - 1]; })
                    .attr("class", "link")
                    .attr("d", graph.line);

                graph.node = graph.node
                  .data(root.leaves())
                  .enter().append("text")
                    .attr("class", "node")
                    .attr("dy", "0.31em")
                    .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + (d.y + 8) + ",0)" + (d.x < 180 ? "" : "rotate(180)"); })
                    .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
                    .text(function(d) { return d.data.key; });
            }
        };

        this.requestData = function(dataUrl, callback){
            d3.json(dataUrl, function(res){
                graph._data = res.resources;
                relationalPlotHelpers.displayResources(Object.keys(graph._data).length);
                //relationalPlotHelpers.displayRelations();
                relationalPlotHelpers.displayScrapeTime(res.date);
                if(typeof callback === 'function'){
                    callback();
                }
            });
        };

        this.findStartAngle = function(children) {
            var min = children[0].x;
            children.forEach(function(d) {
                if (d.x < min)
                    min = d.x;
            });
            return min;
        };

        this.findEndAngle = function(children) {
            var max = children[0].x;
            children.forEach(function(d) {
                if (d.x > max)
                    max = d.x;
            });
            return max;
        };

    };
    return RelationalPlot;
}(RelationalPlot || {});
