#!/usr/bin/env python3
"""
SYSTEM CLEANUP SCRIPT
====================

This script safely removes the 290+ temporary files cluttering the system
and causing server crashes, while preserving essential files.

Categories to remove:
- pfr_* files (replaced by robust_nfl_system.py)
- fix_* files (temporary patches)
- debug_* files (debugging scripts)
- test_* files (test scripts)
- check_* files (diagnostic scripts)
- Duplicate/backup files

This will clean up from 458 files to ~20 essential files.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


class SystemCleanup:
    """Safe system cleanup removing temporary files"""
    
    def __init__(self, workspace_dir: str = '.'):
        self.workspace_dir = Path(workspace_dir)
        self.backup_dir = Path('cleanup_backup')
        
        # Essential files to KEEP (core system)
        self.keep_files = {
            'app.py',                    # Main Flask application
            'robust_nfl_system.py',      # New consolidated score system
            'database.py',               # Database utilities
            'setup_database.py',         # Database setup
            'database_sync.py',          # Database sync utilities
            'deadline_manager.py',       # Deadline management
            'deadline_override_manager.py',  # Deadline overrides
            'weekly_winner_manager.py',  # Weekly winner logic
            'utils/',                    # Utility directory
            'templates/',                # HTML templates
            'static/',                   # CSS/JS/images
            'nfl_fantasy.db',            # Database file
            'config.py',                 # Configuration
            'requirements.txt',          # Dependencies
            'README.md',                 # Documentation
            '.git/',                     # Git repository
            '.gitignore',                # Git ignore
        }
        
        # Patterns to REMOVE (temporary files)
        self.remove_patterns = [
            'pfr_*.py',              # PFR integration files (replaced)
            'fix_*.py',              # Fix scripts
            'debug_*.py',            # Debug scripts  
            'test_*.py',             # Test scripts
            'check_*.py',            # Check scripts
            'analyze_*.py',          # Analysis scripts
            'force_*.py',            # Force fix scripts
            'patch_*.py',            # Patch scripts
            'emergency_*.py',        # Emergency fix scripts
            'investigate_*.py',      # Investigation scripts
            'update_week*.py',       # Week update scripts
            'manual_*.py',           # Manual operation scripts
            'complete_*.py',         # Completion scripts
            'working_*.py',          # Working versions
            'fixed_*.py',            # Fixed versions
            'final_*.py',            # Final versions
            '*_backup*.py',          # Backup files
            '*_copy*.py',            # Copy files
            '*_old*.py',             # Old files
            '*_temp*.py',            # Temporary files
            'background_updater*.py', # Old background systems
            'enhanced_*.py',         # Enhanced versions
            '*.log',                 # Log files (except essential)
            'update_*.json',         # Update history files
            '*monitor*.py',          # Old monitoring files
            'comprehensive_*.py',    # Comprehensive scripts
        ]

    def create_backup(self) -> bool:
        """Create backup of files before deletion"""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
                
            self.backup_dir.mkdir()
            
            print(f"📦 Creating backup in {self.backup_dir}...")
            
            # Find all files to be removed
            files_to_backup = []
            
            for pattern in self.remove_patterns:
                for file_path in self.workspace_dir.glob(pattern):
                    if file_path.is_file():
                        files_to_backup.append(file_path)
            
            # Backup files
            for file_path in files_to_backup:
                backup_path = self.backup_dir / file_path.name
                shutil.copy2(file_path, backup_path)
            
            print(f"✅ Backed up {len(files_to_backup)} files")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False

    def analyze_files(self) -> dict:
        """Analyze files in the workspace"""
        analysis = {
            'total_files': 0,
            'keep_files': 0,
            'remove_files': 0,
            'size_before': 0,
            'size_after_cleanup': 0,
            'remove_list': [],
            'keep_list': []
        }
        
        try:
            for file_path in self.workspace_dir.rglob('*.py'):
                if not file_path.is_file():
                    continue
                    
                analysis['total_files'] += 1
                file_size = file_path.stat().st_size
                analysis['size_before'] += file_size
                
                # Check if file should be kept
                keep_file = False
                
                # Check against keep list
                rel_path = file_path.relative_to(self.workspace_dir)
                for keep_pattern in self.keep_files:
                    if str(rel_path) == keep_pattern or str(rel_path).startswith(keep_pattern):
                        keep_file = True
                        break
                
                # Check against remove patterns
                if not keep_file:
                    for pattern in self.remove_patterns:
                        if file_path.match(pattern):
                            analysis['remove_files'] += 1
                            analysis['remove_list'].append(str(rel_path))
                            break
                    else:
                        # File doesn't match remove patterns, keep it
                        keep_file = True
                
                if keep_file:
                    analysis['keep_files'] += 1
                    analysis['keep_list'].append(str(rel_path))
                    analysis['size_after_cleanup'] += file_size
            
            return analysis
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return analysis

    def remove_temporary_files(self, dry_run: bool = True) -> int:
        """Remove temporary files (dry run by default)"""
        removed_count = 0
        
        try:
            for pattern in self.remove_patterns:
                for file_path in self.workspace_dir.glob(pattern):
                    if not file_path.is_file():
                        continue
                    
                    # Double-check not removing essential files
                    rel_path = file_path.relative_to(self.workspace_dir)
                    if any(str(rel_path).startswith(keep) for keep in self.keep_files):
                        print(f"⚠️  Skipping protected file: {rel_path}")
                        continue
                    
                    if dry_run:
                        print(f"[DRY RUN] Would remove: {rel_path}")
                    else:
                        file_path.unlink()
                        print(f"🗑️  Removed: {rel_path}")
                    
                    removed_count += 1
            
            return removed_count
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return 0

    def run_cleanup(self, confirm: bool = False):
        """Run the complete cleanup process"""
        print("🧹 SYSTEM CLEANUP ANALYSIS")
        print("=" * 50)
        
        # Analyze current state
        print("📊 Analyzing current files...")
        analysis = self.analyze_files()
        
        print(f"\\n📋 CLEANUP SUMMARY:")
        print(f"   Total Python files: {analysis['total_files']}")
        print(f"   Files to keep: {analysis['keep_files']}")
        print(f"   Files to remove: {analysis['remove_files']}")
        print(f"   Size reduction: {(analysis['size_before'] - analysis['size_after_cleanup']) / 1024:.1f} KB")
        
        if analysis['remove_files'] == 0:
            print("✅ No files need cleanup!")
            return
        
        print(f"\\n🗑️  FILES TO REMOVE ({analysis['remove_files']}):")
        for file_name in sorted(analysis['remove_list'])[:10]:  # Show first 10
            print(f"   {file_name}")
        if len(analysis['remove_list']) > 10:
            print(f"   ... and {len(analysis['remove_list']) - 10} more")
        
        print(f"\\n✅ ESSENTIAL FILES TO KEEP ({analysis['keep_files']}):")
        for file_name in sorted(analysis['keep_list'])[:10]:  # Show first 10
            print(f"   {file_name}")
        if len(analysis['keep_list']) > 10:
            print(f"   ... and {len(analysis['keep_list']) - 10} more")
        
        # Dry run first
        print(f"\\n🔍 DRY RUN - What would be removed:")
        self.remove_temporary_files(dry_run=True)
        
        if not confirm:
            print(f"\\n⚠️  This was a DRY RUN - no files were actually removed")
            print(f"🔧 To actually clean up, run: python cleanup_system.py --confirm")
            return
        
        # Ask for confirmation
        print(f"\\n⚠️  WARNING: This will permanently remove {analysis['remove_files']} files!")
        response = input("Continue with cleanup? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("❌ Cleanup cancelled")
            return
        
        # Create backup first
        if not self.create_backup():
            print("❌ Cannot proceed without backup")
            return
        
        # Perform actual cleanup
        print(f"\\n🧹 Performing cleanup...")
        removed = self.remove_temporary_files(dry_run=False)
        
        print(f"\\n✅ CLEANUP COMPLETE!")
        print(f"   Removed {removed} temporary files")
        print(f"   Backup created in: {self.backup_dir}")
        print(f"   System simplified from {analysis['total_files']} → {analysis['keep_files']} files")
        
        # Verify robust system works
        print(f"\\n🧪 Testing new robust system...")
        try:
            import subprocess
            result = subprocess.run(['python', 'robust_nfl_system.py', '--test'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Robust NFL system working correctly")
            else:
                print("⚠️  Robust NFL system needs testing")
        except:
            print("💡 Test robust system manually: python robust_nfl_system.py")


def main():
    """Main cleanup function"""
    import sys
    
    print("🧹 SYSTEM CLEANUP UTILITY")
    print("=" * 40)
    print("This tool removes 290+ temporary files cluttering the system")
    print("and replaces them with one robust solution.")
    print()
    
    cleanup = SystemCleanup()
    
    # Check if user wants to confirm cleanup
    confirm = '--confirm' in sys.argv
    
    cleanup.run_cleanup(confirm=confirm)


if __name__ == "__main__":
    main()