#!/usr/bin/env python3
"""
Update Week 1 results with corrected tiebreaker logic
"""

from scoring_updater import ScoringUpdater

def update_week1_results():
    updater = ScoringUpdater()
    print('Updating Week 1 results with corrected tiebreaker logic...')
    
    success = updater.update_weekly_results(1, 2025)
    if success:
        print('✅ Week 1 results updated successfully!')
        
        # Show the updated results
        results = updater.get_week_winners(1, 2025)
        print(f'\n=== UPDATED WEEK 1 RESULTS (Top 5) ===')
        for i, result in enumerate(results[:5], 1):
            mnf = result['monday_tiebreaker']
            print(f'{i}. {result["username"]}: {result["correct_picks"]} correct')
            if mnf.get('correct_winner') is not None:
                correct_str = "✅" if mnf["correct_winner"] else "❌"
                print(f'   MNF: {correct_str} Winner, Home±{mnf["home_diff"]}, Away±{mnf["away_diff"]}, Total±{mnf["total_diff"]}')
    else:
        print('❌ Failed to update Week 1 results')

if __name__ == "__main__":
    update_week1_results()
