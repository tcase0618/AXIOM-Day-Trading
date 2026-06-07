from datetime import datetime

print("="*80)
print("DATA TIME RANGE ANALYSIS")
print("="*80)
print("")

# First and last timestamps from the 300-bar dataset
first_ts = 1780599600
last_ts = 1780692900

first_dt = datetime.utcfromtimestamp(first_ts)
last_dt = datetime.utcfromtimestamp(last_ts)

# Convert to ET (EDT = UTC - 4)
first_et_hour = first_dt.hour - 4
first_et_min = first_dt.minute
last_et_hour = last_dt.hour - 4
last_et_min = last_dt.minute

if first_et_hour < 0:
    first_et_hour += 24
if last_et_hour < 0:
    last_et_hour += 24

print("FIRST BAR:")
print(f"  UTC: {first_dt.isoformat()}")
print(f"  ET:  {first_et_hour}:{str(first_et_min).zfill(2)}")
print("")

print("LAST BAR:")
print(f"  UTC: {last_dt.isoformat()}")
print(f"  ET:  {last_et_hour}:{str(last_et_min).zfill(2)}")
print("")

print("="*80)
print("PROBLEM IDENTIFIED:")
print("="*80)
print("")
print("US Open ORB triggers at: 9:30 AM ET = 13:30 UTC")
print("Current data range:      19:00 UTC to 17:35 UTC next day")
print("Current data times:      3:00 PM ET to 1:35 PM ET next day")
print("")
print("Result: NO market open data in the dataset!")
print("The strategy can't trigger ORB entries if 9:30 AM data is missing.")
print("")

print("="*80)
print("SOLUTION:")
print("="*80)
print("")
print("Pull data that INCLUDES the 9:30 AM ET market open.")
print("That means including bars from 13:30 UTC onwards each day.")
print("")
print("With 300 bars of 5-min data starting at 19:00 UTC:")
print("- 300 bars * 5 min = 1500 minutes = 25 hours")
print("- Ends at 19:00 UTC + 25 hours = 20:00 UTC next day")
print("- This is afternoon of next day, still missing the morning open")
print("")
print("Need to request data from earlier in the morning.")
print("Or request MORE bars that go back further.")
