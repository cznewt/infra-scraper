var RelationalPlot = function(RelationalPlot){
    /**
     * Tree map render method
     * @param dataUrl - URL to data endpoint
     * @param graphSelector - CSS selector of graph parent div
     * @param refreshInterval - Refresh interval in seconds (can be null, means refresh disabled)
     */
    RelationalPlot.treeMap = function(dataUrl, graphSelector, refreshInterval){
      var contentWidth = $(graphSelector).innerWidth(),
          width = contentWidth,
          height = 500,
          positioningMagicNumber = -105,
          //var fill = d3.scale.ordinal()      .range(["#f0f0f0", "#d9d9d9", "#bdbdbd"]);
          fill = d3.scaleCategory20,
          stroke = d3.scaleLinear().domain([0, 1e4]).range(["brown", "steelblue"]),
          graph = this;
      this._data = {};
      this.init = function(reinit){
          graph.treemap = d3.layout.treemap()
              .size([width, height])
              .value(function(d) { return d.service.length });

          graph.bundle = d3.layout.bundle();

          if(reinit && graph.div){
             graph.div.remove();
          }
          graph.div = d3.select(graphSelector).append("div")
              .style("position", "relative")
              .style("width", width + "px")
              .style("height", height + "px");

          graph.line = d3.svg.line()
              .interpolate("bundle")
              .tension(.85)
              .x(function(d) { return d.x + d.dx / 2; })
              .y(function(d) { return d.y + d.dy / 2; });
        if(!reinit){
            graph.requestData(dataUrl, graph.render);
            $(window).on('resize', function(ev){
                graph.resetPosition();
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
      this.render = function(){
        var nodes = graph.treemap.nodes(relationalPlotHelpers.root(graph._data)),
            links = relationalPlotHelpers.imports(nodes);

        graph.div.selectAll(".cell")
            .data(nodes)
          .enter().append("div")
            .attr("class", "cell")
            .style("background-color", function(d) { return d.children ? fill(d.host) : null; })
          .call(function cell() {
                this.style("left", function(d) { return d.x + "px"; })
                    .style("top", function(d) { return d.y + "px"; })
                    .style("width", function(d) { return d.dx - 1 + "px"; })
                    .style("height", function(d) { return d.dy - 1 + "px"; });
            })
            .text(function(d) { return d.children ? null : d.service; });

        graph.div.append("svg")
            .attr("width", width)
            .attr("height", height)
            .style("position", "absolute")
          .selectAll(".link")
            .data(graph.bundle(links))
          .enter().append("path")
            .attr("class", "link")
            .attr("d", graph.line)
            .style("stroke", function(d) { return stroke(d[0].value); });
      };
        this.requestData = function(dataUrl, callback){
            d3.json(dataUrl, function(res){
                if(res && res.result === 'ok'){
                    graph._data = res.data;
                    if(typeof callback === 'function'){
                        callback();
                    }
                }else{
                    console.log("Cannot create topology graph, server returns error: " + res.data);
                }
            });
        };
        this.resetPosition = function(){
            var sidebarWidth = $("#sidebar").width(),
                windowWidth = $(window).width();
            if(windowWidth > sidebarWidth){
                contentWidth = windowWidth - sidebarWidth + positioningMagicNumber;
            }else{
                contentWidth = windowWidth;
            }
            width = contentWidth;
        };
    };
    return RelationalPlot;
}(RelationalPlot || {});