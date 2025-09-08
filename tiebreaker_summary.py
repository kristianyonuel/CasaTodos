#!/usr/bin/env python3
"""
CASA TODOS - MONDAY NIGHT TIEBREAKER SUMMARY
Clear summary of winning conditions for each tied player
"""

def print_summary():
    print("🏈 LA CASA DE TODOS - WEEK 1 MONDAY NIGHT TIEBREAKER")
    print("=" * 80)
    
    print("\n👥 TIED LEADERS (12 correct picks):")
    print("🏆 COYOTE   - Picked MIN to win, predicted MIN 21 - CHI 27")
    print("🏆 RAMFIS   - Picked CHI to win, predicted MIN 19 - CHI 22")
    print("🏆 RAYMOND  - Picked MIN to win, predicted MIN 21 - CHI 25")
    print("🏆 VIZCA    - Picked MIN to win, predicted MIN 17 - CHI 24")
    
    print("\n📋 TIEBREAKER RULES:")
    print("1️⃣  Only players who picked the WINNING TEAM can win the week")
    print("2️⃣  Among eligible players, closest to actual scores wins")
    print("3️⃣  Tiebreaker order: Home score ± > Away score ± > Total ±")
    
    print("\n🎯 WINNING CONDITIONS FOR EACH PLAYER:")
    print("=" * 60)
    
    print("\n🏆 RAMFIS WINS IF:")
    print("   ✅ Chicago beats Minnesota (ANY score)")
    print("   📊 Optimal result: MIN 19 - CHI 22 (his exact prediction)")
    print("   📈 Probability: ~50% (wins any CHI victory)")
    print("   💪 ADVANTAGE: Only CHI picker among tied leaders!")
    
    print("\n🏆 COYOTE WINS IF:")
    print("   ✅ Minnesota beats Chicago")
    print("   📊 AND actual score is close to MIN 21 - CHI 27")
    print("   🎯 Best case: MIN 21 - CHI anything close to 27")
    print("   📈 Probability: ~10% (needs MIN win + specific scores)")
    
    print("\n🏆 RAYMOND WINS IF:")
    print("   ✅ Minnesota beats Chicago")
    print("   📊 AND actual score is close to MIN 21 - CHI 25")
    print("   🎯 Best case: MIN 21 - CHI anything close to 25")
    print("   📈 Probability: ~2% (needs MIN win + very specific scores)")
    
    print("\n🏆 VIZCA WINS IF:")
    print("   ✅ Minnesota beats Chicago")
    print("   📊 AND actual score is close to MIN 17 - CHI 24")
    print("   🎯 Best case: Low-scoring MIN win (his specialty)")
    print("   📈 Probability: ~38% (wins most MIN victory scenarios)")
    
    print("\n🔥 KEY INSIGHTS:")
    print("=" * 40)
    print("💡 RAMFIS has HUGE advantage - wins any CHI victory")
    print("💡 VIZCA wins most MIN victory scenarios (low predictions)")
    print("💡 COYOTE needs high-scoring MIN win")
    print("💡 RAYMOND has smallest winning window")
    
    print("\n📊 REALISTIC SCENARIOS:")
    print("🏈 If MIN 20 - CHI 18: VIZCA wins")
    print("🏈 If MIN 24 - CHI 22: VIZCA wins")
    print("🏈 If MIN 21 - CHI 27: COYOTE wins (but CHI wins, so RAMFIS wins!)")
    print("🏈 If MIN 19 - CHI 22: RAMFIS wins")
    print("🏈 If MIN 17 - CHI 20: VIZCA wins")
    
    print("\n🎮 BOTTOM LINE:")
    print("🏆 RAMFIS: 'I just need Chicago to win!'")
    print("🏆 VIZCA: 'I need a low-scoring Minnesota win'")
    print("🏆 COYOTE: 'I need a high-scoring Minnesota win'")
    print("🏆 RAYMOND: 'I need a very specific Minnesota win'")

if __name__ == "__main__":
    print_summary()
