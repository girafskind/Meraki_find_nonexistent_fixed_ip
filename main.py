import csv
import meraki
from datetime import datetime, timedelta
from config import API_KEY
from device_class import FixedIP


# Initialize Meraki Dashboard object
def initialize_dashboard(api_key: str) -> meraki.DashboardAPI:
    """
    Initialize Meraki Dashboard object
    :param api_key: API key for authorizing access
    :return: A Meraki dashboard object
    """
    dashboard = meraki.DashboardAPI(api_key, suppress_logging=True)

    return dashboard


# Gather list of DHCP reservations
def get_dhcp_reservations(dashboard: meraki.DashboardAPI, net_id: str, org_tuple: tuple):
    """
    Return list of all DHCP reservations
    :param dashboard: Meraki Dashboard object
    :param net_id: Network ID to look into
    :param org_tuple: Organization ID and name
    :return: List of dicts containing every DHCP reservation
    """

    org_id = org_tuple[0]
    org_name = org_tuple[1]

    fixed_ip_object_list = []
    try:
        appliance_vlans = dashboard.appliance.getNetworkApplianceVlans(net_id)
        fixed_ips = {}
        for vlan in appliance_vlans:
            if vlan['fixedIpAssignments']:
                fixed_ips.update(vlan['fixedIpAssignments'])
                for fix_ip in vlan['fixedIpAssignments']:
                    fixed_ip_object_list.append(FixedIP(fix_ip,
                                                        vlan['fixedIpAssignments'][fix_ip]['ip'],
                                                        vlan['fixedIpAssignments'][fix_ip]['name'],
                                                        net_id, vlan['id'],
                                                        org_id, org_name))

    except meraki.APIError as e:
        print(e.message)

    return fixed_ip_object_list


# Find all clients that have not been seen for X number of days
def get_clients_older_than(dashboard: meraki.DashboardAPI, net_id: str, fixed_clients: list, older_than_days=30):
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
            network_client = dashboard.networks.getNetworkClient(net_id, fixed_client.mac)
        except meraki.APIError:
            fixed_client.dead()
            clients_not_older_than_arg.append(fixed_client)
            continue
        time_string = network_client['lastSeen']
        last_seen = datetime.utcfromtimestamp(time_string)
        time_since = datetime.now() - last_seen
        if time_since > timedelta(days=older_than_days):
            clients_not_older_than_arg.append(fixed_client)
            fixed_client.dead()
        else:
            clients_still_alive.append(fixed_client)
            fixed_client.alive()
    return clients_not_older_than_arg, clients_still_alive


def chose_org(dashboard: meraki.DashboardAPI) -> tuple:
    """
    Function that gets all organizations the API-key has access to, and user chooses one organization
    :param dashboard: Meraki dashboard object
    :return: String with organization ID
    """
    list_of_orgs = dashboard.organizations.getOrganizations()

    print("Following organizations is available for API-key")
    for i, organization in enumerate(list_of_orgs):
        print(i, organization['name'])
    org_index = int(input("Which organization to trawl for fixed IPs?"))

    return list_of_orgs[org_index]['id'], list_of_orgs[org_index]['name']


def chose_network(dashboard: meraki.DashboardAPI, org_id: tuple) -> list:
    """
    Function that gets all network the within an organization, and returns them as a list
    :param dashboard: Meraki dashboard object
    :param org_id: Organization ID
    :return: String with organization ID
    :param dashboard:
    :return:
    """
    list_of_networks = dashboard.organizations.getOrganizationNetworks(org_id[0])
    print("Following networks is available for {}:".format(org_id))
    for i, network in enumerate(list_of_networks):
        print("#", i, network['name'])
    chosen_network = input("Chose network # to trawl for fixed IPs or 'all' :")

    if chosen_network == "all":
        return list_of_networks
    else:
        return [list_of_networks[int(chosen_network)]]


def write_to_csv(objects: list):
    """
    Write list of fixed IP objects to a CSV-file
    :param objects: List of fixed IP objects
    :return: None
    """
    with open("output.csv", 'w') as csvfile:
        fields = ['Alive', 'MAC', 'IP', 'Hostname', 'Network ID', 'Organization Name', 'Organization ID', 'VLAN ID']
        writer = csv.writer(csvfile)
        writer.writerow(fields)
        for fixip_object in objects:
            writer.writerow(fixip_object.print())


def main():
    # We initialize the dashboard
    dashboard = initialize_dashboard(API_KEY)
    # Menu for choosing an organization
    chosen_org = chose_org(dashboard)
    # Menu for choosing the network
    chosen_network = chose_network(dashboard, chosen_org)
    # Global fixed_clients
    all_fixed_clients = []
    # We gather a list of fixed IP assignments
    for network in chosen_network:
        print("Trawling network", network['name'], "for fixed IP")
        # Gather all fixed IPs from current network and create list of objects
        fixed_clients = get_dhcp_reservations(dashboard, network['id'], chosen_org)
        # We pass the list of fixed IP objects to this function to find which of these have not been seen
        get_clients_older_than(dashboard, network['id'], fixed_clients)
        # Add the list of fixed clients to global list
        all_fixed_clients.extend(fixed_clients)

    write_to_csv(all_fixed_clients)


if __name__ == "__main__":
    main()
