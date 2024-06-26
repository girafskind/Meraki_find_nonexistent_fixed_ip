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


def chose_org(dashboard: meraki.DashboardAPI) -> str:
    """
    Function that gets all organizations the API-key has access to, and user chooses one organization
    :param dashboard: Meraki dashboard object
    :return: String with organization ID
    """
    list_of_orgs = dashboard.organizations.getOrganizations()

    print("Following organzations is available for API-key")
    for i, organization in enumerate(list_of_orgs):
        print(i, organization['name'])
    org_index = int(input("Which organization to trawl for fixed IPs?"))

    return list_of_orgs[org_index]['id']


def chose_network(dashboard:meraki.DashboardAPI, org_id: str) -> str:
    """
    Function that gets all network the within an organization, and returns them as a list
    :param dashboard: Meraki dashboard object
    :param org_id: Organization ID
    :return: String with organization ID
    :param dashboard:
    :return:
    """
    list_of_networks = dashboard.organizations.getOrganizationNetworks(org_id)
    print("Following networks is available for {}:".format(org_id))
    for i, network in enumerate(list_of_networks):
        print(i, network['name'])
    chosen_network = int(input("Which network to trawl for fixed IPs?"))

    return list_of_networks[chosen_network]['id']


def main():
    # We initialize the dashboard
    dashboard = initialize_dashboard(API_KEY)
    # Menu for choosing an organization
    chosen_org = chose_org(dashboard)
    # Menu for choosing the network
    chosen_network = chose_network(dashboard, chosen_org)
    # We gather a list of fixed IP assignments
    fixed_clients = get_dhcp_reservations(dashboard, chosen_network)
    # We pass the list of fixed IP assignments to this function to find which of these have not been seen
    old_fixed_clients, alive_fixed_clients = get_clients_older_than(dashboard, chosen_network, fixed_clients)
    # Then we print a list of the fixed IP list and which have not been seen
    print("Fixed clients")
    pprint.pprint(fixed_clients)
    print("Fixed clients not seen")
    pprint.pprint(old_fixed_clients)
    print("Fixed clients still alive")
    pprint.pprint(alive_fixed_clients)


if __name__ == "__main__":
    main()
