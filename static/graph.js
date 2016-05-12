var width = 8000;
var height = 8000;

// _TAGS, _ENV, 
// function calculate_fill_color(group_strongly_by, group_weakly_by)
// function calculate_stroke_color(group_strongly_by, group_weakly_by)
// function sanitize_archdomain(d)

var TAGS = _.filter(_.flatten(_TAGS), function (x) { return (x !== null); });
var ENVS = _.filter(_.flatten(_ENVS), function (x) { return (x !== null); });

var params = {
     rows: 0,
     columns: 0,
     max_rows_or_columns: 0,
     focus_node_radius: 0,
     left_margin: 0,
     top_margin: 0,
     ENV_FOCI_NODES: [],
     TAG_FOCI_NODES: []
};

function setup_params(group_strongly_by) {
    if (group_strongly_by == 'env') {
        params.rows = _ENVS.length;
        params.columns = _.max(_ENVS, 'length').length;
    } else if (group_strongly_by == 'archdomain') {
        params.rows = _TAGS.length;
        params.columns =_.max(_TAGS, 'length').length;
    } else {
        params.rows = 1;
        params.columns = 1;
    }

    params.max_rows_or_columns = Math.max(params.rows, params.columns);
    params.focus_node_radius = Math.min(width/params.max_rows_or_columns, height/params.max_rows_or_columns) / 2;
    params.left_margin = params.focus_node_radius * 1.5;
    params.top_margin = params.focus_node_radius * 1.5;

    params.ENV_FOCI_NODES = make_foci_nodes_env();
    params.TAG_FOCI_NODES = make_foci_nodes_tag();
}

d3.select("#pause_resume_button").on("click", function () {
    if (force.alpha() != 0) {
        force.stop(); 
    } else {
        force.resume();
    }
    d3.select(this).text(force.alpha() != 0 ? "Pause" : "Resume");
});

d3.select("#download").on("click", function () {
    var svg = document.getElementsByTagName("svg")[0];
    // Extract the data as SVG text string
    var svg_xml = (new XMLSerializer).serializeToString(svg);
    d3.text("graph.css", "text/plain", function(style) {
        var html = "<html><head><style> " + style + "</style></head><body>" + svg_xml + "</body></html>";
        var content = "data:application/octet-stream," + encodeURIComponent(html);
        var anchor = document.getElementById("download-link");
        anchor.href = content;
        var json_fn = d3.select("#data_file_name").node().value;
        var base_fn = json_fn.replace(/\.json/, '');
        anchor.download = base_fn + ".html";
        anchor.click();
    });
});


d3.select("#go_button").on("click", function() {
    d3.select("#pause_resume_button")
        .text("Pause")
        .property('disabled', '');

    var group_strongly_by = d3.select("#group_strongly_by").node().value;
    var group_weakly_by = d3.select("#group_weakly_by").node().value;
    var cluster_strength = d3.select("#cluster_strength").node().value;

    var fill_by = calculate_fill_color(group_strongly_by, group_weakly_by);
    var stroke_by = calculate_stroke_color(group_strongly_by, group_weakly_by);

    var omit_archdomains = document.querySelectorAll("input[type=checkbox][name=omit_archdomain]:checked");
    var omit_archdomains_regex = _.map(omit_archdomains, 'value').join("|");

    var omit_envs = document.querySelectorAll("input[type=checkbox][name=omit_env]:checked");
    var omit_envs_regex = _.map(omit_envs, 'value').join("|");

    var hide_filtered_nodes = (! _.isEmpty(document.querySelectorAll("input[type=checkbox][name=hide_filtered_nodes]:checked")));

    update(d3.select("#data_file_name").node().value,
           group_strongly_by, group_weakly_by,
           fill_by, stroke_by,
           omit_archdomains_regex, omit_envs_regex, hide_filtered_nodes,
           cluster_strength);

    // hack: enable download button now that we have content
    d3.select("#download_button").property('disabled', '');
});

function startswith(str, start) {
    return str.indexOf(start) === 0;
}

function endswith(str, end) { 
    return str.indexOf(end, str.length - end.length) !== -1; 
}

function is_filtered_node(d, re) {
    return re.test(d.archdomain);
}

var env_color = d3.scale.category20().domain(ENVS);
var archdomain_color = d3.scale.category20().domain(TAGS);
var traffic_color= d3.scale.quantize().domain([0,6]).range(colorbrewer.Reds[6]); // 6 orders of magnitude

function color_by_ip_type(d) {
    switch (d.ip_type) {
    case "internal":
        return "#1f77b4";
    case "external":
        return "#2ca02c";
    case "unknown":
        return "#ff7f0e";
    default:
        return "#ff0000"; 
    }
}

function color_by(stroke_by, d) {
    switch(stroke_by) {
    case 'env':
        return env_color(d.env);
    case 'archdomain':
        return archdomain_color(sanitize_archdomain(d));
    case 'traffic':
        return traffic_color(d.traffic);
    case 'ip':
        return color_by_ip_type(d);
    }
}


function make_foci_nodes_env() {
    var nodes = {};
    for (var i = 0; i < _ENVS.length; i++) {
        var envs1 = _ENVS[i];
        for (var j = 0; j < envs1.length; j++) {
            var env = envs1[j];
            if (env != null) {
                var node = {
                    'env': env,

                    'label': env,
                    'archdomain': '',
                    'name': env,
                    'instance_type': '',
                    'traffic': 0,
                    'price': 0,

                    'x': params.left_margin + (j * params.focus_node_radius * 2) + 100,
                    'y': params.top_margin + (i * params.focus_node_radius * 2) + 100,
                    'fixed': true,      // mouseover sets fixed so we have to use focus for our purposes
                    'focus': true
                };
                nodes[env] = node;
            }
        }
    }
    return nodes;
}

function make_foci_nodes_tag() {
    var nodes = {};
    for (var i = 0; i < _TAGS.length; i++) {
        var tags1 = _TAGS[i];
        for (var j = 0; j < tags1.length; j++) {
            var tag = tags1[j];
            if (tag != null) {
                var node = {
                    'env': 'any',
                    'label': tag,
                    'archdomain': tag,
                    'name': tag,
                    'instance_type': '',
                    'traffic': 0,
                    'price': 0,

                    'x': params.left_margin + (j * params.focus_node_radius * 2),
                    'y': params.top_margin + (i * params.focus_node_radius * 2),
                    'fixed': true,
                    'focus': true
                };
                nodes[tag] = node;
            }
        }
    }
    return nodes;
}

function calculate_env_totals(json) {
    for (var i = 0; i < json.nodes.length; i++) {
        var d = json.nodes[i];
        if (is_host_node(d)) {
            var e = params.ENV_FOCI_NODES[d.env];
            e.price += d.price;
            e.traffic += d.traffic;
        }
    }

    _.mapValues(params.ENV_FOCI_NODES, function(e, env) {
        e.label += 
            " $" + (e.price*24*365/1000).toFixed(0) + "K/yr " +
            " $" + e.price.toFixed(0) + "/hr traffic=" + e.traffic.toFixed(0);
    });
}

function add_some_nodes(nodes, names, new_nodes) {
    for (var i = 0; i < names.length; i++) {
        var node = (new_nodes[names[i]]);
        // evil side effect
        // FOCI nodes must come at the beginning of the list so they wind up at the end of the display in z-order.
        // WARNING: this is mis-adjusting all the offsets in the JSON array so all links are now to the wrong things and have to be fixed up.
        nodes.unshift(node);
    }
}

function count_foci_nodes(group_strongly_by, group_weakly_by) {
    if (group_strongly_by == 'env') {
        return ENVS.length;
    } else if (group_strongly_by== 'archdomain') {
        return TAGS.length;
    } else {
        return 0;
    }
}

function add_foci_nodes(group_strongly_by, group_weakly_by, nodes) {
    var g = group_strongly_by;
    if (g == 'traffic') {
        g = group_weakly_by;
    }
    
    if (group_strongly_by == 'env') {
        add_some_nodes(nodes, ENVS, params.ENV_FOCI_NODES)
    } else if (group_strongly_by== 'archdomain') {
        add_some_nodes(nodes, TAGS, params.TAG_FOCI_NODES)
    }
    return nodes;
}

function filter_params_links(params, nodes, links) {
    var result = [];
    var len = links.length;
    for (var i = 0; i < len; i++) {
        var link = links[i];
        var source_record = nodes[link.source];
        var target_record = nodes[link.target];
        var ok = true;
        for (var key in params) {
            if (params.hasOwnProperty(key)) {
                var value = params[key]
                if ((source_record[key] != value) && 
                    (target_record[key] != value))
                    ok = false;
                break;
            }
        }
        if (ok) {
            result.push(link)
        }
    }
    return result;
}

function filter_predicate_links(links, predicate) {
    var result = [];
    var len = links.length;
    for (var i = 0; i < len; i++) {
        var link = links[i];
        if (predicate(link.source_link) || predicate(link.target_link)) {
            // skip
        } else {
            result.push(link)
        }
    }
    return result;
}

function is_external_link(link) {
    lse = link.source_link.env;
    lte = link.target_link.env;
    return (((lse == 'aws-external') || (lte == 'aws-external')) ||
            ((lse == 'external') || (lte == 'external')));
}


function is_focus_node (d) { return ('focus' in d) && d.focus == true; }
function is_host_node (d) { return !(('focus' in d) || d.focus == true); }

function get_focus_node(group_strongly_by, group_weakly_by, node) {

    var g = group_strongly_by == 'traffic' ? group_weakly_by : group_strongly_by;

    if (g == 'env') {
        return params.ENV_FOCI_NODES[node['env']];
    } else if (g == 'archdomain') {
	function matcher (archdomain) { return function (x) { return (archdomain.indexOf(x) == 0) ? x.length : -1; } };

	var sanitized_archdomain = sanitize_archdomain(node);
	var best_matching_archdomain = _.orderBy(_.keys(params.TAG_FOCI_NODES), matcher(sanitized_archdomain), ['desc'])[0];
	if (_.isUndefined(best_matching_archdomain)) {
	    return undefined;
	} else {
            return params.TAG_FOCI_NODES[best_matching_archdomain];
	}
    }

    return null;
}

// dan bernstein string has function
function hash_djb2(str) {
    var hash = 5381;
    for (i = 0; i < str.length; i++) {
        char = str.charCodeAt(i);
        hash = ((hash << 5) + hash) + char; /* hash * 33 + c */
    }
    return hash;
}

function host_radius(d) {
    if ('price' in d && d.price != null) return 24 + d.price * 24;
    else return 24;
}


// filter out traffic and nodess to/from some archdomain or env (key) if requested
function hide_filtered_links_and_nodes(json, hide_filtered_nodes, omit_regex, key) {
    if (omit_regex) {
        var re = new RegExp(omit_regex);
        json.links = filter_predicate_links(json.links, function (d) { return re.test(d[key]); });
        if (hide_filtered_nodes) {
            for (var i = 0; i < json.nodes.length; i++) {
                if (re.test(json.nodes[i][key])) {
                    json.nodes[i].hidden = true;
                }
            }
        }
    }
}

// global for access from html click
var force;

function update(file, group_strongly_by, group_weakly_by, fill_by, stroke_by,
                omit_archdomains_regex, omit_envs_regex, hide_filtered_nodes,
                cluster_strength) {
    setup_params(group_strongly_by);

    var cluster_factor = 0.1;
    if (cluster_strength == 'weak') cluster_factor = 0.5;
    if (cluster_strength == 'strong') cluster_factor = 3;

    d3.select("body").select("svg").remove();

    function zoomer() {
        // if we translate, then d3 grabs the mouse for moving the whole screen, and can't
        // move the nodes any more.
        //svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
        svg.attr("transform", "scale(" + d3.event.scale + ")");
    }

    var zoom = d3.behavior.zoom().scale(0.125).scaleExtent([0.125, 1]);
    var svg = d3.select("body").append("svg")
        .attr("width", width * (1+1/params.rows))
        .attr("height", height * (1+1/params.columns))
        .append("g")
        .call(zoom.on("zoom", zoomer))
        .append("g")
        .attr("transform", "scale(0.125)");
    
    force = d3.layout.force()
        .gravity(.05)
        .friction(0.2)
        .distance(function(link) { return link.value * 50 || 3*300; })
        .charge(function(node) {
            if (is_focus_node(node)) return 0;
            else return (node.price * -500) * node.traffic;
        })
        .linkStrength(function(link, idx) {
            var k = 0.5/(link.value||1);

            if (group_strongly_by == 'env' && (link.source_link.env != link.target_link.env)) {
                // reduce strength for cross-env links in strong env clustering mode
                k *= 0.1;
            }

            if (group_strongly_by == 'archdomain' && (sanitize_archdomain(link.source_link) != sanitize_archdomain(link.target_link))) {
                // reduce strength for cross-archdomain links in strong archdomain clustering mode
                k *= 0.05;
            }

            // reduce strength for links to external nodes in non-traffic clustering modes
            if ((group_strongly_by != 'traffic') && is_external_link(link)) {
                k *= 0.1;
            }

            return k;
        })
        .size([width, height]);


    var node_tip = d3.tip()
        .attr('class', 'd3-tip node-tip')
        .html(function(d) {
            var ips = "";
            var cluster_size = "";
            if ('ips' in d) {
                if (d.ips.length > 1) {
                    cluster_size =
                        "<li><strong>Cluster size:</strong> " +
                        d.ips.length +
                        "</li>";
                }
                ips = _.take(d.ips, 10).join(',') +"...";
            } else {
                ips = d.name + " (" + d.ip_type + ")";
            }
            return "<ul>" + 
                "<li><strong>Label:</strong> " + d.label + "</li>" +
                "<li><strong>Env:</strong> " + d.env + "</li>" + 
                "<li><strong>Arch:</strong> " + d.archdomain + "</li>" + 
                "<li><strong>IP:</strong> " + ips + "</li>" +
                "<li><strong>Instance Type:</strong> " + d.instance_type + "</li>" + 
                cluster_size +
                "<li><strong>Traffic:</strong> " + d.traffic.toFixed(2) + "</li>" + 
                "<li><strong>Price/hr: $</strong> " + d.price.toFixed(2) + "</li>" + 
                "<li><strong>Price/yr: $</strong> " + ((d.price*24*365/1000).toFixed(0)) + "K</li>" + 
                "</ul>";
        });

    svg.call(node_tip);

    var link_tip = d3.tip()
        .attr('class', 'd3-tip link-tip')
        .offset(function() {
            return [0, 0]
        })
        .html(function(d) {
            var source_env = d.source_link.env;
            var target_env = d.target_link.env;
            return "<ul>" + 
                "<li><strong>Source:</strong> " + d.source_name + " (" + source_env + " " + d.source_link.label + ")</li>" +
                "<li><strong>Target:</strong> " + d.target_name + " (" + target_env + " " + d.target_link.label + ")</li>" +
                "<li><strong>Traffic:</strong> " + d.value + "</li>" + 
                "<li><strong>Ports:</strong> " + d.ports.join(", ") + "</li>" + 
                "</ul>";
        });

    svg.call(link_tip);

    function dragstart(d) {
        d3.select(this).classed("fixed", d.fixed = true);
    }

    function dblclick(d) {
        d3.select(this).classed("fixed", d.fixed = false);
    }

    d3.json(file, function(error, json) {

        calculate_env_totals(json);

        if (group_strongly_by != 'traffic' && group_weakly_by != 'traffic') {
            // omit all links if so requested
            json.links = [];
        } else {
            // hack in pointers from links to nodes JSON so link tooltips can be more informative
            for (var i = 0; i < json.links.length; i++) {
                json.links[i].source_link = json.nodes[json.links[i].source];
                json.links[i].target_link = json.nodes[json.links[i].target];
            }

            // filter out traffic and/or nodes to/from some archdomains if requested
            hide_filtered_links_and_nodes(json, hide_filtered_nodes, omit_archdomains_regex, 'archdomain');

            // filter out traffic and/or nodes to/from some envs if requested
            hide_filtered_links_and_nodes(json, hide_filtered_nodes, omit_envs_regex, 'env');
        }

        {
            var offset = count_foci_nodes(group_strongly_by, group_weakly_by);
            if (offset != 0) {
                for (var i = 0; i < json.links.length; i++) {
                    json.links[i].source += offset;
                    json.links[i].target += offset;
                }
            }
        }

        force
            .nodes(add_foci_nodes(group_strongly_by, group_weakly_by, json.nodes))
            .links(json.links)
            .start();

        var link = svg.selectAll(".link")
            .data(json.links)
            .enter().append("line")
            .style("stroke-width", function(d) { return d.value; })
            .attr("class", function(d) { 
                if (_.isUndefined(d.ports)) {
                    return "foo";
                } else {
                    return "link " + d.ports.map(function(x) { return "p" + x }).join(" ") 
                }
            })
            .on('mouseover', link_tip.show)
            .on('mouseout', link_tip.hide);

        var drag = force.drag()
            .on("dragstart", dragstart);

        var node = svg.selectAll(".node")
            .data(json.nodes)
            .enter().append("g")
            .on("dblclick", dblclick)
            .call(drag);

        node.filter(is_host_node)
            .filter(function(d) { return d.hidden != true })
            .append("circle")
            .style("stroke", function(d) { return color_by(stroke_by, d); })
            .style("fill", function(d) { return color_by(fill_by, d); })
            .classed(function(d) { return 'node env-' +  d.env + 'archdomain-' + d.archdomain })
            .attr("r", host_radius)
            .on('mouseover', node_tip.show)
            .on('mouseout', node_tip.hide);

        node.filter(is_focus_node)
            .append("circle")
            .style("stroke", function(d) { return color_by(fill_by, d); }) // stroke by the fill of the matching hosts 
            .style("fill", function(d) { return color_by(fill_by, d); }) // and fill nearly transparent
            .classed(function(d) { return 'node focus ' +  d.env; })
            .attr("fill-opacity", "0.2")
            .attr("r", params.focus_node_radius);

        node.filter(is_host_node)
            .filter(function(d) { return d.hidden != true })
            .append("text")
            .attr("dx", "-12")
            .attr("dy", ".35em")
            .style("font-size", function(d) { return 12 * (1 + d.price) ; })
            .text(function(d) { return d.label; });

        node.filter(is_focus_node)
            .append("text")
            .attr("dy",  -params.focus_node_radius)
            .attr("dx", 0)
            .attr("text-anchor", "middle")
            .style("font-size", 72)
            .text(function(d) { return d.label; });

        function tick (e, i) {
            var k = e.alpha * cluster_factor;
            json.nodes.forEach(function(node) {
                if (! is_focus_node(node)) {
                    var focus_node = get_focus_node(group_strongly_by, group_weakly_by, node);
                    if (focus_node) {
                        var focus_x = focus_node.x;
                        var focus_y = focus_node.y;
                        {
                            // distribute the focus r of the nodes by traffic or size
                            // distribute the focus theta of the nodes by hash of tag and label if the tag is numerous 
                            var dr = Math.min(Math.max(0, host_radius(node)*8), params.focus_node_radius);
                            var theta1 = (hash_djb2(node.archdomain || "") % 180) * (Math.PI / 180);  // +/- 180
                            var theta2 = ((hash_djb2(node.label) % 180) * (Math.PI / 180)); // +/- 180
                            var dy = dr * Math.cos(theta1) + dr/4 * Math.cos(theta2);
                            var dx = dr * Math.sin(theta1) + dr/4 * Math.sin(theta2);
                            
                            node.x += (focus_x + dx - node.x) * k;
                            node.y += (focus_y + dy - node.y) * k;
                        }
                    }
                }
            });

            link.attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
        }

        force.on("tick", tick);
    });
}

