class FixedIP:
    alive = True

    def __init__(self, mac_address, network_id, vlan_id, org_id):
        self.mac = mac_address
        self.network_id = network_id
        self.vlan_id = vlan_id
        self.org_id = org_id

    def alive(self):
        self.alive = True

    def dead(self):
        self.alive = False

    def status(self):
        return self.alive
