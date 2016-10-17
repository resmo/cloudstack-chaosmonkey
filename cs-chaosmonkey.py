#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2016, René Moser <mail@renemoser.net>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import sys
import argparse
import random
import time

try:
    from cs import CloudStack, CloudStackException, read_config
except ImportError as e:
    sys.stderr.write("pip install cs: %s" % str(e))
    sys.exit(1)

class CloudStackChaosMonkey(object):

    def __init__(self, group, chaos_action, max_not_running=0, min_wait=10, max_wait=300):
        self.actions = [
            'reboot',
            'stop',
            'stop-wait-start',
            'no-action',
        ]
        self.cs = CloudStack(**read_config())
        self.max_not_running = max_not_running
        self.group = group
        self.chaos_action = chaos_action
        self.min_wait = min_wait
        self.max_wait = max_wait

    def get_instances(self):
        group = self.get_instance_groups()
        if group:
            instances = self.cs.listVirtualMachines(instancegroupid=group['id'])
        else:
            instances = self.cs.listVirtualMachines()
        if not instances:
            sys.stderr.write("No VMs found")
            sys.exit(1)

        instances_not_running = 0
        for instance in instances.get('virtualmachine', []):
            if instance['state'].lower() != "running":
                instances_not_running += 1
                if instances_not_running > self.max_not_running:
                    print ("max-not-running reached: %s > %s. Avoiding too much chaos." % (instances_not_running, self.max_not_running))
                    sys.exit(0)
        return instances.get('virtualmachine', [])

    def get_instance_groups(self):
        if not self.group:
            return None
        groups = self.cs.listInstanceGroups(name=self.group)
        if not groups:
            sys.stderr.write("No group %s found" % self.group)
            sys.exit(1)
        return groups['instancegroup'][0]

    def make_chaos(self):
        instances = self.get_instances()
        random_number = random.randint(0, len(instances)-1)
        instance = instances[random_number]
        if instance['state'].lower() != "running":
            return
        action = self.find_action()
        print("action: %s" % action)

        if action == "stop":
            print("stop %s" % instance['displayname'])
            res = self.cs.stopVirtualMachine(id=instance['id'])
            instance = self.poll_job(res, 'virtualmachine')
        elif action == "reboot":
            print("reboot %s" % instance['displayname'])
            res = self.cs.rebootVirtualMachine(id=instance['id'])
            instance = self.poll_job(res, 'virtualmachine')
        elif action == "stop-wait-start":
            print("stop-wait-start %s" % instance['displayname'])
            res = self.cs.stopVirtualMachine(id=instance['id'])
            instance = self.poll_job(res, 'virtualmachine')
            random_number = random.randint(self.min_wait, self.max_wait)
            print("Wating %s" % random_number )
            time.sleep(random_number)
            res = self.cs.startVirtualMachine(id=instance['id'])
            instance = self.poll_job(res, 'virtualmachine')

    def find_action(self):
        if self.chaos_action not in self.actions:
            random_number = random.randint(0, len(self.actions)-1)
            return self.actions[random_number]
        else:
            return self.chaos_action

    def poll_job(self, job=None, key=None):
        if 'jobid' in job:
            while True:
                res = self.cs.queryAsyncJobResult(jobid=job['jobid'])
                if res['jobstatus'] != 0 and 'jobresult' in res:
                    if 'errortext' in res['jobresult']:
                        self.module.fail_json(msg="Failed: '%s'" % res['jobresult']['errortext'])
                    if key and key in res['jobresult']:
                        job = res['jobresult'][key]
                    sys.stdout.write("\n")
                    break
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(2)
        return job

def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--group', help="Name of instances group, default: None")
        parser.add_argument('--max-not-running', type=int, default=0, help="Max allowed VM not running, default: 0")
        parser.add_argument('--chaos-action', choices=['reboot', 'stop', 'stop-wait-start', 'no-action', 'ask-monkey'], default='ask-monkey', help="Monkey action, default: ask-monkey")
        parser.add_argument('--min-wait', type=int, default=10, help="Wait at least some time in seconds, default: 10")
        parser.add_argument('--max-wait', type=int, default=300, help="Wait at most some time in seconds, default: 300")
        args = parser.parse_args()

        monkey = CloudStackChaosMonkey(max_not_running=args.max_not_running, group=args.group, chaos_action=args.chaos_action, min_wait=args.min_wait, max_wait=args.max_wait)
        monkey.make_chaos()

    except CloudStackException as e:
        sys.stderr.write("CloudStackException: %s" % str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
