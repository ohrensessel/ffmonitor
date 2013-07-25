ffmonitor
=========

A monitoring tool for Freifunk [http://freifunk.net] networks.
It was developed for Freifunk Hamburg [http://hamburg.freifunk.net/],
but should be usable for other Freifunk communities as well.
It works by pulling a nodes.json file from the respective freifunk
node graph website every minute.

You can see a running instance at http://www.ohrensessel.net/ffhh

This repository only contains the backend python code, the PHP
frontend code will be available in an extra repository shortly.

Features
--------
- [x] Graph number of clients, wlan links and vpn connections of each node.
- [x] Graph the overall network/mesh size.
- [x] Rough calculation of offline statistics for each node.
- [x] Multiple data source urls for fallback on errors.
- [x] Only new data is pulled from the Freifunk server and saved.
- [x] Human readable names of the nodes are saved.
- [ ] Handling of nodes that forever vanished from the network (delete rrd file, ...)
- [ ] Consider batman-adv timeouts when calculating number of clients

Installation
------------
Create a monitor.conf file (on the basis of monitor.conf.dist).
Adapt the path to your conf file in configuration.py (better solution to come),
use the full path.

update.py should be run every minute via cron
(the interval is not configurable at the moment)

graph.py could be run every five minutes via cron.
(or any other interval, depending on your needs)
Additionaly delay it by e.g. 30 seconds (by sleep 30) so that it does not run
in parallel with update.py.

stats.py could be run every hour via cron
(or any other interval if you think that is more suitable)


Requirements
------------------------------------------------
(probably incomplete at the moment)

rrdtool must be installed, along with the python rrdtool module.

The rrdcached daemon should be used to avoid high I/O when updating the rrd files (by update.py).

The python Requests module [http://docs.python-requests.org/en/latest/] must be installed.
