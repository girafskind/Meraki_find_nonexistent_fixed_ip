# Find non-exsistent fixed IP-addresses
This script will take all fixed IP reservations in a given network, then check if they have been online for the last 30 days.

## Files
- main.py - Main script file
- config.py - File containing API key and network ID
- device_class.py - File containing FixedIP class
- output.csv - Script will write result to this file

## Todo
- [x] Gather fixed IP from network
- [x] Check client MAC
- [ ] Delete fixed IP from network
- [x] Some kind of iteration over the organization networks
- [x] Write output to CSV file