#!/usr/bin/env python3
"""
Diagnose problematic queries in the database
This will scan for any stored queries, views, triggers, or data containing 'us.total_games_won'
"""

import sqlite3
import sys

def diagnose_database_queries(db_path='nfl_fantasy.db'):
    """Find any problematic queries stored in the database"""
    print("🔍 SCANNING DATABASE FOR PROBLEMATIC QUERIES")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Check for views that might contain the problematic query
        print("\n📋 CHECKING VIEWS:")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='view'")
        views = cursor.fetchall()
        
        if views:
            for view_name, view_sql in views:
                print(f"View: {view_name}")
                if view_sql and 'us.total_games_won' in view_sql:
                    print(f"❌ PROBLEMATIC VIEW FOUND: {view_name}")
                    print(f"SQL: {view_sql}")
                elif view_sql:
                    print(f"✅ View looks okay")
                    print(f"SQL: {view_sql[:100]}...")
                print()
        else:
            print("No views found")
        
        # 2. Check for triggers
        print("\n🔧 CHECKING TRIGGERS:")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger'")
        triggers = cursor.fetchall()
        
        if triggers:
            for trigger_name, trigger_sql in triggers:
                print(f"Trigger: {trigger_name}")
                if trigger_sql and 'us.total_games_won' in trigger_sql:
                    print(f"❌ PROBLEMATIC TRIGGER FOUND: {trigger_name}")
                    print(f"SQL: {trigger_sql}")
                elif trigger_sql:
                    print(f"✅ Trigger looks okay")
                    print(f"SQL: {trigger_sql[:100]}...")
                print()
        else:
            print("No triggers found")
        
        # 3. Check all table schemas for any computed columns or constraints
        print("\n📊 CHECKING TABLE SCHEMAS:")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table_name, table_sql in tables:
            if table_sql and 'us.total_games_won' in table_sql:
                print(f"❌ PROBLEMATIC TABLE SCHEMA: {table_name}")
                print(f"SQL: {table_sql}")
            else:
                print(f"✅ {table_name}: Schema looks okay")
        
        # 4. Check for any stored procedures or functions (though SQLite doesn't have these by default)
        print("\n🔍 CHECKING FOR ANY OTHER DATABASE OBJECTS:")
        cursor.execute("SELECT type, name, sql FROM sqlite_master WHERE sql LIKE '%us.total_games_won%'")
        problematic_objects = cursor.fetchall()
        
        if problematic_objects:
            print("❌ FOUND PROBLEMATIC DATABASE OBJECTS:")
            for obj_type, obj_name, obj_sql in problematic_objects:
                print(f"Type: {obj_type}, Name: {obj_name}")
                print(f"SQL: {obj_sql}")
                print()
        else:
            print("No problematic database objects found")
        
        # 5. Check if any table data contains problematic queries
        print("\n💾 CHECKING TABLE DATA FOR STORED QUERIES:")
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [row[0] for row in cursor.fetchall()]
        
        for table_name in table_names:
            try:
                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                text_columns = [col[1] for col in columns if col[2] in ('TEXT', 'VARCHAR', 'CHAR')]
                
                if text_columns:
                    # Check each text column for problematic queries
                    for col in text_columns:
                        cursor.execute(f"SELECT rowid, {col} FROM {table_name} WHERE {col} LIKE '%us.total_games_won%'")
                        problematic_rows = cursor.fetchall()
                        
                        if problematic_rows:
                            print(f"❌ FOUND PROBLEMATIC DATA in {table_name}.{col}:")
                            for rowid, data in problematic_rows:
                                print(f"  Row {rowid}: {data}")
                            print()
                            
            except Exception as e:
                print(f"⚠️ Error checking table {table_name}: {e}")
        
        # 6. Show a complete dump of sqlite_master for manual inspection
        print("\n📋 COMPLETE sqlite_master DUMP:")
        cursor.execute("SELECT * FROM sqlite_master")
        master_rows = cursor.fetchall()
        
        for row in master_rows:
            obj_type, name, tbl_name, rootpage, sql = row
            print(f"Type: {obj_type}, Name: {name}, Table: {tbl_name}")
            if sql:
                if 'total_games_won' in sql:
                    print(f"  ⚠️  SQL contains 'total_games_won': {sql}")
                else:
                    print(f"  SQL: {sql[:100]}...")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error diagnosing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'nfl_fantasy.db'
    diagnose_database_queries(db_path)
