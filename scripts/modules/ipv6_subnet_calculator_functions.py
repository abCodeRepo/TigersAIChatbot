def expand_ipv6_address(shortened_address):
	"""
    Expands a shortened IPv6 address into its full representation.

    Args:
        shortened_address (str): The abbreviated IPv6 address with "::" or missing zeroes.

    Returns:
        expanded_segments (list): A list of strings representing the full IPv6 address, with each segment padded to 4 characters.
    """
	# Split the address into segments
	segments = shortened_address.split(":")
	
	#count missing segments (due to "::")
	missing_segments = 8 - len([segment for segment in segments if segment != ""])
	
	#replace "::" with the required number of "0"
	expanded_segments = []
	for segment in segments:
		if segment == "":
			# onsert the missing segments where "::" was
			expanded_segments.extend(["0000"] * missing_segments)
			missing_segments = 0
		else:
			# pad each segment with leading zeros to ensure it has 4 characters
			expanded_segments.append(segment.zfill(4))
	
	return expanded_segments


def convert_hexadecimal_to_decimal(hexadecimal_list):
	"""
    Converts an IPv6 address represented in hexadecimal format to decimal.

    Args:
        hexadecimal_list (list): A list of hexadecimal strings representing the IPv6 address.

    Returns:
        decimal_address (list): A list of integers representing the IPv6 address in decimal format.

    """
	decimal_address = []
	for i in hexadecimal_list:
		i = int(i,16)
		decimal_address.append(i)
	return decimal_address

def convert_decimal_to_binary(address: list) -> list:
	"""
    Converts an IPv6 address from decimal format to binary.

    Args:
        address (list): A list of integers representing the IPv6 address in decimal format.

    Returns:
        binary_adress (list): A list of binary strings, each representing a 16-bit segment of the IPv6 address.

    """
	binary_address = []
	for i in address:
		i = bin(i)[2:].zfill(16)
		binary_address.append(i)
	return binary_address

def convert_decimal_to_hexadecimal(decimal_list) -> list:
	"""
    Converts an IPv6 address from decimal format to hexadecimal.

    Args:
        decimal_list (list): A list of integers representing the IPv6 address in decimal format.

    Returns:
        hexadecimal_address (list): A list of hexadecimal strings, each representing a 4-character segment.
    """
	hexadecimal_address = []
	for i in decimal_list:
		hex_value = hex(i)[2:]
		hex_value = hex_value.zfill(4)
		hexadecimal_address.append(hex_value)
	return hexadecimal_address

def ipv6_prefix_to_subnet_mask(prefix):
	"""
    Converts an IPv6 prefix length into a subnet mask in hexadecimal format.

    Args:
        prefix (int): The prefix length, representing the number of network bits.

    Returns:
        hex_segments (list): A list of hexadecimal strings representing the IPv6 subnet mask.
    """
	# Create a binary string of prefix 1s
	binary_ones = ''
	for _ in range(prefix):
		binary_ones += '1'
	
	# add remaining (128 - prefix) 0s to complete the 128-bit binary string
	binary_zeros = ''
	for _ in range(128 - prefix):
		binary_zeros += '0'
	
	binary_mask = binary_ones + binary_zeros
	
	#split the binary string into 16-bit segments
	binary_segments = []
	for i in range(0, 128, 16):
		segment = binary_mask[i:i + 16]
		binary_segments.append(segment)
	
	# convert each 16-bit segment to hexadecimal
	hex_segments = []
	for segment in binary_segments:
		hex_value = hex(int(segment, 2))[2:]  
		hex_value = hex_value.zfill(4)     
		hex_segments.append(hex_value)
	
	return hex_segments


def bitwise_and_decimals(decimal_list1, decimal_list2):
	"""
    Performs a bitwise AND operation on two lists of decimal values, returning the network address.

    Args:
        decimal_list1 (list): A list of decimal integers representing an IPv6 address.
        decimal_list2 (list): A list of decimal integers representing a subnet mask.

    Returns:
        bitwised_address (list): A list of decimal integers representing the resulting network address.
    """
	bitwised_address = []
	for i, j in zip(decimal_list1[3:], decimal_list2[3:]):  
		bitwise_and = i & j  #bitwise AND

		bitwised_address.append(bitwise_and)

	return bitwised_address


def calculate_ipv6_range(ipv6_network, prefix):
	"""
    Calculates the start and end address range for a given IPv6 network.

    Args:
        ipv6_network (list): A list of hexadecimal strings representing the IPv6 network address.
        prefix (int): The network prefix length.

    Returns:
        tuple: Two lists representing the start and end IPv6 addresses in hexadecimal format.

    """
	# convert the network hexadecimal address to binary
	binary_network = []
	for segment in ipv6_network:
		binary_segment = bin(int(segment, 16))[2:].zfill(16)
		binary_network.append(binary_segment)
	
	# join all segments into a single binary string
	binary_network_string = ''.join(binary_network)
	
	#calculate the number of host bits (128 - prefix length)
	host_bits = 128 - prefix
	
	# Start address: Binary string remains unchanged for the network portion
	binary_start = binary_network_string[:prefix] + '0' * host_bits  # Pad host bits with 0
	
	# end adress: Host bits are set to 1
	binary_end = binary_network_string[:prefix] + '1' * host_bits  # Pad host bits with 1
	
	# convert binary start and end addresses back to hexadecimal segments
	start_address = []
	end_address = []
	for i in range(0, 128, 16):
		start_segment = hex(int(binary_start[i:i + 16], 2))[2:].zfill(4)
		end_segment = hex(int(binary_end[i:i + 16], 2))[2:].zfill(4)
		start_address.append(start_segment)
		end_address.append(end_segment)
	
	return start_address, end_address

def get_total_assignable_ip_addresses(prefix):
	"""
    Calculates the total number of assignable IPv6 addresses in a subnet based on the prefix length.

    Args:
        prefix (int): The subnet prefix length.

    Returns:
        formatted_total_addresses (str): A formatted string representing the total number of assignable IP addresses.
    """
	total_addresses = 2**(128-prefix)
	formatted_total_addresses = f'{total_addresses:,}'
	return formatted_total_addresses

