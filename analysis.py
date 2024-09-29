import mysql.connector
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import scipy.stats as stats

def convert_24hr(time):
  time_object = datetime.strptime(time,'%I:%M %p').strftime('%H:%M')
  return time_object

# Connect to the database with user credentials
conn = mysql.connector.connect(
  user='aryan',
	password = '1234',
	host='localhost',
	database='aviation_data',
)


# Creating cursor object to execute SQL queries
cursor = conn.cursor()

query="""
  SELECT * FROM FlightSchedule;
"""

# Executing the SQL query and fetch all the rows into a list of tuples
cursor.execute(query)

results = []

# Fetching each row and appending it to the results list.
for i, data in enumerate(cursor):
	results.append(data)

# Closing the cursor and connection
cursor.close()
conn.close()

# Creating a pandas DataFrame from the results list of tuples
df = pd.DataFrame(results, columns=['FlightNumber', 'DepartureDate', 'DepartureTime','ArrivalDate', 'ArrivalTime', 'Airline', 'DelayMinutes'])

print(df)
#Saving the progress with a csv file
df.to_csv('flight_schedule-1.csv', index=False)

# Checking for missing values and filling them with the mean of DelayMinutes
print(df.isna().sum())

df.fillna(df['DelayMinutes'].mean(),inplace=True)
print(df.isna().sum())
print(df)

# Converting to Date
df['DepartureDate']=pd.to_datetime(df['DepartureDate'],format="%m/%d/%Y")
df['ArrivalDate']=pd.to_datetime(df['ArrivalDate'],format="%m/%d/%Y")
# print(">\n",df.dtypes)
# print(df.info())


# Converting to Time
df['DepartureTime'] = df['DepartureTime'].apply(convert_24hr)
df['ArrivalTime'] = df['ArrivalTime'].apply(convert_24hr)

print(df)

duplicate_entries = df[df.duplicated(keep=False)]
print("\nDuplicate Entries:\n",duplicate_entries)
print()

for index,row in df.iterrows():
  if row['DepartureDate']==row['ArrivalDate']: # If the departure and arrival dates are same
    if row['ArrivalTime'] > row['DepartureTime']: # If the arrival time is greater than depature time i.e, the plane departs before it lands (ERROR)
      # Swap the departure and arrival time for that index
      temp=row['DepartureTime']
      df.at[index, 'DepartureTime'] = row['ArrivalTime']
      df.at[index, 'ArrivalTime'] = temp
  elif row['DepartureDate'] < row['ArrivalDate']: # If the depature date is less than arrival
    # Swap the departure and arrival date for that index
    temp=row['ArrivalDate']
    df.at[index, 'ArrivalDate'] = row['DepartureDate']
    df.at[index, 'DepartureDate'] = temp

for index,row in df.iterrows():
  # For the same date, duration of the flight is (24 hours - (departure time of the flight - arrival time)) of the flight, since departure time is greater than arrival time
  if row['DepartureDate'] == row['ArrivalDate']:
    departure_seconds = pd.to_timedelta(row['DepartureTime']+":00").total_seconds()
    arrival_seconds = pd.to_timedelta(row['ArrivalTime']+":00").total_seconds()

    # Storing the data in a new column
    df.at[index, 'FlightDuration(in Hrs)'] = round(((86400-(departure_seconds - arrival_seconds)) / 3600),2)
  else:
    # For the flights not in the same day, duration of the flight is (48 hours - (24 hours - arrival time) + the departure time of the next day)
    arrival_seconds= (pd.Timedelta('1 day')-pd.to_timedelta(row['ArrivalTime']+":00")).total_seconds()
    departure_seconds = pd.to_timedelta(row['DepartureTime']+":00").total_seconds()

    # Storing the data in a new column
    df.at[index, 'FlightDuration(in Hrs)'] = round(((172800-(departure_seconds + arrival_seconds)) / 3600),2)

print(df)

# Analyzing the distribution of delays and identify any trends or patterns.
print()
print(df['DelayMinutes'].describe()) # provides the 5 central tendency values for DelayMinutes

#Saving the progress with a csv file
df.to_csv('flight_schedule-2.csv', index=False)

# Calculate the average delay time per airline
print()
print("Delay time per airline: \n")
print(df.groupby('Airline')['DelayMinutes'].sum())
print()
print("Average delay time per airline: \n")
print(df.groupby('Airline')['DelayMinutes'].mean())

#Distribution of delays (visually)
plt.hist(df['DelayMinutes'])
plt.title('Delay Minutes Distribution')
plt.xlabel('Delay Minutes')
plt.ylabel('Frequency')
plt.savefig("DelayDist-Freq.png")
plt.close()

# Plotting flight delays for departure time
df.sort_values(by='DepartureTime', inplace=True)
print(df)

colors = plt.cm.viridis(np.linspace(0, 1, df['FlightNumber'].nunique()))

plt.figure(figsize=(10, 6))
for index,flight_number in enumerate(df['FlightNumber'].unique()):
    # subset = df[df['FlightNumber'] == flight_number]
    plt.plot(df['DepartureTime'], df['DelayMinutes'], marker='o', label=flight_number,color=colors[index])

plt.title('Flight Delay Minutes by Flight Number')
plt.xlabel('Flight Number')
plt.ylabel('Delay Minutes')
plt.savefig("DelaysDist-ByDeptTime.png")
plt.close()

# Delay per date
mean_delay_by_date = df.groupby('DepartureDate')['DelayMinutes'].mean().reset_index()

# Plot mean delay over time
plt.figure(figsize=(12, 6))
sns.lineplot(x='DepartureDate', y='DelayMinutes', data=mean_delay_by_date, marker='o')
plt.title('Mean Flight Delays Over Date')
plt.xlabel('Departure Date')
plt.ylabel('Mean Delay Minutes')
plt.savefig("DelayperDate.png")
plt.close()

mean_delay_by_time = df.groupby('DepartureTime')['DelayMinutes'].mean().reset_index()

# Plot mean delay over time
plt.figure(figsize=(12, 6))
sns.lineplot(x='DepartureTime', y='DelayMinutes', data=mean_delay_by_time, marker='o')
plt.title('Mean Flight Delays Over Time')
plt.xlabel('Departure Time')
plt.ylabel('Mean Delay Minutes')
plt.savefig("DelayperTime.png")
plt.close()
# Findings: The amount of delay increases after 19:15

# Group by FlightNumber and calculate mean delay
mean_delay_by_flight = df.groupby('FlightNumber')['DelayMinutes'].mean().reset_index()

# Plot mean delay by FlightNumber
plt.figure(figsize=(12, 6))
sns.barplot(x='FlightNumber', y='DelayMinutes', data=mean_delay_by_flight)
plt.title('Mean Flight Delays by Flight Number')
plt.xlabel('Flight Number')
plt.ylabel('Mean Delay Minutes')
plt.savefig("MeanDelay-byFlights.png")
plt.close()
# Findings: The average delay for AA1234 is the highest, followed by UA9101

# Average Delay for each Airline
average_delay_per_airline = df.groupby('Airline')['DelayMinutes'].mean().reset_index()

print(average_delay_per_airline)

# Relationship between DepartureTime and DelayMinute
plt.figure(figsize=(12, 6))
sns.scatterplot(x='DepartureTime', y='DelayMinutes', data=df, hue='Airline', style='Airline', markers=['o', 's', 'D'])
plt.title('Flight Delays vs Departure Time')
plt.xlabel('Departure Time')
plt.ylabel('Delay Minutes')
plt.savefig("DepartureTimeVsDelay.png")
plt.close()

# To determine if there is any significant difference in delays between different airlines

# Null Hypothesis (H0): There is no significant difference in the mean delay times between the airlines.
# Alternative Hypothesis (H1): There is a significant difference in the mean delay times between the airlines.

delay_AA= df[df['Airline'] == 'American Airlines']['DelayMinutes']
delay_D= df[df['Airline'] == 'Delta']['DelayMinutes']
delay_UA= df[df['Airline'] == 'United Airlines']['DelayMinutes']

comparison_set={
  ('American Airlines','Delta'):(delay_AA,delay_D),
  ('Delta','United Airlines'):(delay_D,delay_UA),
  ('United Airlines','American Airlines'):(delay_UA,delay_AA)
}

alpha=0.05
alpha_dash = alpha / len(comparison_set)
results={}

for (i, j), (d1, d2) in comparison_set.items():
  t_stat, p_value = stats.ttest_ind(d1, d2)
  results[(i, j)] = (t_stat, p_value)

  print(f'Comparing {i} and {j}:')
  print(f'T-statistic: {t_stat}, P-value: {p_value}')

  df_t = len(d1) + len(d2) - 2
  critical_t = stats.t.ppf(1 - alpha_dash / 2, df_t)

  x = np.linspace(-4, 4, 1000)
  y = stats.t.pdf(x, df_t)

  # Plot the standard t-distribution curve
  plt.figure(figsize=(10, 6))
  plt.plot(x, y, label='t-Distribution', color='blue')

  # The rejection region
  plt.fill_between(x, y, where=(x > critical_t) | (x < -critical_t), color='red', alpha=0.5, label='Rejection Region')

  # Plotting the t-statistic
  plt.axvline(t_stat, color='orange', linestyle='--', label=f'T-statistic: {t_stat:.2f}')

  # Critical t-values
  plt.axvline(critical_t, color='green', linestyle='--', label=f'Critical t-value: {critical_t:.2f}')
  plt.axvline(-critical_t, color='green', linestyle='--')

  plt.title(f't-Test for {i} vs {j}\n(P-value: {p_value:.4f})')
  plt.xlabel('t-value')
  plt.ylabel('Probability Density')
  plt.legend()
  plt.grid(True)
  plt.savefig(f"t-testCurve{i}_{j}.png")
  plt.close()

  # if p_value is greater than alpha_dash then we accept the null hypothesis or fail to reject null hypothesis H0, we reject null hypothesis H0
  if p_value < alpha_dash:
      conclusion = "Reject the null hypothesis."
  else:
        conclusion = "Fail to reject the null hypothesis."

  print("Conclusion : ", conclusion)
  print()

# Since all the pairs fail to reject Null Hypothesis, so there is no significant difference in the mean delay times between the airlines.

average_delay = df.groupby('Airline')['DelayMinutes'].mean().reset_index()

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Bar Plot for Average Delay by Airline
sns.barplot(x='Airline', y='DelayMinutes', data=average_delay, ax=axes[0], palette="Blues_d")
axes[0].set_title('Average Delay by Airline')
axes[0].set_ylabel('Average Delay (Minutes)')
axes[0].set_xlabel('Airline')

# Box Plot for Delay Distribution by Airline
sns.boxplot(x='Airline', y='DelayMinutes', data=df, ax=axes[1], palette="Set2")
axes[1].set_title('Delay Distribution by Airline')
axes[1].set_ylabel('Delay Minutes')
axes[1].set_xlabel('Airline')

plt.tight_layout()
plt.savefig("Delay_distributions.png")
plt.close()

# The impact of departure times on delays.
df['DepartureTimeMinutes'] = pd.to_datetime(df['DepartureTime'], format='%H:%M').dt.hour * 60 + pd.to_datetime(df['DepartureTime'], format='%H:%M').dt.minute

correlation = df['DepartureTimeMinutes'].corr(df['DelayMinutes'])
print(f'Correlation between Departure Time (in minutes) and Delay Minutes: {correlation}')

plt.figure(figsize=(12, 6))
sns.scatterplot(x='DepartureTimeMinutes', y='DelayMinutes', data=df, hue='Airline', style='Airline')

# Trend line
sns.regplot(x='DepartureTimeMinutes', y='DelayMinutes', data=df, scatter=False, color='red', ci=None)

plt.title('Impact of Departure Time on Flight Delays')
plt.xlabel('Departure Time (minutes since midnight)')
plt.ylabel('Delay Minutes')
plt.savefig("departureTimeVsFlightDelay.png")
plt.close()

#Saving the progress with a csv file
df.to_csv('flight_schedule-3.csv', index=False)