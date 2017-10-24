
d3.hive = {};

Math.radians = function(degrees) {
  return degrees * Math.PI / 180;
};

Math.degrees = function(radians) {
  return radians * 180 / Math.PI;
};

d3.hive.link = function() {
  var source = function(d) { return d.source; },
      target = function(d) { return d.target; },
      angle = function(d) { return d.angle; },
      startRadius = function(d) { return d.radius; },
      endRadius = startRadius,
      arcOffset = 0;

  function link(d, i) {
    var s = node(source, this, d, i),
        t = node(target, this, d, i),
        x;
    if (t.a < s.a) x = t, t = s, s = x;
    if (t.a - s.a > Math.PI) s.a += 2 * Math.PI;
    var a1 = s.a + (t.a - s.a) / 3,
        a2 = t.a - (t.a - s.a) / 3;
    return s.r0 - s.r1 || t.r0 - t.r1
        ? "M" + Math.cos(s.a) * s.r0 + "," + Math.sin(s.a) * s.r0
        + "L" + Math.cos(s.a) * s.r1 + "," + Math.sin(s.a) * s.r1
        + "C" + Math.cos(a1) * s.r1 + "," + Math.sin(a1) * s.r1
        + " " + Math.cos(a2) * t.r1 + "," + Math.sin(a2) * t.r1
        + " " + Math.cos(t.a) * t.r1 + "," + Math.sin(t.a) * t.r1
        + "L" + Math.cos(t.a) * t.r0 + "," + Math.sin(t.a) * t.r0
        + "C" + Math.cos(a2) * t.r0 + "," + Math.sin(a2) * t.r0
        + " " + Math.cos(a1) * s.r0 + "," + Math.sin(a1) * s.r0
        + " " + Math.cos(s.a) * s.r0 + "," + Math.sin(s.a) * s.r0
        : "M" + Math.cos(s.a) * s.r0 + "," + Math.sin(s.a) * s.r0
        + "C" + Math.cos(a1) * s.r1 + "," + Math.sin(a1) * s.r1
        + " " + Math.cos(a2) * t.r1 + "," + Math.sin(a2) * t.r1
        + " " + Math.cos(t.a) * t.r1 + "," + Math.sin(t.a) * t.r1;
  }

  function node(method, thiz, d, i) {
    var node = method.call(thiz, d, i),
        a = +(typeof angle === "function" ? angle.call(thiz, node, i) : angle) + arcOffset,
        r0 = +(typeof startRadius === "function" ? startRadius.call(thiz, node, i) : startRadius),
        r1 = (startRadius === endRadius ? r0 : +(typeof endRadius === "function" ? endRadius.call(thiz, node, i) : endRadius));
    return {r0: r0, r1: r1, a: a};
  }

  link.source = function(_) {
    if (!arguments.length) return source;
    source = _;
    return link;
  };

  link.target = function(_) {
    if (!arguments.length) return target;
    target = _;
    return link;
  };

  link.angle = function(_) {
    if (!arguments.length) return angle;
    angle = _;
    return link;
  };

  link.radius = function(_) {
    if (!arguments.length) return startRadius;
    startRadius = endRadius = _;
    return link;
  };

  link.startRadius = function(_) {
    if (!arguments.length) return startRadius;
    startRadius = _;
    return link;
  };

  link.endRadius = function(_) {
    if (!arguments.length) return endRadius;
    endRadius = _;
    return link;
  };

  return link;
};

var HivePlot = {
  init: function(container, config, data) {
    if (!data) {
      throw new Error("Cannot initialize Hive plot, invalid data provided: " + data);
    }
    var width = config.width || 1920,
        height = config.height || 1920,
        radius = config.radius || 600,
        axisMapping = {},
        iconMapping = {},
        radiusMapping = {},
        itemCounters = {},
        itemStep = {};

    var plotFunctions = {
      createAxes: function(items) {
        return items.map(function(item, index) {
          item.icon.color = d3.schemeCategory20[index];
          iconMapping[item.kind] = item.icon;
          itemCounters[item.kind] = 0;
          axisMapping[item.kind] = item.x;
          itemStep[item.kind] = 1 / item.items;
          radiusMapping[item.kind] = d3.scaleLinear()
            .range([item.innerRadius*radius, item.outerRadius*radius]);
          return item;
        });
      },
      createNodes: function(items) {
        return items.map(function(item) {
          item["x"] = axisMapping[item.kind];
          itemCounters[item.kind]++;
          item["y"] = itemCounters[item.kind];
          return item;
        });
      },
      createLinks: function(nodes, relations) {
        return relations.map(function(link) {
          var retLink = {};
          nodes.forEach(function(node) {
            if (link.source == node.id) {
              retLink.source = node;
            } else if (link.target == node.id) {
              retLink.target = node;
            }
          });
          if (!retLink.hasOwnProperty("source") || !retLink.hasOwnProperty("target")) {
            console.log("Can not find relation node for link " + link);
            retLink = link;
          }
          return retLink;
        });
      }
    };

    if (typeof data.axes === 'object') {
      data.axes = Object.values(data.axes);
    }

    if (typeof data.resources === 'object') {
      data.resources = Object.values(data.resources);
    }

    var axes = plotFunctions.createAxes(data.axes);
    var nodes = plotFunctions.createNodes(data.resources);
    var links = plotFunctions.createLinks(nodes, data.relations);

    var iconFunctions = {
      family: function(d) {
        return iconMapping[d].family;
      },
      color: function(d) {
        return iconMapping[d].color;
      },
      character: function(d) {
        return String.fromCharCode(iconMapping[d].char);
      },
      size: function(d) {
        return iconMapping[d].size + 'px';
      },
      transform: function(d) {
        return 'translate('+ iconMapping[d].x + ', ' + iconMapping[d].y + ')';
      }
    };

    var angle = function(d) {
      var angle = 0,
          found = false;
      axes.forEach(function(item) {
        if (d.kind == item.kind) {
          angle = item.angle;
          found = true;
        }
      });
      if (!found) {
        console.log("Cannot compute angle for " + d.kind + " " + d.name)
      }
      return angle;
    }

    var mouseFunctions = {
      linkOver: function(d) {
        svg.selectAll(".link").classed("active", function(p) {
          return p === d;
        });
        svg.selectAll(".node circle").classed("active", function(p) {
          return p === d.source || p === d.target;
        });
        svg.selectAll(".node text").classed("active", function(p) {
          return p === d.source || p === d.target;
        });
        //NodeMouseFunctions.over();
      },
      nodeOver: function(d) {
        svg.selectAll(".link").classed("active", function(p) {
          return p.source === d || p.target === d;
        });
        d3.select(this).select("circle").classed("active", true);
        d3.select(this).select("text").classed("active", true);
        tooltip.html("Node - " + d.name + "<br/>" + "Kind - " + d.kind)
          .style("left", (d3.event.pageX + 5) + "px")
          .style("top", (d3.event.pageY - 28) + "px");
        tooltip.transition()
          .duration(200)
          .style("opacity", .9);
      },
      out: function(d) {
        svg.selectAll(".active").classed("active", false);
        tooltip.transition()
          .duration(500)
          .style("opacity", 0);
      }
    };

    var svg = d3.select(selector)
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", "translate(" + (width / 2 - 180) + "," + (height / 2 - 20) + ")");

    var tooltip = d3.select("body").append("div")
      .attr("class", "tooltip")
      .style("opacity", 0);

    // Plot render

    var axe = svg.selectAll(".node").data(axes)
      .enter().append("g");

    axe.append("line")
      .attr("class", "axis")
      .attr("transform", function(d) {
        return "rotate(" + d.angle + ")";
      })
      .attr("x1", function(d) {
        return radiusMapping[d.kind].range()[0]
      })
      .attr("x2", function(d) {
        return radiusMapping[d.kind].range()[1]
      });

    axe.append("text")
      .attr("class", "axis-label")
      .attr('font-size', '16px')
      .attr('font-family', 'Open Sans')
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'central')
      .text(function(d) {
        return d.name;
      })
      .attr("transform", function(d) {
        var x = (radiusMapping[d.kind].range()[1] + 30) * Math.cos(Math.radians(d.angle));
        var y = (radiusMapping[d.kind].range()[1] + 30) * Math.sin(Math.radians(d.angle));
        return "translate(" + x + ", " + y + ")";
      });

    svg.selectAll(".link").data(links)
      .enter().append("path")
      .attr("class", "link")
      .attr("d", d3.hive.link()
        .angle(function(d) {
          return Math.radians(angle(d));
        })
        .radius(function(d) {
          return radiusMapping[d.kind](d.y * itemStep[d.kind] - 0.1);
        }))
      .on("mouseover", mouseFunctions.linkOver)
      .on("mouseout", mouseFunctions.out);

    var node = svg.selectAll(".node").data(nodes)
      .enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) {
        var x = radiusMapping[d.kind](d.y * itemStep[d.kind] - 0.1) * Math.cos(Math.radians(angle(d)));
        var y = radiusMapping[d.kind](d.y * itemStep[d.kind] - 0.1) * Math.sin(Math.radians(angle(d)));
        return "translate(" + x + ", " + y + ")";
      })
      .on("mouseover", mouseFunctions.nodeOver)
      .on("mouseout", mouseFunctions.out);

    node.append("circle")
      .attr("r", 16)
      .attr("class", "node")
      .on("mouseover", mouseFunctions.nodeOver)
      .on("mouseout", mouseFunctions.out);

    node.append("text")
      .attr('fill', function(d) { return iconFunctions.color(d.kind); })
      .attr('font-size', function(d) { return iconFunctions.size(d.kind); })
      .attr('font-family', function(d) { return iconFunctions.family(d.kind); })
      .text(function(d) { return iconFunctions.character(d.kind); })
      .attr("transform", function(d) { return iconFunctions.transform(d.kind); })
      .on("mouseover", mouseFunctions.modeOver)
      .on("mouseout", mouseFunctions.out);

    if(config.hasOwnProperty("nodeClickFn") && typeof config.nodeClickFn === 'function'){
      node.on("click", config.nodeClickFn);
    }

  }
};