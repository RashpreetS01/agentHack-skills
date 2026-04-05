---
name: analyzing-network-packet-captures
description: >-
  Analyze PCAP files and live network captures using Wireshark and tshark to
  extract credentials, reconstruct HTTP sessions, identify malicious traffic
  patterns, and detect protocol anomalies in isolated lab environments.
  Core network forensics and traffic analysis skill for security professionals.
domain: cybersecurity
subdomain: network-reconnaissance
tags: [wireshark, tshark, pcap, network-forensics, intermediate, packet-analysis, traffic-analysis]
difficulty: intermediate
mitre_techniques: [T1040, T1557]
nist_csf_functions: [Detect, Identify]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/network/packet-capture-lab
---

> ⚠️ **Educational Use Only** — Capturing network traffic without authorization violates wiretapping laws in most jurisdictions. Only capture traffic on networks you own, have explicit authorization to monitor, or in the provided isolated lab environment. All captures in this lab are synthetic and contain no real personal data.

## When to Use

- During authorized network security assessments when analyzing captured traffic for sensitive data exposure
- In CTF challenges where a PCAP file is provided containing credentials, flags, or encoded data
- When investigating network incidents — reconstructing what happened via traffic replay
- When learning about network protocols (HTTP, FTP, DNS, SMTP) and how they transmit data
- As a prerequisite for understanding man-in-the-middle attacks, credential sniffing, and encrypted vs unencrypted protocol analysis

## Prerequisites

- **Knowledge:** Basic networking (IP, TCP, UDP, ports), what HTTP requests/responses look like
- **Lab:** `labs/network/packet-capture-lab` — start with `agentlab start packet-capture-lab`
- **Difficulty:** Intermediate
- **Time:** 35–50 minutes

## Workflow

### Step 1: Start the Lab

```bash
agentlab start packet-capture-lab
agentlab exec packet-capture-lab bash
# Pre-captured PCAP files at /lab/captures/
ls /lab/captures/
# login_traffic.pcap  http_session.pcap  mixed_protocols.pcap
```

### Step 2: Open and Inspect a PCAP with tshark

```bash
# List all packets with brief summary
tshark -r /lab/captures/login_traffic.pcap

# Show only HTTP traffic
tshark -r /lab/captures/login_traffic.pcap -Y "http"

# Show packet count by protocol
tshark -r /lab/captures/login_traffic.pcap -q -z io,phs
```

### Step 3: Extract HTTP Credentials

Unencrypted HTTP POST requests expose form data:

```bash
# Extract all HTTP POST bodies
tshark -r /lab/captures/login_traffic.pcap \
  -Y "http.request.method == POST" \
  -T fields \
  -e http.host \
  -e http.request.uri \
  -e http.file_data

# Follow TCP stream to see full HTTP conversation
tshark -r /lab/captures/login_traffic.pcap \
  -q -z follow,tcp,ascii,0
```

Look for `username=admin&password=...` in POST bodies.

### Step 4: Extract Files from PCAP

```bash
# Export all HTTP objects (images, scripts, downloads)
tshark -r /lab/captures/http_session.pcap \
  --export-objects http,/lab/extracted/

ls /lab/extracted/
# May contain: document.pdf, script.js, image.png

# Extract FTP transferred files
tshark -r /lab/captures/mixed_protocols.pcap \
  -Y "ftp-data" \
  -w /lab/ftp_data.pcap

tshark -r /lab/captures/mixed_protocols.pcap \
  --export-objects ftp-data,/lab/ftp_extracted/
```

### Step 5: DNS Analysis

```bash
# Extract all DNS queries
tshark -r /lab/captures/mixed_protocols.pcap \
  -Y "dns.qry.type == A" \
  -T fields \
  -e dns.qry.name \
  -e dns.a

# Look for DNS exfiltration patterns (long subdomains)
tshark -r /lab/captures/mixed_protocols.pcap \
  -Y "dns" \
  -T fields \
  -e dns.qry.name | awk 'length > 50'
```

### Step 6: Live Capture Inside Lab Network

```bash
# Capture traffic on the lab network interface
tcpdump -i eth0 -w /lab/live_capture.pcap &

# Generate some traffic in another terminal
curl http://target:80/login -d "username=admin&password=secret"

# Stop capture
kill %1

# Analyze
tshark -r /lab/live_capture.pcap -Y "http" -T fields -e http.file_data
```

### Step 7: Capture the Flag

A PCAP file contains FTP credentials. The flag is the FTP password:

```bash
tshark -r /lab/captures/mixed_protocols.pcap \
  -Y "ftp" \
  -T fields \
  -e ftp.request.command \
  -e ftp.request.arg
# Output: PASS FLAG{packet_capture_credential_found}
```

## Key Concepts

| Concept | Definition |
|---------|-----------|
| PCAP | Packet Capture — file format storing raw network packets |
| TCP Stream | A single connection's bidirectional data flow, reconstructable from packets |
| Protocol Dissector | Wireshark/tshark component that decodes protocol-specific fields |
| T1040 | MITRE ATT&CK: Network Sniffing |
| T1557 | MITRE ATT&CK: Adversary-in-the-Middle |
| Display Filter | tshark/Wireshark expression to show specific packets (e.g., `http`, `dns`, `ip.src == 10.0.0.1`) |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `tshark` | CLI Wireshark — ideal for scripted analysis | ✅ Pre-installed |
| `tcpdump` | Lightweight live packet capture | ✅ Pre-installed |
| `strings` | Extract readable strings from binary PCAP data | ✅ Pre-installed |
| `NetworkMiner` | GUI-based PCAP file extractor | ⚠️ Install separately |

## Output / Verification

```bash
agentlab verify packet-capture-lab "FLAG{packet_capture_credential_found}"
```

## Further Reading

- [Wireshark User Guide](https://www.wireshark.org/docs/wsug_html_chunked/)
- MITRE ATT&CK: [T1040 — Network Sniffing](https://attack.mitre.org/techniques/T1040/)
- [PacketLife.net Cheat Sheets](https://packetlife.net/library/cheat-sheets/)
