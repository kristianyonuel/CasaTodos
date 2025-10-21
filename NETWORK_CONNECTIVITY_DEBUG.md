# Network Connectivity Investigation

## Issue: casadetodos.eastus.cloudapp.azure.com ERR_TIMED_OUT

The app is running on the server but not accessible from the internet.
This is a network/firewall issue, not an app crash.

## Commands to Run on Server:

### 1. Check Azure Network Security Group (Firewall)
```bash
# Check if ports 80/443 are blocked by Azure firewall
curl -I http://20.157.116.145:80
curl -k -I https://20.157.116.145:443

# Test external connectivity 
curl -I http://google.com
```

### 2. Check Local Firewall (iptables/ufw)
```bash
# Check if local firewall is blocking connections
sudo ufw status
sudo iptables -L -n | grep -E "(80|443)"
```

### 3. Check Network Interface Binding
```bash
# Verify app is listening on all interfaces (0.0.0.0), not just localhost
ss -tlnp | grep -E ":80|:443"
netstat -tlnp | grep -E ":80|:443"
```

### 4. Test DNS Resolution
```bash
# Check if domain resolves correctly
nslookup casadetodos.eastus.cloudapp.azure.com
dig casadetodos.eastus.cloudapp.azure.com
```

### 5. Check Azure VM Network Settings
```bash
# Get VM network info
ip addr show
ip route show
```

### 6. Test Direct IP Access
From your local machine, try:
- http://20.157.116.145
- https://20.157.116.145

## Likely Causes:

1. **Azure NSG (Network Security Group)**: Ports 80/443 not open in Azure firewall
2. **Local Firewall**: ufw/iptables blocking incoming connections  
3. **App Binding**: Flask only listening on localhost instead of all interfaces
4. **DNS Issues**: Domain not pointing to correct IP
5. **Azure Load Balancer**: Misconfigured health probes

## Quick Fixes:

### If Azure NSG Issue:
```bash
# This needs to be done in Azure Portal:
# 1. Go to VM → Network Security Group  
# 2. Add inbound rules for ports 80 and 443
# 3. Source: Any, Destination: Any, Action: Allow
```

### If Local Firewall Issue:
```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw reload
```

### If App Binding Issue:
Check if app.py has host='0.0.0.0' (it should based on code review)

Run these commands and report back the results!