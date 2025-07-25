import sys
import json
from modules.ipv6_subnet_calculator_functions import * 

#retrieve inputs from web app
ip_address = expand_ipv6_address(sys.argv[1]) #Convert IP to list
prefix = int(sys.argv[2].replace("/", ""))  #remove slash

#perform subnet calculations
decimal_address = convert_hexadecimal_to_decimal(ip_address)
binary_address = convert_decimal_to_binary(decimal_address)

prefix_conversion = ipv6_prefix_to_subnet_mask(prefix)
decimal_prefix = convert_hexadecimal_to_decimal(prefix_conversion)
binary_prefix = convert_decimal_to_binary(decimal_prefix)

bitwised = bitwise_and_decimals(decimal_address, decimal_prefix)
network_hexadecimal = convert_decimal_to_hexadecimal(bitwised)

ipv6_network_start = ip_address[:3]
ipv6_network = ipv6_network_start + network_hexadecimal
start_address, end_address = calculate_ipv6_range(ipv6_network, prefix)
total_assignable_addresses = get_total_assignable_ip_addresses(prefix)



subnet_info = {
	"IP Address": ":".join(ip_address),
	"Network": ":".join(ipv6_network),
	"Address Range Start": ":".join(start_address),
	"Address Range End": ":".join(end_address),
	"Total Hosts": total_assignable_addresses
}
print(json.dumps(subnet_info))