def identify_ip_class(ip_address: list) -> str:
	"""
	Returns a string representation of the Class type of the given IP Address.

	Args:
		ip_address (list): An IP address indexed by "." splits.

	Returns:
		Class (str): The class of the IP address parameter.
	"""
	first_octet = ip_address[0]  #get the first octet

	if 1 <= first_octet <= 126:
		return "Class A"
	elif 128 <= first_octet <= 191:
		return "Class B"
	elif 192 <= first_octet <= 223:
		return "Class C"
	elif 224 <= first_octet <= 239:
		return "Class D (Multicast)"
	elif 240 <= first_octet <= 255:
		return "Class E (Experimental)"
	else:
		return "Invalid IP Address"


def convert_decimal_address_to_binary(address: list) -> list:
	"""
	Returns the binary coversion of a given list of decimal values.

	Args:
		address (list): A list of decimal values.

	Returns:
		binary_address (list): A list of binary values that represent the coverted decimal values.
	"""
	binary_address = []
	for i in address:
		i = bin(i)[2:].zfill(8)
		binary_address.append(i)
	return binary_address

def network_anding_bitwise_process(binary_ip: list, binary_mask: list) -> list:
	"""
	Uses a bitwise and operation and 8-bit binary conversion to
	return a bitwised address as a list of a binary ip address,
	and a binary subnet mask.

	Args:
		binary_ip (list): A list of binary values representing an IP address.
		binary_mask (list): A list of binary values representing a Subnet mask.

	Returns:
		bitwised_address (list): A bitwised list representing an IP address
		and subnet mask.
	"""
	bitwised_address = []
	for i, j in zip(binary_ip, binary_mask):  
		int_ip = int(i, 2)  #convert binary string to integer
		int_mask = int(j, 2) 

		bitwise_and = int_ip & int_mask  #bitwise AND
		binary_result = format(bitwise_and, '08b')  #convert back to 8-bit binary string

		bitwised_address.append(binary_result)

	return bitwised_address

def bitwise_and_to_decimal(bitwised_value: list) -> list:
	"""
	Uses a bitwise and operation and 8-bit binary conversion to
	return a bitwised address as a list of a binary ip address,
	and a binary subnet mask.

	Args:
		binary_ip (list): A list of binary values representing an IP address.
		binary_mask (list): A list of binary values representing a Subnet mask.

	Returns:
		bitwised_address (list): A bitwised list representing an IP address
		and subnet mask.
	"""
	binary_address = []
	for i in bitwised_value:
		i = int(i,2)
		binary_address.append(i)
	return binary_address


def calculate_broadcast_address(network_address: list, subnet_mask: list) -> list:
	"""
	Iterates through and inverts a subnet mask, and iterates through
	the values of a bitwised network_address to calculate the broadcast address
	i.e the last available host.

	Args:
		binary_ip (list): A list of binary values representing an IP address.
		binary_mask (list): A list of binary values representing a Subnet mask.

	Returns:
		bitwised_address (list): A bitwised list representing an IP address
		and subnet mask.
	"""
	inverted_mask = []
	broadcast_address = []
	for i in subnet_mask:
		i = 255 - i
		inverted_mask.append(i)
	
	for i, j in zip(network_address, inverted_mask):
		value = i | j
		broadcast_address.append(value)
	return broadcast_address

def calculate_usable_ips(network_address: list, broadcast_address: list) -> list:
	"""
	Takes a given network and broadcast address and calculates the first and last
	usable IP addresses.

	Args:
		network_address (list): A bitwised network address.
		broadcast_address (list): A bitwised broadcast address.

	Returns:
		first_ip, last_ip (list): The first usable IP, The last usable IP. 
	"""
	first_ip = network_address[:-1] + [network_address[-1] + 1]  # increment last byte
	last_ip = broadcast_address[:-1] + [broadcast_address[-1] - 1]  # decrement last byte
	return first_ip, last_ip

def total_hosts(subnet_mask: list) -> int:
	"""
	Takes a given subnet mask as a list and calculates the
	total host count of the address.

	Args:
		network_address (list): A bitwised network address.
		broadcast_address (list): A bitwised broadcast address.

	Returns:
		first_ip, last_ip (list): The first usable IP, The last usable IP. 
	"""
	host_bits = 0  # initialize a variable to store the number of host bits
	
	# iterate through each octet in the subnet mask
	for value in subnet_mask:
		binary_representation = bin(value)  #convert the decimal value to binary
		ones_count = binary_representation.count('1')  #count the number of "1" bits
		host_bits += ones_count  #the total count of network bits
	
	total_bits = 32  # IP addresses have 32 bits in total!
	host_bits = total_bits - host_bits  # calculate the number of host bits

	#calculate the total number of hosts using (2^host_bits)
	#subtract 2 (one for the network address, one for the broadcast address)
	total_host_count = (2 ** host_bits) - 2

	return total_host_count

def calculate_cidr(subnet_mask: list) -> str:
	"""
	Calculates the CIDR notation for a given subnet mask.

	Args:
		subnet_mask (list): A list of integers representing the subnet mask

	Returns:
		cidr_notation (str): The CIDR notation as a string, formatted as "/<number_of_network_bits>".
	"""
	cidr_count = 0  # Initialize a counter for the number of network bits

	# Iterate through each octet in the subnet mask
	for value in subnet_mask:
		binary_representation = bin(value)  # Convert the decimal value to binary
		ones_count = binary_representation.count('1')  # Count the number of '1' bits
		cidr_count += ones_count  # Accumulate the count of network bits
	
	# Format the CIDR notation as "/<number_of_network_bits>"
	cidr_notation = f'/{cidr_count}'

	return cidr_notation  # Return the CIDR notation


def to_dotted_decimal(ip_list):
	"""
    Converts a list of integers into a dotted-decimal IP address format.

    Args:
        ip_list (list): A list of integers representing the octets of an IP address.

    Returns:
        str: The IP address in dotted-decimal format.

    """
	return ".".join(str(octet) for octet in ip_list)
