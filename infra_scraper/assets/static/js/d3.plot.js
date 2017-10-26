
var relationalPlotHelpers = {
  nodeServiceId: function(d){
    if(d && d.host && d.service){
        return "node-" + d.host.replace(/\./g,"_") + "-service-" + d.service.replace(/\./g,"_");
    }else{
        console.log("Cannot generate node-service ID, given node or its host/service is undefined! node: " + graphHelpers.nodeToString(d));
        return "node-" + (node.host?node.host:"UNDEFINED_HOST") + (node.service?node.service:"UNDEFINED_SERVICE");
    }
  },
  nodeToString: function(n, hideRelations){
       var cleanNode = {};
       $.extend(cleanNode, n);
       delete cleanNode.children;
       delete cleanNode.parent;
       if(hideRelations){
         delete cleanNode.relations;
       }
       return JSON.stringify(cleanNode);
  },
  root: function(classes) {
    var map = {};
    var parentObj = {host:"", children:[]};
    var addedHosts = []

    classes.forEach(function(d) {
      //create hosts array
       if(addedHosts.indexOf(d.host) === -1){
          addedHosts.push(d.host);
          var newHost={host: d.host, service: d.host, parent: parentObj}
          newHost.children = [$.extend({parent:newHost}, d)]
          parentObj.children.push(newHost);
      }else{
          // find host and add children
          parentObj.children.forEach(function(item){
            if(item.host == d.host){
                item.children.push($.extend({parent:item}, d))
            }
          });
      }
    });

    return parentObj;
  },

  // Return a list of imports for the given array of nodes.
  imports: function(nodes) {
    var map = {},
        imports = [];

    // Compute a map from name to node.
    nodes.forEach(function(d) {
      map[d.host+"_"+d.service] = d;
    });

    // For each import, construct a link from the source to target node.
    nodes.forEach(function(d) {
      if (d.relations) {
        d.relations.forEach(function(i) {
            var line = {source: map[d.host+"_"+d.service], target: map[i.host + "_" + i.service], link_str: 2};
            if(line.source && line.target){
                imports.push(line);
            }else{
                console.log("Cannot create relation link, node: " + graphHelpers.nodeToString(d) + " relation: " + JSON.stringify(i));
            }
        });
      }
    });
    return imports;
  }
};



function nodeRelations(nodes) {
  var map = {},
      relations = [];

  // Compute a map from name to node.
  nodes.forEach(function(d) {
    map[d.data.name] = d;
  });

  // For each import, construct a link from the source to target node.
  nodes.forEach(function(d) {
    if (d.data.relations) d.data.relations.forEach(function(i) {
      relations.push(map[d.data.name].path(map[i]));
    });
  });

  return relations;
}

function nodeHierarchy(nodes) {
  var map = {};

  function find(name, data) {
    var node = map[name], i;
    if (!node) {
      node = map[name] = data || {name: name, children: []};
      if (name.length) {
        node.parent = find(name.substring(0, i = name.lastIndexOf("|")));
        node.parent.children.push(node);
        node.key = name.substring(i + 1);
      }
    }
    return node;
  }

  nodes.forEach(function(d) {
    find(d.name, d);
  });

  return d3.hierarchy(map[""]);
}

