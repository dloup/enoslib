from enoslib.api import generate_inventory
from enoslib.infra.enos_g5k.provider import G5k
from enoslib.infra.enos_vmong5k.provider import start_virtualmachines
import enoslib.infra.enos_vmong5k.configuration as vmconf
from enoslib.infra.enos_g5k.configuration import (Configuration,
                                                  NetworkConfiguration)

import logging
import os

logging.basicConfig(level=logging.INFO)

# path to the inventory
inventory = os.path.join(os.getcwd(), "hosts")

# claim the resources
conf = Configuration.from_settings(job_type="allow_classic_ssh")
prod_network = NetworkConfiguration(id="n1",
                                    type="prod",
                                    roles=["my_network"],
                                    site="rennes")
conf.add_network_conf(prod_network)\
    .add_network(id="not_linked_to_any_machine",
                 type="slash_22",
                 roles=["my_subnet"],
                 site="rennes")\
    .add_machine(roles=["control"],
                 cluster="parapluie",
                 nodes=1,
                 primary_network=prod_network)\
    .add_machine(roles=["compute"],
                 cluster="parasilo",
                 nodes=1,
                 primary_network=prod_network)\
    .finalize()

provider = G5k(conf)
roles, networks = provider.init()

# Retrieving subnet
subnet = [n for n in networks if "my_subnet" in n["roles"]]
logging.info(subnet)
# This returns the subnet information
# {
#    'roles': ['my_subnet'],
#    'start': '10.158.0.1',
#    'dns': '131.254.203.235',
#    'end': '10.158.3.254',
#    'cidr': '10.158.0.0/22',
#    'gateway': '10.159.255.254'
#    'mac_end': '00:16:3E:9E:03:FE',
#    'mac_start': '00:16:3E:9E:00:01',
# }

# We describe the VMs types and placement in the following
virt_conf = vmconf.Configuration.from_settings()
virt_conf.add_machine(roles=["vmcontrol"],
                      number=1,
                      undercloud=roles["control"])\
         .add_machine(roles=["vmcompute"],
                     number=3,
                     undercloud=roles["compute"])\
         .finalize()

# Start them
vmroles, networks =start_virtualmachines(virt_conf, subnet[0])
print(vmroles)
print(networks)
