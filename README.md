# CloudStack Chaos Monkey

## Summary

Simple choas monkey for CloudStack based clouds.

* Python 2.6+ and 3.3+ support
* Uses [cs](https://github.com/exoscale/cs)
* GPL license

## Usage

~~~
$ ./cs-chaosmonkey.py -h
usage: cs-chaosmonkey.py [-h] [--group GROUP]
                         [--max-not-running MAX_NOT_RUNNING]
                         [--chaos-action {reboot,stop,stop-wait-start,no-action,ask-monkey}]
                         [--min-wait MIN_WAIT] [--max-wait MAX_WAIT]

optional arguments:
  -h, --help            show this help message and exit
  --group GROUP         Name of instances group, default: None
  --max-not-running MAX_NOT_RUNNING
                        Max allowed VM not running, default: 1
  --chaos-action {reboot,stop,stop-wait-start,no-action,ask-monkey}
                        Monkey action, default: ask-monkey
  --min-wait MIN_WAIT   Wait at least some time in seconds, default: 10
  --max-wait MAX_WAIT   Wait at most some time in seconds, default: 300
~~~

## Examples

~~~
# Make an random action of a random node but only if all nodes are running
./cs-chaosmonkey.py

# Make an random action of a random node even if 1 node is down
./cs-chaosmonkey.py --max-not-running 1

# Stop wait start a node of the group web, wait is random in range of 10-300 secs
./cs-chaosmonkey.py --group web --chaos-action stop-wait-start
~~~

Seeing it in action

~~~
$ ./cs-chaosmonkey.py
action: stop-wait-start
stop-wait-start web-01
..........
Wating 228
.........
~~~
