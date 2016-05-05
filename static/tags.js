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

    // specially handle offline/ingestion: DAF, Focused Crawler, Other
    {
        if (archdomain === "offline/ingestion/daf") {
            return "offline/ingestion/daf"
        }

        if ((archdomain === "offline/ingestion/focused_crawl") ||
            (archdomain === "offline/ingestion/seedserver") ||
            (archdomain === "offline/ingestion/maestro")) {
            return "offline/ingestion/focused_crawl";
        }
    }

    // specially handle infrastructure/core/kafka, infrastructure/core/zookeeper, monitoring, deployment
    {
        if (archdomain === "infrastructure/core/kafka") return archdomain;
        if (archdomain === "infrastructure/core/zookeeper") return archdomain;
        if (startswith(archdomain, "infrastructure/monitoring/")) return "infrastructure/monitoring";
        if (startswith(archdomain, "infrastructure/deployment/")) return "infrastructure/deployment";
    }

    if (archdomain === "" && d.env === "external") archdomain = "external";
    else if (archdomain === "external" && d.env === "aws-external") archdomain = "aws-external";
    else if (startswith(archdomain, "dev/")) archdomain = "dev";
    else if (startswith(archdomain, "infrastructure/")) archdomain = "infrastructure";
    else if (startswith(archdomain, "loader/")) archdomain = "loader";
    else if (startswith(archdomain, "offline/data/")) archdomain = "offline/data";
    else if (startswith(archdomain, "offline/content/")) archdomain = "offline/content";
    else if (startswith(archdomain, "offline/midtier/imageengine")) archdomain = "offline/midtier/imageengine";
    else if (startswith(archdomain, "offline/midtier/scoring")) archdomain = "online/midtier"; // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    else if (startswith(archdomain, "offline/ingestion/proxy")) archdomain = "offline/ingestion/proxy";
    else if (startswith(archdomain, "offline/ingestion/")) archdomain = "offline/ingestion";
    else if (startswith(archdomain, "online/midtier")) archdomain = "online/midtier";
    else if (startswith(archdomain, "online/shared/cassandra")) archdomain = "online/shared/cassandra";
    else if (startswith(archdomain, "online/shared/elasticsearch")) archdomain = "online/shared/elasticsearch";
    else if (startswith(archdomain, "online/shared/")) archdomain = "online/shared";
    else if (startswith(archdomain, "online/orchestration")) archdomain = "online/orchestration";
    else if (startswith(archdomain, "website/")) archdomain = "website";
    else if (startswith(archdomain, "science/")) archdomain = "science";
    else if (startswith(archdomain, "offline/")) archdomain = "offline";
    else if (archdomain === "mongo") archdomain = "mongo";
    else if (archdomain.indexOf('/') == -1) archdomain = archdomain;
    else archdomain = archdomain.substr(0, archdomain.indexOf('/')); 

    return archdomain;
}

