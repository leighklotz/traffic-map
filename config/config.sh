# By default just take one day's worth of data as the same.  Delete the directories if you want to start over.
DATE=`date +%Y-%m-%d`
YMD=$DATE

# Collect traffic from hosts in this region but collect names of hosts in all regions
REGION=us-west-1

# DATDIR is where the scp jobs copy tcpdump output to from the remote systems
DATDIR="/mnt/traffic/traffic-map/data/netgraph-dat-${DATE}"

# OUTPUT is where the instances and clusters JSON files go for serving; serve/node.sh symlinks this to $STATIC/data so node will serve it.
OUTPUT="/mnt/traffic/traffic-map/visualization"

# SCRIPTDIR is where this code runs.
SCRIPTDIR="/home/traffic/src/traffic-map"

# STATIC is where the static HTML files are
STATIC="/home/traffic/src/traffic-map/static"

# Foreign-IPs is well-known IP addresses that are not resolved
FOREIGN_IPS="/home/traffic/src/traffic-map/config/foreign-ips.txt"

HOSTS_TXT="${DATDIR}/hosts.txt"

# IPS is the list of hostnames and interface IP addresses.
IPS="${DATDIR}/ips.txt"

# List AWS security groups as well
COMPRESSED_SECURITY_GROUPS="${DATDIR}/security-groups.json.gz"

# timeouts etc to avoid getting stuck
SSHOPTS="-i /home/traffic/.ssh/id_rsa_unlocked -q -n -o ConnectTimeout=1 -o ConnectionAttempts=2 -o StrictHostKeyChecking=no -o BatchMode=yes -o PreferredAuthentications=publickey"

# CSV of Archdomain Tag, Component Owner, and Component UID
MASTER_ARCHDOMAIN_TAGS="/home/traffic/archdomain.csv"

# Admin Email
ADMIN_EMAIL=traffic@example.com

# Reports go here
REPORT_EMAIL=traffic@example.com
