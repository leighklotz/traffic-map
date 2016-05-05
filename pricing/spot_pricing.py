#!/usr/bin/env python

from __future__ import print_function

import boto3
import sys
from datetime import datetime, timedelta
import dateutil.tz

from memoizer import memoized

class SpotPricing(object):
    def __init__(self):
        self.ec2 = boto3.client('ec2')

    # this is an estimate based on recent prices
    # http://stackoverflow.com/questions/11780262/calculate-running-cumulative-cost-of-ec2-spot-instance 
    @memoized
    def get_spot_instance_pricing(self, instance_type, start_time, end_time, availability_zone, spot_instance_request_id=None):
        # don't fetch any more since this is an approximation of hourly cost anyway
        # we can only report the accumulated cost for the time period we examine,
        # not the total time.

        max_results = 30
        result = self.ec2.describe_spot_price_history(InstanceTypes=[instance_type], StartTime=start_time, EndTime=end_time,
                                                      AvailabilityZone=availability_zone, MaxResults = max_results)
        total_cost = 0.0
        total_seconds = (end_time - start_time).total_seconds()
        total_hours = total_seconds / (60*60)
        computed_seconds = 0

        last_time = end_time
        for price in result["SpotPriceHistory"]:
            price["SpotPrice"] = float(price["SpotPrice"])

            available_seconds = (last_time - price["Timestamp"]).total_seconds()
            remaining_seconds = total_seconds - computed_seconds
            used_seconds = min(available_seconds, remaining_seconds)

            total_cost += (price["SpotPrice"] / (60 * 60)) * used_seconds
            computed_seconds += used_seconds

            last_time = price["Timestamp"]

        return float("{0:.3f}".format((total_cost / (computed_seconds / (60.0 * 60.0)))))

if __name__ == "__main__":
    def main():
        instance_type = sys.argv[1]
        availability_zone = sys.argv[2]
        now = datetime.utcnow()
        now = now.replace(tzinfo=dateutil.tz.tzutc())

        spot_pricing = SpotPricingHistory()
        print("recent average_cost=%g" %
              (spot_pricing.get_spot_instance_pricing(instance_type, now-timedelta(hours=1), now, availability_zone)))

    main()
