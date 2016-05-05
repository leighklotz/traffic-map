# Traffic Map

Author: Leigh L. Klotz, Jr. <klotz@klotz.me>

## Summary

Visualizes TCP Network Traffic from a large number of servers and
combines with metadata about servers and their services in a map
highlighting environments and architecture domains.  The servers or clusters are drawn as circle nodes and lines between them represent traffic collected during the minute of monitoring.  Checkboxes allow you to suppress certain types of traffic in visualization to prevent all nodes from being connected together by monitoring.

The visualization is clustered by archdomain and env.  Env is the traditional list but expandable: prod, stage, etc.  Archdomain is a hierarchical name structure of what function an instance uas, and are usually identified with clusters.  The name parts are alphabetical and separated with slash; they do not start with slash.  For example, all online systems are "online/*" and all offline systems are "offline/*".  For example, online mid-tier services are "online/midtier/_name_."  You can edit tags.js to change these field types.  

There are three major modes of grouping: ungrouped, grouped by archdomain, and grouped by archdomain.  You can also choose to allow traffic to extert a bigger or smaller influence on layout.  D3 and D3 gravity offer many layout mechanisms and you can change lots of parameters in graph.ks.

In practice, grouping by archdomain does not appear to be useful, but group by env is.
There are three major data sets to visualize: instances, clusters (named by archdomain), and security-groups.  Ideally security-groups would mirror clusters.

## Caveats

This software has never been configured or run outside of the initial AWS environment where it was developed.  It needs some work to be more generally useful.

# Screenshots

![Clusters](/screenshots/Clusters.png)

For more, see [screenshots](/screenshots).

# Guide to files

## config/
- config/config.sh:
Edit this file to change pathmames, email addresses, etc.
Traffic Data is collected into $DATDIR.  Convert writes the clustered data for visualization into $OUTPUT.  Both of these need to be on a largeish disk, not inside a docker image for example.
Node serves the visualization files from $STATIC/data (unfortunate dual use of the name 'data') which is a symlink created by serve/start-node.sh.  (This twisty maze could be cleaned up.)
- config/foreign-ips.txt:
Manually put hostnames in here for services that we can't find by reverse DNS.  Typically contains well-known names like AWS DNS server, etc.  Not critical but will help you not be startled if you see hosts talking to what appear to be non-EC2 hosts.

## collect/
- collect/fabconfig.ini:
edit this file to change pathmames as well as the config/config.sh.
- collect/gather-dat.sh
reads the sudo password. the sudo password is kept in env and it is not written to disk or used in a cli where it might show up in ps.
passes the password via stdout to fab, which is the only user of the password.  after it runs fab with the list of hosts (from list/) it cats all the host-{ip}.dat files together to all.dat and gzips the host-*.dat files.
looking at the host-*.dat files is not that useful unless you need details about the tcp port and src/dest in individual calls, not just in aggregate for the host pair.  it would save disk space to remove them since nothing uses them later.
keeping all.dat is good in case you want to re-process old files, but bear in mind that it will re-proecss them with the new view of ip addresses, prices, etc., which change rapidly on aws, so it's not important to keep more than a day or two if you want to delete them.

## - collect/capture-packets.sh
fab runs this file on all remote hosts.  it writes its output to /tmp/captured-packets.dat via a temp name, so that if that file exists, it is complete.  fab scp copies it back to $datdir/host-${ip}.dat.
running tcpdump requires root access.  you can use usergroups to do this instead: http://www.stev.org/post/2012/01/19/getting-tcpdump-to-run-as-non-root.aspx
however that requires setting up a specific user.  so that might be better if you can swing it and then you can eliminate the passwords from gather-dat.sh and collect/fabfile.py.
- collect/backup.sh:
backs up to s3, using "aws s3 sync" cli. this file is self-configured, sadly.
- collect/get-uptime-load.sh
uses fab to collect uptime, cpuload, and memory statistics to $datdir in individual files named uptime-{ip}.dat etc.  Not currently automated or used but would be a valuable addition.

## start.sh:
Run this to start both traffic collection and and serving.  You will need to run "screen -r traffic-map" (as it will tell you) to type in the sudo password for the account this script runs as.
It also starts serve/serve-node.sh in another screen.  Again, this could all be made a service if you can eliminate the sudo password.

## doit.sh
doit.sh loops and runs once a day (if you give it a time on the CLI) or immediately and exits if you don't.
doit.sh runs the list/, collect/, and convert/ phases followed by utils/archdomain and collect/backup (to S3).  S3 location is specified in config/config.sh
Normally you don't run doit.sh yourself, you run start.sh, and you don't have to run it often.  (Again, if you can eliminate the sudo password you can set this up as a service instead of having to run it via a shell.)
This host can monitor only hosts in its own EC2 region.

## list/
List uses Python boto to collect the list of EC2 hosts, their public and private IP addresses, archdomain and env tags, and machine class.  It uses pricing/ to collect the hourly price for on-demand, and the last effective hourly price for spot.
It writes all this in 

## convert/
convert/convert-dat-to-json.sh runs convert/convert-dat-to-json.py and converts the ${DATDIR}/all.dat and ${IPS} from host listign to output to JSON data in ${OUTPUT}/instances-${YMD}.json and gzips all.dat.
convert/coalesce-to-cluster.sh runs conver/coalesce-to-cluster.py and operates on the output of conver-dat-to-json.  It collects together data about individual hosts and clusters it by archdomain and env.  It puts its output in ${OUTPUT}/clustesr-${YMD}.json.
If you have a large number of hosts and if your archdomain and env tags are widely used, then the clustered view is more valuable and displays more quickly.

## pricing/
- instance_pricing.py offers a module used by list/list-ec2-hosts-table.py to put the current price of ondemand and spot instances (last hour) in ${IPS}.  it uses aws_regions, spot_pricing, memoizer, nav, and __init__.py to do this.
- pricing has its own requirements.txt file for python modules because it's used only on aws.
- Other files such as *-costs.sh and *-costs.py produce various reports, and are run by hand as neede, but may not be useful.

## requirements.txt
list of modules used in main python code, but not in pricing

## screenshots/
- examples of what output looks like, for README.md

## security-groups/
aws security groups listing.  ideally, the security groups would be laid out along archdomain lines and the system would form (like a coral reef ;-) on the substrate.  doit.sh collects security groups daily and you can visualize them to see how close they are to the clusters view.
main entry point is security-groups/list-security-groups.sh.  aws only.
- map of existing security groups to existing archdomains to help heuristic algorithm.
- add more of your own and copy  security_group_archdomains.py.sample to security_group_archdomains.py


## serve/
- serve-node.sh
Uses node to serve the static/ directory and enables serving data/ via symlink.  Python HTTP server was prone to deadlocks and was slow to serve up the big data files.  Visit http://traffic-map-hostname:8000 to get the UI.
Press the X button to get a list of filenames, but it's generated on load because this node server can't do directory list.  So reload the page each day for new data.

## static/
- the files needed for the single-page webapp, served by node.  the data/ symlink points to the $OUTPUT directory and node needs to follow-symlinks.
- index.html: edit this file to change the regexs of archdomains to onit, in the fieldset id="omit_traffic_archdomain_regexes" and id="omit_traffic_env_regexes".
- graph.js: the D3 graphing code using gravity. 
- tags.js: edit this file to list your environment focus nodes (big bubbles) and your tag focus nodes.  tag focus nodes don't seem to be that useful for the archdomain-centric view.
  in particular you can fix up or shorten archdomain tags in function sanitize_archdomain.

## utils/
- a variety of things
- utils/compare-archdomain-to-master.sh is run by doit.sh and it sends daily email to ${REPORT_EMAIL} from config/config.sh about the comparison of seen and allowed archdomain tags.
  The list of allowed archdomain tags is in ${MASTER_ARCHDOMAIN_TAGS} from config/config.sh.  You need to find this directory and update it yourself regularly with archdomains.csv.
- howfar.sh, howlong.sh
  Monitors the sleep that doit.sh runs.  Could be removed if you make this run as a service.
- tcpdump-bandwidth, cross-env-traffic, whocalls, etc.  CLI utilities which might or might not work.


## Other files:
- ~/.ssh used for ssh keys (see collect/fabconfig.ini).  Key must not be password protected.
- ~/.aws/config for AWS keys used for aws cli and boto.  Needs privileges to read security groups, read EC2, etc.


# Similar Projects

I was inspired by tcpdumpt2dot Gulfie@grotto-group.com formerly at
http://www.grotto-group.com/~gulfie/projects/ which used Graphviz, but
eventually the scale and inability for direct clustering guided me to
a re-write from scratch.  Traffic Map outputs D3 Gravity files instead
of Graphviz; written in Python instead of Perl.  See 
https://web.archive.org/web/20071104191340/http://www.grotto-group.com/~gulfie/projects/analysis/tcpdump2dot.subpage.html

# Resources used
- [d3.js](http://d3js.org/) (BSD License)
- [colorbrewer](http://colorbrewer.org/) (Apache License)
- [d3.tip](https://github.com/Caged/d3-tip/) (MIT License)
- [lodash](http://lodash.com/) (MIT License)
- [jquery](http://jquery.org/) (MIT License)

# LICENSE
Since traffic-map was inspired by tcpdumpt2dot, which was offered under GPLv2, this software carries the same license.
- [LICENSE](LICENSE)

# Copyright
Copyright 2016 Leigh L. Klotz, Jr. All Rights Reserved.
