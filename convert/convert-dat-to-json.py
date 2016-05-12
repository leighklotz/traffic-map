#!/usr/bin/python

# Inspired by tcpdumpt2ot Gulfie@grotto-group.com formerly at http://www.grotto-group.com/~gulfie/projects/
# Outputs d3 Gravity files instead of Grapviz; written in Python instead of Perl
# collections only IP, not ethernet or port; relies on external code for providing IPs.  tags foreign
# vs local IPs.

from __future__ import print_function
from functools import partial
import json
import csv
import re
import sys
import math
from netifaces import ifaddresses, AF_INET
from collections import Counter, defaultdict
import socket
import operator
import pricing.instance_pricing as instance_pricing


def get_my_ip_addresses(interface_name):
  return [i['addr'] for i in ifaddresses(interface_name).setdefault(AF_INET, [{'addr':None}])]


def warn(msg, *args):
  print(msg.format(*args), file=sys.stderr)


def info(msg, *args):
  print(msg.format(*args), file=sys.stderr)

PORT_NAMES = {
  53: 'dns',
  80: 'http',
  123: 'ntp',
  443: 'https',
  3307: 'mysql',
  5514: 'syslog'
}

class Status(object):
  INTERFACE = "eth0"
#  PRUNE_LINKS_FRACTION = 0.25
  PRUNE_LINKS_FRACTION = 1.00
  DEBUG = False
  VERBOSE = True

  LINE_ADDR_MATCH_REGEXP = r'^[0-9.:]+ IP (\d+\.\d+\.\d+\.\d+)\.(\d+)* (>) (\d+\.\d+\.\d+\.\d+)\.(\d+)*: (Flags \[([A-Z.]+)\])?'
  ARP_MATCH_REGEXP = r'^[0-9.:]+ ARP,'
  ICMP_MATCH_REGEXP = r'^[0-9.:]+ IP (\d+\.\d+\.\d+\.\d+) (>) (\d+\.\d+\.\d+\.\d+): ICMP'

  BLUE = '#1f77b4'
  ORANGE = '#ff7f0e'
  GREEN = '#2ca02c'

  def __init__(self):
    self.linesok = 0
    self.lines = 0
    self.nlinks = 0
    self.ignored_packet_lines = 0
    self.ignored_host_lines = 0
    self.ignored_port_lines = 0
    self.pruned = ""
    self.node_counts = Counter()
    self.link_counts = defaultdict(Counter)
    self.link_port_pair_counts = defaultdict(partial(defaultdict, Counter))
    self.host_ports_seen = defaultdict(set)
    self.edge_present = defaultdict(Counter)
    self.ip_to_label_table = {}
    self.ip_to_env_table = {}
    self.ip_to_archdomain_table = {}
    self.ip_to_instance_type_table = {}
    self.ip_to_price_table = {}
    self.ip_to_region_table = {}
    self.node_indices = {}
    self.skip_ip_addresses = set(get_my_ip_addresses(self.INTERFACE))
    self.skip_ports = {53, 123, 5514} # DNS, NTP, syslog
#    self.skip_hostname_regex = r'/splunk-|/infrastructure/monitoring/sensu|infrastructure/monitoring/graphite|opsource\.net|/navigator-|bignay.canonical.com|infrastructure/monitoring/datastax/'
    self.skip_hostname_regex = None
    self.instance_pricer = instance_pricing.InstancePricing()

  def process(self, DATFILE):
    with open(DATFILE, 'rb') as datfile:
      for line in datfile:
        self.lines += 1

        match = re.search(self.LINE_ADDR_MATCH_REGEXP, line)
        if match:
            sip = match.group(1)
            dip = match.group(4)
            sport = int(match.group(2))
            dport = int(match.group(5))
            separator = match.group(3)
            flags = match.group(7)
            self.linesok += 1
            if (separator == 'tell'):
              self.ignored_packet_lines += 1
            else:
              listening_port = self.pick_listening_port(flags, sport, dport)
              self.node_counts[sip] += 1
              self.node_counts[dip] += 1
              self.host_ports_seen[dip].add(listening_port)
              self.host_ports_seen[sip].add(listening_port)

              if sip in self.skip_ip_addresses or dip in self.skip_ip_addresses:
                self.ignored_host_lines += 1
              elif sport in self.skip_ports or dport in self.skip_ports:
                self.ignored_port_lines += 1
              elif self.skip_hostname_regex and (re.search(self.skip_hostname_regex, self.hostify(sip)) or re.search(self.skip_hostname_regex, self.hostify(dip))):
                self.ignored_host_lines += 1
              else:
                self.link_port_pair_counts[sip][dip][listening_port] += 1
                self.edge_present[sip][dip] = 1
                self.edge_present[dip][sip] = 1
                self.link_counts[sip][dip] += 1
        elif re.search(self.ARP_MATCH_REGEXP, line) or line=="\n" or re.search(self.ICMP_MATCH_REGEXP, line):
          self.linesok += 1
          self.ignored_host_lines += 1
          pass
        else:
          warn("Unable to get IP addrs from ({})", line)

  def pick_listening_port(self, flags, sport, dport):
    if flags is None:
      pass
    elif flags == 'P.' or flags == 'F.' or flags == '.' or flags == 'R.':
      pass
    elif flags == 'S.':
      return sport
    elif flags == 'S':
      return dport
    
    if sport < dport:
      return sport
    else:
      return dport
    

  # ips.txt
  # TSV: REGION	NAME	INSTANCE_TYPE	[SPOT|ON-DEMAND]	ARCHDOMAIN	ENV_TAG	IP1	IP2...
  def read_ips(self, ips_txt):
    info("Reading {}", ips_txt)
    with open(ips_txt,'rb') as tsvin:
      tsvin = csv.reader(tsvin, delimiter='\t')
      for parsed in tsvin:
        i = 0
        if len(parsed) > 0:
          region = parsed[i].lower(); i += 1
          name = parsed[i].lower(); i += 1
          instance_type = parsed[i].lower(); i += 1
          price = parsed[i]; i+= 1
          archdomain = parsed[i].lower(); i += 1
          env_tag = parsed[i].lower(); i += 1
          for ip in parsed[i:]:
            self.ip_to_env_table[ip] = env_tag
            self.ip_to_archdomain_table[ip] = archdomain
            self.ip_to_instance_type_table[ip] = instance_type
            self.ip_to_price_table[ip] = float(price)
            self.ip_to_region_table[ip] = region
            if name != "unknown":
              self.ip_to_label_table[ip] = archdomain + "/" + name
            else:
              self.ip_to_label_table[ip] = archdomain + "/" + ip

  # foreign_ips.txt
  # TSV: NAME	IP1	IP2...
  def read_foreign_ips(self, fn):
    info("Reading {}", fn)
    with open(fn,'rb') as tsvin:
      no_comment = (row for row in tsvin if not row.startswith('#'))
      tsvin = csv.reader(no_comment, delimiter='\t')
      for parsed in tsvin:
        if len(parsed) < 2:
          raise(Exception("Unable to parse line in TSV file " + fn+"; line=" + str(parsed)))
        else:
          i = 0
          name = parsed[i].lower()
          for ip in parsed[i:]:
            self.ip_to_label_table[ip] = name
            self.ip_to_env_table[ip] = "external"


  def build_nodes(self):
    info("Building nodes")
    return [self.build_node(ip) for ip in self.node_counts.keys()]

  def build_node(self, ip):
    hostified_name = self.hostify(ip)
    env_tag = self.ip_to_env_table.get(ip, "external")
    if self.ip_to_env_table.get(ip, "external") != "external":
      ip_type = "internal"
    elif ip.startswith("10.") or hostified_name.endswith("amazonaws.com"):
      ip_type = "aws"
      env_tag = "aws-external"
    else:
      ip_type = "external"

    region = None
    price = 0.0
    instance_type = self.ip_to_instance_type_table.get(ip, "unknown")
    if instance_type is not "unknown":
      region = self.ip_to_region_table.get(ip, "unknown")
      price = self.ip_to_price_table.get(ip, "unknown")

    archdomain = self.ip_to_archdomain_table.get(ip, "external")

    if hostified_name != "unknown" and not self.match_ip_addr(hostified_name):
      if self.match_aws_compute_name(hostified_name):
        label = hostified_name+ ':' + (','.join([ self.portify(x) for x in self.host_ports_seen[ip]]))
      else:
        label = hostified_name
    else:
      label = ip + ':' + (','.join([ self.portify(x) for x in self.host_ports_seen[ip]]))

    traffic = 1 + int(math.log10(self.node_counts[ip]))
    return {
        "name": ip, 
        "label": label, 
        "env": env_tag, 
        "ip_type": ip_type, 
        "traffic": traffic, 
        "archdomain": archdomain, 
        "instance_type": instance_type, 
        "price": price,
        "region": region
    }


  def portify(self, port):
    return PORT_NAMES.get(port, str(port))

  def calculate_node_indices(self, nodes):
    info("Building node indices")
    i = 0
    for n in nodes:
      self.node_indices[n['name']] = i
      i += 1


  _host_cache = dict()

  def match_ip_addr(self, txt):
    return re.match(r'((\d{1,3}\.){3}\d{1,3})', txt)
    
  def match_aws_compute_name(self, txt):
    return re.match(r'ip-(\d{1,3}\-){3}\d{1,3}\.[a-z]+-[a-z]+-[0-9]+\.compute.internal', txt)    

  def hostify(self, ip):
    def _hostify(self, ip):
      ret = ip

      # fix, more range checking
      match = self.match_ip_addr(ip)
      if match:
        fullip = match.group(1)

        if fullip in self.ip_to_label_table:
            ret = self.ip_to_label_table[fullip]
        else:
          try:
            tuple = socket.gethostbyaddr(fullip)
            if tuple:
              ret = tuple[0]
          except socket.herror:
            pass
      return ret

    if ip in self._host_cache:
      return self._host_cache[ip]
    else:
      ret = _hostify(self, ip)
      self._host_cache[ip] = ret
      return ret


  def build_links(self):
    return [self.build_link_component(src, dst) for src in sorted(self.link_counts.keys()) for dst in sorted(self.link_counts[src].keys())]

  def build_link_component(self, src, dst):
    cnt = self.link_counts[src][dst]
    self.nlinks += 1
    traffic = 1 + int(math.log10(cnt))  # ln
    src_idx = self.node_indices[src]
    target_idx = self.node_indices[dst]
    link_port_pair_counts = self.link_port_pair_counts[src][dst]
    return {"source": src_idx, "target": target_idx, "source_name": src, "target_name": dst, "value": traffic, "ports": sorted(list(link_port_pair_counts))}


  # Prune links to/from hosts because they exceed link fraction
  def prune_hog_links(self, links, nodes, frac):
    info("pruning hog links")
    nnodes = len(self.node_counts)
    hogs = {k:len(v) for k,v in self.edge_present.items() if ((float(len(v))) / nnodes) > frac}
    percent = int(Status.PRUNE_LINKS_FRACTION * 100)
    self.pruned = str(len(hogs)) + ": " + (', ').join(["{} (talking to {} hosts, >{percent}% of all hosts)".format(self.hostify(rec[0]), rec[1], percent=percent) for rec in sorted(hogs.items(), key=operator.itemgetter(1), reverse=True)])
    # prune hogs
    kept = [link for link in links if not(link['source_name'] in hogs or link['target_name'] in hogs)]
    return kept

  def find_node_by_label(self, nodes, label):
    for node in nodes:
      if node['label'] == label:
        return node
    return None

  def main(self, ips_txt, foreign_ips_txt, datfile, outjson):
    self.outjson = outjson
    self.read_ips(ips_txt)
    self.read_foreign_ips(foreign_ips_txt)
    self.process(datfile)
    nodes = self.build_nodes()
    self.calculate_node_indices(nodes)
    links = self.build_links()
    links = self.prune_hog_links(links, nodes, self.PRUNE_LINKS_FRACTION)
    failed = self.lines - self.linesok
    about = {
      'lines':self.lines,
      'linesok':self.linesok,
      'ignored_packet_lines':self.ignored_packet_lines,
      'ignored_host_lines':self.ignored_host_lines,
      'ignored_port_lines':self.ignored_port_lines,
      'skip_ports':list(self.skip_ports),
      'skip_ip_addresses':list(self.skip_ip_addresses),
      'skip_hostname_regex':self.skip_hostname_regex,
      'pruned':self.pruned,
      'failed':failed,
      'nnodes':len(self.node_counts),
      'nlinks':self.nlinks
    }

    report = """
            total input lines : {lines}
            total read lines  : {linesok}
            ignored packet    : {ignored_packet_lines}
            ignored host      : {ignored_host_lines} ({skip_ip_addresses}, {skip_hostname_regex})
            ignored port      : {ignored_port_lines} (port {skip_ports})
            failed lines      : {failed}
            nodes             : {nnodes}
            links	      : {nlinks}
            pruned	      : {pruned}
    """.format(**about)

    info("Writing Graph")
    graph = {"nodes": nodes, "links": links, "about": about}
    with open(self.outjson, 'w') as f:
      json.dump(graph, f, indent=2)

    if (self.DEBUG or self.VERBOSE):
      info("Report: {}", report)

if __name__ == "__main__":
  if len(sys.argv) < 4:
    warn("usage: {} ips.txt config/foreign_ips.txt DATFILE OUTJSON", sys.argv[0])
    exit(-1)
  else:
    ips_txt = sys.argv[1]
    foreign_ips_txt = sys.argv[2]
    datfile = sys.argv[3]
    outjson = sys.argv[4]
    status = Status()
    status.main(ips_txt, foreign_ips_txt, datfile, outjson)
