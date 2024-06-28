class FixedIP:
    alive = None

    def __init__(self, mac_address, ip_address, hostname, network_id, vlan_id, org_id, org_name):
        self.mac = mac_address
        self.ip_addr = ip_address
        self.hostname = hostname
        self.network_id = network_id
        self.vlan_id = vlan_id
        self.org_id = org_id
        self.org_name = org_name

    def alive(self):
        self.alive = True

    def dead(self):
        self.alive = False

    def status(self):
        return self.alive

    def print(self):
        return [self.alive,
                self.mac,
                self.ip_addr,
                self.hostname,
                self.network_id,
                self.org_name,
                self.org_id,
                self.vlan_id]
