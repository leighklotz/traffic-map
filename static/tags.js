var _TAGS = [["website", null, "aws-external"],
            [null, "online/orchestration"],
            [null, null, null, "online/midtier"],
            ["online/shared/cassandra", null, "online/shared/elasticsearch", null, "online/shared"],
            ["loader", null, null, "offline/content"],
            ["offline/data", null, "offline/midtier/imageengine", null, null, "offline/midtier"] ,
            ["offline/ingestion", null, "external", "offline/ingestion/focused_crawl", "offline"],
            [null, null, "offline/ingestion/proxy"],
            ["science", "dev"],
            ["infrastructure", "infrastructure/core/kafka", "infrastructure/core/zookeeper", "infrastructure/deployment", "infrastructure/monitoring"],
            ["mongo", "unknown", ""]];

var _ENVS = [["usw1-prod", null, "prod", null, "dev"],
             ["stage", null, null, null, "canary"],
             ["phnx", "build", "unknown", "aws-external", "external"]];

function calculate_fill_color(group_strongly_by, group_weakly_by) {
    switch (group_strongly_by) {
    case "traffic":
        return 'env';
    case "env":
        return 'env';
    case "archdomain":
        return 'archdomain';
    case "none":
    default:
        return 'traffic';
    }
}

function calculate_stroke_color(group_strongly_by, group_weakly_by) {
    switch (group_weakly_by) {
    case "env":
        return 'archdomain';
    case "archdomain":
        return 'env';
    case "default":
    case "none":
    case "traffic":
        switch (group_strongly_by) {
        case 'env':
            return 'archdomain';
        case 'archdomain':
            return 'env';
        default:
            return 'traffic';
        }
    }
}

function sanitize_archdomain(d) {
    var label = d.label;
    var archdomain = d.archdomain;

    if (archdomain === "" && d.env === "external") archdomain = "external";
    else if (archdomain === "external" && d.env === "aws-external") archdomain = "aws-external";
    else if (archdomain.indexOf('/') == -1) archdomain = archdomain;

    return archdomain;
}

