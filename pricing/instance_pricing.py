#!/usr/bin/python

from __future__ import print_function

import os
import json
import requests
import urlparse

from pricing.nav import nav
from pricing.aws_regions import AWS_REGION_LONG_NAMES
from pricing.memoizer import memoized

# evil
INSTANCE_PRICES_FILENAME = '/tmp/aws-prices.json'

INSTANCE_PRICES_URL_PREFIX="https://pricing.us-east-1.amazonaws.com/"
OPERATING_SYSTEM="Linux"
TENANCY='Shared'


class InstancePricing(object):
    def __init__(self):
        if not os.path.isfile(INSTANCE_PRICES_FILENAME):
            self.retrieve_pricing_file()
        with open(INSTANCE_PRICES_FILENAME, 'r') as infile:
            pricing = json.load(infile)
        vers = nav(pricing, 'formatVersion')
        if vers != "v1.0":
            raise Exception("Expected version v1.0 but got {}".format(vers))
        self.products = nav(pricing, 'products')
        self.terms = nav(pricing, 'terms')

    def retrieve_pricing_file(self):
        # http://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html
        OFFERS_URL=urlparse.urljoin(INSTANCE_PRICES_URL_PREFIX, "/offers/v1.0/aws/index.json")
        offers = requests.get(OFFERS_URL).json()
        AMAZONEC2_URL = urlparse.urljoin(INSTANCE_PRICES_URL_PREFIX, offers['offers']['AmazonEC2']['currentVersionUrl'])
        ec2_prices = requests.get(AMAZONEC2_URL).json()
        with open(INSTANCE_PRICES_FILENAME, 'w') as f:
            print(json.dumps(ec2_prices), file=f)

    @memoized
    def get_spot_pricing(self, ec2, spot_instance_request_id):
        # inefficient
        spot_instance_requests = ec2.get_all_spot_instance_requests(request_ids=[spot_instance_request_id])
        return spot_instance_requests[0].price
        
    @memoized
    def get_ondemand_pricing(self, region, instance_type):
        def pick_one(d):
            return d.itervalues().next()

        location = AWS_REGION_LONG_NAMES[region]

        (sku,product) = [
            (sku, nav(product, 'attributes'))
            for sku,product in self.products.items() 
            if (nav(product, 'attributes.instanceType')==instance_type and 
                nav(product, 'attributes.operatingSystem') == OPERATING_SYSTEM and 
                nav(product, 'attributes.location') == location and 
                nav(product, 'attributes.tenancy') == TENANCY)
        ][0]
        price = float(nav(pick_one(nav(pick_one(self.terms['OnDemand'][sku]), "priceDimensions")), 'pricePerUnit.USD'))
        return price

        

if __name__ == "__main__":
    print(InstancePricing().get_ondemand_pricing('ap-southeast-1', 'm1.small'))
    print(InstancePricing().get_spot_pricing('ap-southeast-1', 'm1.small'))
    print(InstancePricing().get_ondemand_pricing('ap-southeast-1', 'm1.small'))
