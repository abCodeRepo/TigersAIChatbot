document.addEventListener("DOMContentLoaded", () => {
	//console.log("Sidebar script loaded!"); // debugging step

	const sidebarToggler = document.querySelector('.sidebar-toggler');
	const sidebar = document.querySelector('.sidebar');

	if (sidebarToggler && sidebar) {
		sidebarToggler.addEventListener('click', () => {
			//console.log("Sidebar toggle clicked!"); // debugging step
			sidebar.classList.toggle('active'); // toggle visibility
		});
	} else {
		console.error("Sidebar elements not found!"); // log error if sidebar is missing
	}
});

//on click events
document.getElementById("btn-ipv4").addEventListener("click", () => {
	document.getElementById("ipv4-container").style.display = "block";
	document.getElementById("ipv6-container").style.display = "none";
	document.getElementById("btn-ipv4").classList.add("active");
	document.getElementById("btn-ipv6").classList.remove("active");
});

document.getElementById("btn-ipv6").addEventListener("click", () => {
	document.getElementById("ipv4-container").style.display = "none";
	document.getElementById("ipv6-container").style.display = "block";
	document.getElementById("btn-ipv6").classList.add("active");
	document.getElementById("btn-ipv4").classList.remove("active");
});


//form submission and response for ipv4
document.getElementById("ipv4-form").addEventListener("submit", (event) => {
	event.preventDefault();
	clearSubnetResults();
	const ip_address = document.getElementById("ipv4-address").value;
	const subnet_mask = document.getElementById("ipv4-subnet").value;

	fetch("/calculateIPv4", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ ip_address, subnet_mask }),
	})
	.then((response) => response.json()) // convert response to JSON
	.then((data) => {
		// ensure valid JSON response from Python
		if (data.error) {
			console.error("Error:", data.error);
			alert("Error processing subnet calculation!");
			return;
		}

		// update HTML content with the received JSON values
		document.getElementById("network-type").textContent = `IPv4`;
		document.getElementById("network-address").textContent = `Network Address: ${data["Network Address"]}`;
		document.getElementById("broadcast-address").textContent = `Broadcast Address: ${data["Broadcast Address"]}`;
		document.getElementById("first-usable").textContent = `First Usable IP: ${data["First Usable IP"]}`;
		document.getElementById("last-usable").textContent = `Last Usable IP: ${data["Last Usable IP"]}`;
		document.getElementById("host-count").textContent = `Total Hosts: ${data["Total Hosts"]}`;
		document.getElementById("cidr").textContent = `CIDR Notation: ${data["CIDR Notation"]}`;
	})
	.catch((error) => {
		console.error("Fetch error:", error);
		alert("Something went wrong! Please try again.");
	});
});

//form submission and response for ipv6
document.getElementById("ipv6-form").addEventListener("submit", (event) => {
	event.preventDefault();
	clearSubnetResults();
	const ip_address = document.getElementById("ipv6-address").value;
	const subnet_mask = document.getElementById("ipv6-subnet").value;

	fetch("/calculateIPv6", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ ip_address, subnet_mask}),
	})
	.then(response => response.json())
	.then(data => {
		// ensure valid JSON response from Python
		if (data.error) {
			console.error("Error:", data.error);
			alert("Error processing subnet calculation!");
			return;
		}
		// update HTML content with the received JSON values
		document.getElementById("network-type").textContent = `IPv6`;
		document.getElementById("network-address").textContent = `Network Address: ${data["IP Address"]}`;
		document.getElementById("broadcast-address").textContent = `Broadcast Address: ${data["Network"]}`;
		document.getElementById("first-usable").textContent = `First Usable IP: ${data["Address Range Start"]}`;
		document.getElementById("last-usable").textContent = `Last Usable IP: ${data["Address Range End"]}`;
		document.getElementById("host-count").textContent = `Total Hosts: ${data["Total Hosts"]}`;
	})
	.catch((error) => {
		console.error("Fetch error:", error);
		alert("Something went wrong! Please try again.");
	});
});

//prevent overlapping of results from ipv4/ipv6
function clearSubnetResults() {
	const resultFields = ["network-type", "network-address", "broadcast-address", "first-usable", "last-usable", "host-count", "cidr"];
	resultFields.forEach(id => {
		const el = document.getElementById(id);
		if (el) el.textContent = "";
	});
}
