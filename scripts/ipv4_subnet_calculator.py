import sys
import json
from modules.ipv4_subnet_calculator_functions import * 

#retrieve inputs from web app
ip_address = sys.argv[1].split(".")  #Convert IP to list
subnet_mask = sys.argv[2].split(".")  #Convert subnet to list



ip_address = [int(octet) for octet in ip_address]
subnet_mask = [int(octet) for octet in subnet_mask]

#perform subnet calculations
binary_ip_address = convert_decimal_address_to_binary(ip_address)
binary_subnet_mask = convert_decimal_address_to_binary(subnet_mask)

bitwised_result = network_anding_bitwise_process(binary_ip_address, binary_subnet_mask)
network_address = bitwise_and_to_decimal(bitwised_result)

broadcast_address = calculate_broadcast_address(network_address, subnet_mask)
first_ip, last_ip = calculate_usable_ips(network_address, broadcast_address)
host_count = total_hosts(subnet_mask)
cidr_notation = calculate_cidr(subnet_mask)

#format results as JSON string
subnet_info = {
	"Network Address": to_dotted_decimal(network_address),
	"Broadcast Address": to_dotted_decimal(broadcast_address),
	"First Usable IP": to_dotted_decimal(first_ip),
	"Last Usable IP": to_dotted_decimal(last_ip),
	"Total Hosts": host_count,
	"CIDR Notation": cidr_notation
}
print(json.dumps(subnet_info))
