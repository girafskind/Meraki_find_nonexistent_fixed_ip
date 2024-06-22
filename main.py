import meraki
import pprint
from datetime import datetime, timedelta

from config import API_KEY, NET_ID


# Initialize Meraki Dashboard object
def initialize_dashboard(api_key: meraki.DashboardAPI):
    """
    Initialize Meraki Dashboard object
    :param api_key: API key for authorizing access
    :return: A Meraki dashboard object
    """
    dashboard = meraki.DashboardAPI(api_key, suppress_logging=True)

    return dashboard


# Gather list of DHCP reservations
def get_dhcp_reservations(dashboard: meraki.DashboardAPI, net_id: str):
    """
    Return list of all DHCP reservations
    :param dashboard: Meraki Dashboard object
    :param net_id: Network ID to look into
    :return: List of dicts containing every DHCP reservation
    """
    appliance_vlans = dashboard.appliance.getNetworkApplianceVlans(net_id)
    fixed_ips = {}
    for vlan in appliance_vlans:
        if vlan['fixedIpAssignments']:
            fixed_ips.update(vlan['fixedIpAssignments'])

    return fixed_ips


# Find all clients that have not been seen for X number of days
def get_clients_older_than(dashboard: meraki.DashboardAPI, net_id: str, fixed_clients: dict, older_than_days=30):
    """
    Return a list of clients that have not been seen on the network for the given number of days
    :param fixed_clients: Dictionary of fixed clients
    :param dashboard: Meraki dashboard object
    :param net_id: Network ID to look into
    :param older_than_days: How many days have the client not been seen
    :return: 2 lists, clients not seen for more than given days and clients still alive
    """
    clients_not_older_than_arg = []
    clients_still_alive = []
    for fixed_client in fixed_clients:
        try:
            network_client = dashboard.networks.getNetworkClient(net_id, fixed_client)
        except meraki.APIError as e:
            clients_not_older_than_arg.append(fixed_client)
            continue
        time_string = network_client['lastSeen']
        last_seen = datetime.utcfromtimestamp(time_string)
        time_since = datetime.now() - last_seen
        if time_since > timedelta(days=older_than_days):
            clients_not_older_than_arg.append(fixed_client)
        else:
            clients_still_alive.append(fixed_client)
    return clients_not_older_than_arg, clients_still_alive


def main():
    # We initialize the dashboard
    dashboard = initialize_dashboard(API_KEY)
    # We gather a list of fixed IP assignments
    fixed_clients = get_dhcp_reservations(dashboard, NET_ID)
    # We pass the list of fixed IP assignments to this function to find which of these have not been seen
    old_fixed_clients, alive_fixed_clients = get_clients_older_than(dashboard, NET_ID, fixed_clients)

    # Then we print a list of the fixed IP list and which have not been seen
    print("Fixed clients")
    pprint.pprint(fixed_clients)
    print("Fixed clients not seen")
    pprint.pprint(old_fixed_clients)
    print("Fixed clients still alive")
    pprint.pprint(alive_fixed_clients)


if __name__ == "__main__":
    main()
