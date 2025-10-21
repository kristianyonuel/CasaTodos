#!/usr/bin/env python3
"""
Nutanix Prism Central - Citrix VDI Unused VM Analyzer
Identifies Citrix VMs that haven't been powered on or used in specified days
"""

import requests
import json
import urllib3
from datetime import datetime, timedelta
import getpass
import sys
from collections import defaultdict

# Disable SSL warnings (use with caution in production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CitrixVMAnalyzer:
    def __init__(self, pc_ip, username, password, port=9440, inactive_days=10):
        self.pc_ip = pc_ip
        self.username = username
        self.password = password
        self.port = port
        self.inactive_days = inactive_days
        self.base_url = f"https://{pc_ip}:{port}/api/nutanix/v3"
        self.base_url_v2 = f"https://{pc_ip}:{port}/PrismGateway/services/rest/v2.0"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = False
        self.session.headers.update({'Content-Type': 'application/json'})
        self.cutoff_date = datetime.now() - timedelta(days=inactive_days)
    
    def test_connection(self):
        """Test connection to Prism Central"""
        try:
            url = f"{self.base_url}/clusters/list"
            payload = {"kind": "cluster"}
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            print(f"✓ Successfully connected to Prism Central at {self.pc_ip}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to connect to Prism Central: {e}")
            return False
    
    def get_all_vms(self):
        """Retrieve all VMs from Prism Central"""
        url = f"{self.base_url}/vms/list"
        all_vms = []
        offset = 0
        length = 500
        
        print("\nFetching VM list from Prism Central...")
        
        while True:
            payload = {
                "kind": "vm",
                "offset": offset,
                "length": length
            }
            
            try:
                response = self.session.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                vms = data.get('entities', [])
                all_vms.extend(vms)
                
                total = data.get('metadata', {}).get('total_matches', 0)
                print(f"  Retrieved {len(all_vms)} of {total} VMs...")
                
                if len(all_vms) >= total:
                    break
                    
                offset += length
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching VMs: {e}")
                break
        
        print(f"✓ Total VMs retrieved: {len(all_vms)}\n")
        return all_vms
    
    def get_vm_events(self, vm_uuid):
        """Get power state change events for a VM"""
        url = f"{self.base_url}/events/list"
        
        # Calculate timestamp for lookback period (add buffer for API)
        start_time = int((self.cutoff_date - timedelta(days=5)).timestamp() * 1000000)
        
        payload = {
            "filter": f"entity_list=={vm_uuid}",
            "length": 1000
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            events = response.json().get('entities', [])
            return events
        except:
            return []
    
    def get_vm_alerts(self, vm_uuid):
        """Get alerts for a VM"""
        url = f"{self.base_url}/alerts/list"
        
        payload = {
            "filter": f"entity_list=={vm_uuid}",
            "length": 100
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            alerts = response.json().get('entities', [])
            return alerts
        except:
            return []
    
    def parse_vm_last_activity(self, vm, events):
        """Parse VM events to find last power-on activity"""
        last_power_on = None
        last_power_off = None
        power_on_count = 0
        
        for event in events:
            event_type = event.get('status', {}).get('resources', {}).get('classification', '')
            timestamp_str = event.get('status', {}).get('resources', {}).get('created_time', '')
            
            if not timestamp_str:
                continue
            
            try:
                # Parse timestamp
                event_time = datetime.strptime(timestamp_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                
                # Check for power on events
                if 'power' in event_type.lower() and 'on' in event_type.lower():
                    if not last_power_on or event_time > last_power_on:
                        last_power_on = event_time
                    power_on_count += 1
                
                # Check for power off events
                if 'power' in event_type.lower() and 'off' in event_type.lower():
                    if not last_power_off or event_time > last_power_off:
                        last_power_off = event_time
            except:
                continue
        
        return last_power_on, last_power_off, power_on_count
    
    def analyze_citrix_vm(self, vm):
        """Analyze if a Citrix VM is unused based on power-on history"""
        spec = vm.get('spec', {})
        status = vm.get('status', {})
        resources = spec.get('resources', {})
        metadata = vm.get('metadata', {})
        
        vm_name = spec.get('name', 'Unknown')
        vm_uuid = metadata.get('uuid', '')
        power_state = resources.get('power_state', 'UNKNOWN')
        creation_time_str = metadata.get('creation_time', '')
        
        # Get resource configuration
        num_sockets = resources.get('num_sockets', 0)
        num_vcpus_per_socket = resources.get('num_vcpus_per_socket', 0)
        num_vcpus = num_sockets * num_vcpus_per_socket
        memory_mb = resources.get('memory_size_mib', 0)
        
        # Parse creation time
        creation_time = None
        if creation_time_str:
            try:
                creation_time = datetime.strptime(creation_time_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
            except:
                pass
        
        # Get VM categories/tags
        categories = metadata.get('categories', {})
        
        # Get events to determine last activity
        events = self.get_vm_events(vm_uuid)
        last_power_on, last_power_off, power_on_count = self.parse_vm_last_activity(vm, events)
        
        # Calculate days since last power on
        days_since_power_on = None
        if last_power_on:
            days_since_power_on = (datetime.now() - last_power_on).days
        elif creation_time:
            # If no power on events found, use creation time
            days_since_power_on = (datetime.now() - creation_time).days
        
        # Determine if VM is unused
        is_unused = False
        unused_reasons = []
        unused_score = 0
        
        # Check power state
        if power_state == 'OFF':
            unused_reasons.append("Currently powered OFF")
            unused_score += 30
        
        # Check days since last power on
        if days_since_power_on is not None:
            if days_since_power_on >= self.inactive_days:
                unused_reasons.append(f"No power-on activity for {days_since_power_on} days")
                unused_score += 50
            elif days_since_power_on >= (self.inactive_days // 2):
                unused_reasons.append(f"Limited activity ({days_since_power_on} days since power-on)")
                unused_score += 25
        
        # Check power on frequency
        if power_on_count == 0:
            unused_reasons.append("Never powered on since tracking period")
            unused_score += 40
        elif power_on_count <= 2:
            unused_reasons.append(f"Rarely used (only {power_on_count} power-on events)")
            unused_score += 20
        
        # VM is considered unused if score >= 50 or specific critical conditions
        is_unused = (unused_score >= 50 or 
                     (power_state == 'OFF' and days_since_power_on and days_since_power_on >= self.inactive_days))
        
        # Determine VM age
        vm_age_days = None
        if creation_time:
            vm_age_days = (datetime.now() - creation_time).days
        
        return {
            'name': vm_name,
            'uuid': vm_uuid,
            'power_state': power_state,
            'vcpus': num_vcpus,
            'memory_mb': memory_mb,
            'memory_gb': round(memory_mb / 1024, 2),
            'creation_time': creation_time.isoformat() if creation_time else 'Unknown',
            'vm_age_days': vm_age_days,
            'last_power_on': last_power_on.isoformat() if last_power_on else 'Never/Unknown',
            'last_power_off': last_power_off.isoformat() if last_power_off else 'Unknown',
            'days_since_power_on': days_since_power_on,
            'power_on_count': power_on_count,
            'categories': categories,
            'is_unused': is_unused,
            'unused_score': unused_score,
            'unused_reasons': unused_reasons
        }
    
    def generate_report(self, vm_analyses):
        """Generate a detailed report of unused Citrix VMs"""
        print("\n" + "="*100)
        print(f"CITRIX VDI - UNUSED VM ANALYSIS REPORT (Inactive for {self.inactive_days}+ days)")
        print("="*100)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Analysis Period: Last {self.inactive_days} days")
        print(f"Total VMs Analyzed: {len(vm_analyses)}")
        
        # Separate used and unused VMs
        unused_vms = [vm for vm in vm_analyses if vm['is_unused']]
        used_vms = [vm for vm in vm_analyses if not vm['is_unused']]
        
        print(f"Unused/Inactive VMs: {len(unused_vms)}")
        print(f"Active VMs: {len(used_vms)}")
        print("="*100 + "\n")
        
        if unused_vms:
            print("UNUSED/INACTIVE CITRIX VIRTUAL MACHINES")
            print("-"*100)
            
            # Sort by days since power on (highest first)
            unused_vms.sort(key=lambda x: (x['days_since_power_on'] or 0), reverse=True)
            
            for i, vm in enumerate(unused_vms, 1):
                print(f"\n{i}. VM Name: {vm['name']}")
                print(f"   UUID: {vm['uuid']}")
                print(f"   Current State: {vm['power_state']}")
                print(f"   Resources: {vm['vcpus']} vCPUs, {vm['memory_gb']} GB RAM")
                print(f"   VM Age: {vm['vm_age_days']} days" if vm['vm_age_days'] else "   VM Age: Unknown")
                
                if vm['days_since_power_on'] is not None:
                    print(f"   ⚠ Days Since Last Power-On: {vm['days_since_power_on']} days")
                else:
                    print(f"   ⚠ Last Power-On: Never recorded")
                
                print(f"   Last Power-On Date: {vm['last_power_on']}")
                print(f"   Power-On Count (tracking period): {vm['power_on_count']}")
                print(f"   Unused Score: {vm['unused_score']}/100")
                
                if vm['unused_reasons']:
                    print(f"   Reasons:")
                    for reason in vm['unused_reasons']:
                        print(f"     • {reason}")
                
                if vm['categories']:
                    print(f"   Categories/Tags: {json.dumps(vm['categories'])}")
        else:
            print("✓ No unused VMs detected! All VMs show recent activity.")
        
        # Summary statistics
        print("\n" + "="*100)
        print("SUMMARY & RECOMMENDATIONS")
        print("-"*100)
        
        total_unused_vcpus = sum(vm['vcpus'] for vm in unused_vms)
        total_unused_memory = sum(vm['memory_gb'] for vm in unused_vms)
        
        # Categorize by severity
        critical_unused = [vm for vm in unused_vms if vm['days_since_power_on'] and vm['days_since_power_on'] >= 30]
        high_unused = [vm for vm in unused_vms if vm['days_since_power_on'] and 20 <= vm['days_since_power_on'] < 30]
        medium_unused = [vm for vm in unused_vms if vm['days_since_power_on'] and self.inactive_days <= vm['days_since_power_on'] < 20]
        
        print(f"\nUnused VM Breakdown:")
        print(f"  Critical (30+ days inactive): {len(critical_unused)} VMs")
        print(f"  High (20-29 days inactive): {len(high_unused)} VMs")
        print(f"  Medium ({self.inactive_days}-19 days inactive): {len(medium_unused)} VMs")
        
        print(f"\nPotentially Reclaimable Resources:")
        print(f"  vCPUs: {total_unused_vcpus}")
        print(f"  Memory: {total_unused_memory:.2f} GB")
        
        print(f"\nRecommendations:")
        if critical_unused:
            print(f"  ⚠ URGENT: {len(critical_unused)} VMs inactive for 30+ days - Consider deletion")
        if high_unused:
            print(f"  ⚠ HIGH: {len(high_unused)} VMs inactive for 20-29 days - Verify with users")
        if medium_unused:
            print(f"  • MEDIUM: {len(medium_unused)} VMs inactive for {self.inactive_days}-19 days - Monitor closely")
        
        print("="*100 + "\n")
        
        return unused_vms
    
    def export_to_json(self, vm_analyses, filename="citrix_unused_vms_report.json"):
        """Export analysis to JSON file"""
        unused_vms = [vm for vm in vm_analyses if vm['is_unused']]
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'analysis_period_days': self.inactive_days,
            'total_vms': len(vm_analyses),
            'unused_vms_count': len(unused_vms),
            'active_vms_count': len(vm_analyses) - len(unused_vms),
            'unused_vms': unused_vms,
            'active_vms': [vm for vm in vm_analyses if not vm['is_unused']],
            'summary': {
                'total_unused_vcpus': sum(vm['vcpus'] for vm in unused_vms),
                'total_unused_memory_gb': sum(vm['memory_gb'] for vm in unused_vms),
                'critical_count': len([vm for vm in unused_vms if vm['days_since_power_on'] and vm['days_since_power_on'] >= 30]),
                'high_count': len([vm for vm in unused_vms if vm['days_since_power_on'] and 20 <= vm['days_since_power_on'] < 30]),
                'medium_count': len([vm for vm in unused_vms if vm['days_since_power_on'] and self.inactive_days <= vm['days_since_power_on'] < 20])
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Report exported to {filename}")
    
    def export_to_csv(self, vm_analyses, filename="citrix_unused_vms_report.csv"):
        """Export unused VMs to CSV file"""
        import csv
        
        unused_vms = [vm for vm in vm_analyses if vm['is_unused']]
        
        if not unused_vms:
            print("No unused VMs to export.")
            return
        
        with open(filename, 'w', newline='') as f:
            fieldnames = ['name', 'uuid', 'power_state', 'vcpus', 'memory_gb', 
                         'vm_age_days', 'days_since_power_on', 'power_on_count',
                         'last_power_on', 'unused_score', 'unused_reasons']
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for vm in unused_vms:
                row = {k: vm[k] for k in fieldnames if k != 'unused_reasons'}
                row['unused_reasons'] = '; '.join(vm['unused_reasons'])
                writer.writerow(row)
        
        print(f"✓ CSV report exported to {filename}")

def main():
    print("Nutanix Prism Central - Citrix VDI Unused VM Analyzer")
    print("-"*60)
    
    # Get connection details
    pc_ip = input("Prism Central IP/FQDN: ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    
    # Get analysis parameters
    try:
        inactive_days = int(input("Days of inactivity to flag as unused [10]: ").strip() or "10")
    except ValueError:
        inactive_days = 10
    
    # Initialize analyzer
    analyzer = CitrixVMAnalyzer(pc_ip, username, password, inactive_days=inactive_days)
    
    # Test connection
    if not analyzer.test_connection():
        print("Failed to connect. Please check your credentials and try again.")
        sys.exit(1)
    
    # Get all VMs
    vms = analyzer.get_all_vms()
    
    if not vms:
        print("No VMs found or error retrieving VMs.")
        sys.exit(1)
    
    # Analyze each VM
    print(f"Analyzing Citrix VM usage patterns (looking for {inactive_days}+ days of inactivity)...")
    print("This may take a while as we retrieve event history for each VM...\n")
    
    vm_analyses = []
    
    for idx, vm in enumerate(vms, 1):
        if idx % 10 == 0:
            print(f"  Analyzed {idx}/{len(vms)} VMs...")
        analysis = analyzer.analyze_citrix_vm(vm)
        vm_analyses.append(analysis)
    
    print(f"  Completed: {len(vms)}/{len(vms)} VMs\n")
    
    # Generate report
    unused_vms = analyzer.generate_report(vm_analyses)
    
    # Export options
    if unused_vms:
        export = input("\nExport report? (json/csv/both/n): ").strip().lower()
        
        if export in ['json', 'both']:
            filename = input("JSON filename [citrix_unused_vms_report.json]: ").strip() or "citrix_unused_vms_report.json"
            analyzer.export_to_json(vm_analyses, filename)
        
        if export in ['csv', 'both']:
            filename = input("CSV filename [citrix_unused_vms_report.csv]: ").strip() or "citrix_unused_vms_report.csv"
            analyzer.export_to_csv(vm_analyses, filename)

if __name__ == "__main__":
    main()