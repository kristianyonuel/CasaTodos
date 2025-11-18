from datetime import datetime

# Check Python weekday numbering
print("Python weekday() numbering:")
print("Monday =", 0)
print("Tuesday =", 1) 
print("Wednesday =", 2)
print("Thursday =", 3)
print("Friday =", 4)
print("Saturday =", 5)
print("Sunday =", 6)

print(f"\nToday is weekday: {datetime.now().weekday()}")
print(f"Today is: {datetime.now().strftime('%A')}")
