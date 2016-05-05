function get_date_filename(offset) {
    var date = new Date(new Date() - offset);
    var day = date.getDate();
    var month = date.getMonth() + 1;
    var year = date.getFullYear();

    if (month < 10) month = "0" + month;
    if (day < 10) day = "0" + day;

    return year + "-" + month + "-" + day;       
}

function get_date_filenames() {
    var fns = [0, 86400*1000].map(function (offset) { return get_date_filename(offset); });
    var data_names = ["data/clusters", "data/instances", "data/security-groups"];

    // interleave types and dates
    return _.flatten(_.spread(_.zip)(data_names.map(function (dn) {
        return fns.map(function (fn) {
            return dn + "-" + fn + ".json";
        });
    })));
}

function clear_data_file_name() {
    d3.select("#data_file_name").property('value', '');
}

function init_fields() {
    var f = get_date_filenames();
    d3.select('#filenames')
        .selectAll('option')
        .data(f).enter()
        .append('option')
        .attr('value', function(d) { return d; });
    d3.select("#data_file_name").property('value', f[0]);
}


