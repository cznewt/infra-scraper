var RelationalPlot = function(RelationalPlot){
    /**
     * Hierarchical edge bundling render method
     * @param dataUrl - URL to data endpoint
     * @param graphSelector - CSS selector of graph parent div
     * @param refreshInterval - Refresh interval in seconds (can be null, means refresh disabled)
     */
    RelationalPlot.hierarchicalEdgeBundling = function(dataUrl, graphSelector, refreshInterval) {
        var content_width = $(graphSelector).innerWidth(),
            w = content_width,
            h = content_width,
            rx = w / 2,
            ry = h / 2,
            rotate = 0,
            positioningMagicNumber = - 10,
            pi = Math.PI,
            active_link,
            splines = [],
            color_arc = d3.scale.category20(),
            line_color = function(d){
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
        this._data = {},
        this.init = function(reinit) {
            if(!dataUrl || !graphSelector){
                throw new Error("Cannot init ResourceTopology graph, dataUrl or graphSelector not defined");
            }
            graph.cluster = d3.layout.cluster()
                .size([360, ry - 150])
                .sort(function(a, b) {
                    return d3.ascending(a.service, b.service);
                });
            graph.bundle = d3.layout.bundle();
            graph.line = d3.svg.line.radial()
                .interpolate("bundle")
                .tension(.8)
                .radius(function(d) {
                    return d.y - 35;
                })
                .angle(function(d) {
                    return d.x / 180 * pi;
                });
            if(reinit && graph.div){
                graph.div.remove();
            }
            graph.div = d3.select(graphSelector).insert("div", "h2")
                .style("width", w - 20 + "px")
                .style("height", w + "px")
                .style("margin","0px auto");
            graph.svg = graph.div.append("svg:svg")
                .attr("width", w)
                .attr("height", h)
                .append("svg:g")
                .attr("transform", "translate(" + rx + "," + ry + ")")
                .attr("transform", "rotate(180 " + rx / 2 + " " + ry / 2 + ")")

            graph.svg.append("svg:path")
                .attr("class", "arc")
                .attr("d", d3.svg.arc().outerRadius(ry - 120).innerRadius(0).startAngle(0).endAngle(2 * Math.PI))

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
        this.render = function() {
            if(graph._data && graph._data.length > 0){
                var rootNodes = graphHelpers.root(graph._data);
                var nodes = graph.cluster.nodes(rootNodes),
                    links = graphHelpers.imports(nodes),
                    splines = graph.bundle(links);

                var groupData = graph.svg.selectAll("g.group")
                    .data(nodes.filter(function(d) {
                        return d.host && d.service == d.host && d.children;
                    }))
                    .enter().append("group")
                    .attr("class", "group");

                var groupArc = d3.svg.arc()
                    .innerRadius(ry - 185)
                    .outerRadius(ry - 160)
                    .startAngle(function(d) {
                        return (graph.findStartAngle(d.__data__.children) - 0.25) * pi / 180;
                    })
                    .endAngle(function(d) {
                        return (graph.findEndAngle(d.__data__.children) + 0.25) * pi / 180
                    });

                graph.svg.selectAll("g.arc")
                    .data(groupData[0])
                    .enter().append("svg:path")
                    .attr("id",function(d){
                        return "node-"+d.__data__.host.replace(/\./g,"_");
                    })
                    .attr("data-node-host",function(d){
                        return d.__data__.host;
                    })
                    .attr("d", groupArc)
                    .attr("class", "groupArc")
                    .style("fill", function(d,i) {
                        return color_arc(i);
                    });
               graph.svg.selectAll("path.groupArc")[0].forEach(function(group){
                    var arc = d3.select(group),
                        nodeHostId = arc.attr("id"),
                        nodeHost = arc.attr("data-node-host");

                    d3.select("g").append("text")
                    .style("font-size",12)
                    .style("fill","#F8F8F8")
                    .attr("dy", 17)
                    .append("textPath")
                    .attr("xlink:href", function(d){
                        return "#"+nodeHostId;
                    })
                    .attr("startOffset", 7)
                    .attr("width", arc.node().getTotalLength()/2.4)
                    .text(nodeHost)
                    .each(function wrap( d ) {
                        var self = d3.select(this),
                            textLength = self.node().getComputedTextLength(),
                            text = self.text(),
                            width = self.attr('width');
                        if(width > 50){
                            while ( ( textLength > width )&& text.length > 0) {
                                if(width > 100){
                                    text = text.slice(0, -1);
                                    self.text(text + '...');
                                }else{
                                    text = text.slice(0, -5);
                                    self.text(text);
                                }
                                textLength = self.node().getComputedTextLength();
                            }
                        }else{
                            self.text("");
                        }
                    });
                });
                graph.svg.selectAll("g.node")
                    .data(nodes.filter(function(n) {
                        return !n.children;
                    }))
                    .enter().append("svg:g")
                    .attr("class", "node")
                    .attr("data-host-id", function(d){
                        return d.host;
                    })
                    .attr("id", function(d) {
                        return graphHelpers.nodeServiceId(d);
                    })
                    .attr("transform", function(d) {
                        return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")";
                    })
                    .append("svg:a")

                    .append("svg:text")
                    .attr("dx", function(d) {
                        return d.x < 180 ? 0 : 0;
                    })
                    .attr("dy", ".2em")
                    .attr("text-anchor", function(d) {
                        return d.x < 180 ? "start" : "end";
                    })
                    .style("text-anchor", function(d) {
                        return d.x < 180 ? "end" : "start";
                    })
                    .attr("transform", function(d) {
                        return d.x < 180 ? "rotate(180)" : "rotate(0)";
                    })
                    .text(function(d) {
                        return d.service;
                    })
                    .classed("status-success", function(d){ return d.hasOwnProperty("status") && d.status === "success";})
                    .classed("status-failed", function(d){ return d.hasOwnProperty("status") && d.status === "failed";})
                    .classed("status-unknown", function(d){ return !d.hasOwnProperty("status") || d.status === "unknown";})
                    .on("mouseover", function(d) {
                        graph.svg.selectAll("path.link.target-" + d.host.replace(/\./g,"_") + "-" + d.service.replace(/\./g,"_"))
                            .classed("target", true)
                            .each(graph.updateNodes("source", true));

                        graph.svg.selectAll("path.link.source-" + d.host.replace(/\./g,"_") + "-" + d.service.replace(/\./g,"_"))
                            .classed("source", true)
                            .each(graph.updateNodes("target", true));

                        graph.svg.select("#" + graphHelpers.nodeServiceId(d)).classed("selected", true);
                    })
                    .on("mouseout", function mouseout(d) {
                        graph.svg.selectAll("path.link.source-" + d.host.replace(/\./g,"_") + "-" + d.service.replace(/\./g,"_"))
                            .classed("source", false)
                            .each(graph.updateNodes("target", false))
                            .style("stroke", function(d) {
                                return line_color(d);
                            });

                        graph.svg.selectAll("path.link.target-" + d.host.replace(/\./g,"_") + "-" + d.service.replace(/\./g,"_"))
                            .classed("target", false)
                            .each(graph.updateNodes("source", false))
                            .style("stroke", function(d) {
                                return line_color(d);
                            });

                        graph.svg.select("#" + graphHelpers.nodeServiceId(d)).classed("selected", false);
                    });

                var path = graph.svg.selectAll("path.link")
                    .data(links)
                    .enter().append("svg:a")
                    .append("svg:path")
                    .attr("class", function(d) {
                        return "link source-" + d.source.host.replace(/\./g,"_") + "-" + d.source.service.replace(/\./g,"_") +" target-" + d.target.host.replace(/\./g,"_") + "-" + d.target.service.replace(/\./g,"_");
                    })
                    .attr("d", function(d, i) {
                        return graph.line(splines[i]);
                    })
                    .style("stroke", function(d) {
                        return line_color(d);
                    })
                    .on("mouseover", function linkMouseover(d) {
                        active_link = ".source-" + d.source.host.replace(/\./g,"_") + "-" + d.source.service.replace(/\./g,"_") + ".target-" + d.target.host.replace(/\./g,"_") + "-" + d.target.service.replace(/\./g,"_");
                        graph.svg.selectAll(active_link)
                            .classed("active", true);
                        graph.svg.select("#" + graphHelpers.nodeServiceId(d.source))
                            .classed("source", true);

                        graph.svg.select("#" + graphHelpers.nodeServiceId(d.target))
                            .classed("target", true);
                    })
                    .on("mouseout", function linkMouseout(d) {
                        graph.svg.selectAll(active_link).classed("active", false)
                            .style("stroke", function(d) {
                                return line_color(d);
                            });

                        graph.svg.select("#" + graphHelpers.nodeServiceId(d.source))
                            .classed("source", false);

                        graph.svg.select("#" + graphHelpers.nodeServiceId(d.target))
                            .classed("target", false);
                    });
            }
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
                content_width = windowWidth - sidebarWidth + positioningMagicNumber;
            }else{
                content_width = windowWidth;
            }
            w = content_width;
            h = content_width;
            rx = w / 2;
            ry = h / 2;
        };

        this.updateNodes = function(name, value) {
            return function(d) {
                if (value) this.parentNode.appendChild(this);
                var selector = graphHelpers.nodeServiceId(d[name]);
                graph.svg.select("#"+selector).classed(name, value);
            };
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
