#!/usr/bin/env python
import sys, os
import math
import json
from collections import defaultdict

class ClusterEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, Cluster):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)


class Cluster(object):
    def __init__(self):
        self.env = None
        self.regions = set()
        self.archdomain = None
        self.ips = set()
        self.price = 0
        self.labels = set()
        self.instance_type = set()
        self.traffic = 0
        self.label = None

    def to_dict(self):
        r = { 'env': self.env,
                 'regions': list(self.regions),
                 'archdomain': self.archdomain,
                 'label': self.env + "|" + self.archdomain,
                 'ips': list(self.ips),
                 'price': self.price,
                 'labels': list(self.labels),
                 'instance_type': list(self.instance_type),
                 'traffic': self.traffic,
             }
        return r

    def adjoin(self, node):
        if self.env == None:
            self.env = node['env']
        elif self.env != node['env']:
            raise Exception("Trying to adjoin node in env {} to cluster in env {}".format(node['env'], self.env))
        if self.archdomain == None:
            self.archdomain = node['archdomain']
        elif self.archdomain != node['archdomain']:
            raise Exception("Trying to adjoin node in archdomain {} to cluster in archdomain {}".format(node['archdomain'], self.archdomain))
        self.regions.add(node['region'])
        self.labels.add(node['label'])
        self.ips.add(node['name'])
        self.price += node['price']
        self.instance_type.add(node['instance_type'])
        self.traffic = math.log10(pow(10, int(self.traffic)-1) + pow(10, int(node['traffic'])-1))+1
        self.label = self.env + "|" + self.archdomain


class Coalescer(object):
    def __init__(self):
        self.envs = defaultdict(lambda: defaultdict(Cluster))
        self.nested_links = defaultdict(lambda: defaultdict(lambda: dict()))
        self.clusters_by_node_ip = dict()
        self.nodes_by_node_ip = dict()

    def main(self, fn_in, fn_out):
        original = self.load_original(fn_in)
        about,envs,nested_links,output_nodes,output_links = self.coalesce(original)
        
        self.reserialize({
            'envs': envs, 
            'nested_links': nested_links,
            'about': about,
            'nodes': output_nodes, 'links': output_links},
                         fn_out)


    def load_original(self, fn):
        with open(fn, 'r') as f:
            return json.load(f)

    def add_nodes(self, nodes):
        for node in nodes:
            env = node['env']
            archdomain = node['archdomain']

            self.envs[env][archdomain].adjoin(node)
            self.nodes_by_node_ip[node['name']] = node

    def coalesce(self, original):
        about = original['about'].copy()
        about['coalesced'] = True

        nodes = original['nodes']
        self.add_nodes(nodes)

        for env_clusters in self.envs.values():
            for cluster in env_clusters.values():
                for ip in cluster.ips:
                    self.clusters_by_node_ip[ip] = cluster

        original_links = original['links']
        for link in original_links:
            source_node = self.nodes_by_node_ip[link['source_name']]
            target_node = self.nodes_by_node_ip[link['target_name']]
            source_env = source_node['env']
            target_env = target_node['env']
            source_cluster = self.clusters_by_node_ip[source_node['name']]
            target_cluster = self.clusters_by_node_ip[target_node['name']]

            d = self.nested_links[source_env + "|" + source_cluster.archdomain][target_env + "|" + target_cluster.archdomain] 

            d['value'] = d.get('value', 0) + link['value']
            d['ports'] = d.get('ports', set())
            d['ports'] |= set(link['ports'])

        output_nodes = [
            cluster for env in self.envs.values() for cluster in env.values()
        ]

        output_links = [{"source_name": source_cluster_name, 
                         "target_name": target_cluster_name, 
                         "source": self.find_index_by_label(source_cluster_name, output_nodes),
                         "target": self.find_index_by_label(target_cluster_name, output_nodes),
                         "ports": target_cluster['ports'],
                         "value": 1+10*math.log10(target_cluster['value'])
                        }
                        for source_cluster_name, targets in self.nested_links.items() 
                        for target_cluster_name, target_cluster in targets.items() ]

        
        return about, self.envs, self.nested_links, output_nodes, output_links


    def find_index_by_label(self, label, output_nodes):
        for i,x in enumerate(output_nodes):
            if x.label == label:
                return i
        raise Exception("cannot find " + label + " in " + output_nodes)

    def reserialize(self, envs, fn_out):
        print("Writing to {}".format(fn_out)) 
        with open(fn_out, 'w') as f:
            json.dump(envs, f, indent=4, cls=ClusterEncoder)




if __name__ == '__main__':
    
    _fn_in = sys.argv[1] # 'visualization/data/out-2015-09-08.json'
    _fn_out = sys.argv[2] # 'visualization/data/clusters-2015-09-08.json'
    coalescer = Coalescer()
    coalescer.main(_fn_in, _fn_out)
