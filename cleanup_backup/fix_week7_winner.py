"""
Fix Week 7 winner - Raymond should win
"""
import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("=== FIXING WEEK 7 WINNER ===")
print("ANALYSIS:")
print("- Raymond: 10 correct out of 14 games = 71.4% accuracy")
print("- Ramfis: 10 correct out of 15 games = 66.7% accuracy") 
print("- Guillermo: 10 correct out of 15 games = 66.7% accuracy")
print("")
print("MNF Tiebreaker (ATL @ SF = 43 total):")
print("- Ramfis predicted 41 (diff = 2)")
print("- Raymond predicted 45 (diff = 2) - TIE!")
print("- Guillermo predicted 52 (diff = 9)")
print("")
print("WINNER: RAYMOND (higher accuracy percentage breaks the tie)")

# Update Week 7 results
cursor.execute("UPDATE weekly_results SET is_winner = 0 WHERE week = 7 AND year = 2025")

cursor.execute("""
    UPDATE weekly_results 
    SET is_winner = 1 
    WHERE week = 7 AND year = 2025 
    AND user_id = (SELECT id FROM users WHERE username = 'raymond')
""")

conn.commit()
print("\nRaymond is now marked as Week 7 winner!")

# Verify results
cursor.execute("""
    SELECT u.username, wr.correct_picks, wr.is_winner
    FROM weekly_results wr
    JOIN users u ON wr.user_id = u.id
    WHERE wr.week = 7 AND wr.year = 2025
    ORDER BY wr.correct_picks DESC, u.username
""")

results = cursor.fetchall()
print("\nUpdated Week 7 Results:")
for username, correct, is_winner in results:
    status = " (WINNER!)" if is_winner else ""
    print(f"  {username}: {correct} correct{status}")

# Check Raymond's total wins
cursor.execute("""
    SELECT COUNT(*) FROM weekly_results 
    WHERE user_id = (SELECT id FROM users WHERE username = 'raymond') 
    AND year = 2025 AND is_winner = 1
""")

raymond_total_wins = cursor.fetchone()[0]
print(f"\nRaymond's season wins: {raymond_total_wins}")

conn.close()
print("\nSUCCESS: Raymond is now correctly shown as Week 7 winner!")