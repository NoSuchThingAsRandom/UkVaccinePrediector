import calendar
import csv
from datetime import datetime, timedelta

import numpy
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

# DATE_FORMAT="%d/%m/%Y"
DISPLAY_DATE_FORMAT = "%d-%m"
IMPORT_DATE_FORMAT = "%Y-%m-%d"


def toInt(x: str):
    if x.isdigit():
        return int(x)


def read_data(filename="data_2021-May-17.csv"):
    """
    Reads CSV with the provided filename, into a dict of column names, where the value is an array of values per day
    :param filename: The filename to read
    :return: A dict for indexing columns per day
    """
    # TODO Switch to Pandas maybe?
    file = open(filename)
    csv_reader = csv.DictReader(file)
    raw_data = []
    for row in csv_reader:
        raw_data.append(row)
        pass
    # Reversed so first entry, is from 10/1/2021
    raw_data.reverse()
    raw_data = numpy.array(raw_data)
    data = {}
    data["total_vaccines_per_day"] = numpy.array(
        list(filter(lambda val: val != None, map(lambda day: toInt(day["newVaccinesGivenByPublishDate"]), raw_data))))
    data["first_dose_per_day"] = numpy.array(list(
        filter(lambda val: val != None,
               map(lambda day: toInt(day["newPeopleVaccinatedFirstDoseByPublishDate"]), raw_data))))
    data["second_dose_per_day"] = numpy.array(list(
        filter(lambda val: val != None,
               map(lambda day: toInt(day["newPeopleVaccinatedSecondDoseByPublishDate"]), raw_data))))
    data["dates"] = numpy.array(
        list(map(lambda day: day["date"], raw_data)))
    data["cumulative_first_dose"] = numpy.array(list(
        filter(lambda val: val != None,
               map(lambda day: toInt(day["cumPeopleVaccinatedFirstDoseByPublishDate"]), raw_data))))
    data["cumulative_second_dose"] = numpy.array(list(
        filter(lambda val: val != None,
               map(lambda day: toInt(day["cumPeopleVaccinatedSecondDoseByPublishDate"]), raw_data))))
    return data


def plot_daily_breakdown(ax: [Axes], vaccines_per_day, dates):
    day_min = []
    day_max = []
    day_avg = []
    week_avg_total = 0
    for day in range(7):
        day_data = vaccines_per_day[day::7]
        day_dates = dates[day::7]

        min_val = numpy.min(day_data)
        max_val = max(day_data)
        avg_val = numpy.mean(day_data)
        week_avg_total += avg_val

        day_min.append(min_val)
        day_max.append(max_val)
        day_avg.append(avg_val)

        weekday = calendar.day_name[datetime.strptime(day_dates[0], IMPORT_DATE_FORMAT).weekday()]
        title = "Day: " + weekday + " Min: " + str(min_val) + " Max: " + str(max_val) + " Avg: " + str(
            avg_val)

        ax[day].plot(day_dates, day_data, label=title)
        ax[day].set_xticks(numpy.arange(0, len(day_dates) + 1, 7))
        ax[day].set_title(title)
        ax[day].set_ybound(50000, 900000)


def plot_weekly_averages(ax: Axes, vaccines_per_day, dates):
    week_dates = []
    week_plot = []
    for week_index in range(int(vaccines_per_day.shape[0] / 7)):
        week_dates.append(dates[week_index * 7])
        week_total = 0
        for day in range(7):
            week_total += vaccines_per_day[(week_index * 7) + day]
        week_plot.append(week_total)
    ax.plot(week_dates, week_plot)
    ax.set_xticks(numpy.arange(0, len(week_dates) + 1, 2))
    ax.set_title("Weekly vaccine totals")


def plot_graphs(data):
    fig, ax = plt.subplots(3, 8)
    print(ax)
    fig.set_size_inches(50, 50)
    fig.subplots_adjust(top=0.9, bottom=0.1, hspace=0.5, wspace=0.2)
    plot_daily_breakdown(ax[0], data["total_vaccines_per_day"], data["dates"])
    plot_weekly_averages(ax[0], data["total_vaccines_per_day"], data["dates"])

    plot_daily_breakdown(ax[1], data["first_dose_per_day"], data["dates"])
    plot_weekly_averages(ax[1], data["first_dose_per_day"], data["dates"])

    plot_daily_breakdown(ax[2], data["second_dose_per_day"], data["dates"])
    plot_weekly_averages(ax[2], data["second_dose_per_day"], data["dates"])
    # ax[1].set_xticks(numpy.arange(0, len(dates) + 1, 7))
    fig.show()


data = read_data()
"""
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(10, 10)
plot_weekly_averages(ax, data["total_vaccines_per_day"], data["dates"])
fig.show()
#plot_graphs(data)
"""

# The total number of doses to administer
TARGET_DOSES = 53000000
# The dates upon the targets being reached
date_first_dose_target_reached = None
date_second_dose_target_reached = None
date_backlog_cleared = None

# Stores the differences between first and second doses per day
differences = []
# dates = ["10/01"]
# Stores the list of dates for pretty display
dates = ["01-10"]

# The date to start counting from
start_date = "2021-01-11"
# start_date = "10/02/2021"

# Calculates the initial backlog of doses, before data collection properly started
start_index = list(data["dates"]).index(start_date)
print("Start Date Index: " + str(start_index))
initial_first_dose = data["cumulative_first_dose"][start_index]
initial_second_dose = data["cumulative_second_dose"][start_index]

print("Initial first dose:" + str(initial_first_dose))
print("Initial second dose:" + str(initial_second_dose))

# The date to start the "average" dose calculations from
# avg_start_date = "07/04/2021"
avg_start_date = "2021-04-07"
avg_start_index = list(data["dates"]).index(avg_start_date)
first_dose_avg = int(numpy.average(data["first_dose_per_day"][avg_start_index]))
second_dose_avg = int(numpy.average(data["second_dose_per_day"][avg_start_index]))

print("Avg Dose Start Index: " + str(avg_start_index))
print("    First Dose Avg: " + str(first_dose_avg))
print("    Second Dose Avg: " + str(second_dose_avg))
print("    Total Dose Avg: " + str(first_dose_avg + second_dose_avg))

# A list of the backlog of second doses required to administer, per day
second_dose_backlog = [data["cumulative_first_dose"][0] - data["cumulative_second_dose"][0]]

# The doses given per day,
# This is separate from the data to account for predicted dose values
first_doses_given_per_day = [0]
second_doses_given_per_day = [0]

# The total doses given, per day
# This is separate from the data to account for predicted dose values
first_doses_given_per_day_cumulative = list(data["cumulative_first_dose"])[1:]
second_doses_given_per_day_cumulative = list(data["cumulative_second_dose"])[1:]

# The sum of all doses given
total_first_doses_given = initial_first_dose
total_second_doses_given = initial_second_dose

# Import the existing data, into the arrays
for index in range(1, len(data["dates"]) - 1):
    print("-----\nDate: " + str(data["dates"][index]))

    first_dose_given = data["first_dose_per_day"][index]
    first_doses_given_per_day.append(first_dose_given)
    total_first_doses_given += first_dose_given
    print("    First Dose:  " + str(first_dose_given))
    print("    Total First Dose Given: " + str(total_first_doses_given))

    # The calculated value should be the same as the original value
    assert total_first_doses_given == first_doses_given_per_day_cumulative[index]

    second_dose_given = data["second_dose_per_day"][index]
    second_doses_given_per_day.append(second_dose_given)
    total_second_doses_given += second_dose_given
    print("    Second Dose: " + str(second_dose_given))
    print("    Total Second Dose Given: " + str(total_second_doses_given))

    dif = first_dose_given - second_dose_given
    differences.append(dif)
    print("    Difference between doses:    " + str(dif))

    second_dose_backlog.append(dif + second_dose_backlog[-1])

    date = datetime.strptime(data["dates"][index], IMPORT_DATE_FORMAT)
    date = date.strftime(DISPLAY_DATE_FORMAT)
    dates.append(date)
print("Finished importing existing data")
print("     Total First Given: " + str(total_first_doses_given))

# Clearing Backlog
"""
Extrapolates from existing data to predict when the backlog will be cleared 
"""
print("-----\n" * 2)
print("Clearing Backlog")
# TODO Change to finishing when only 12 weeks of backlog available
# TODO Compare against first doses 12 weeks ago
while second_dose_backlog[-1] > 0:
    # Calculate the new date
    new_date = datetime.strptime(dates[-1], DISPLAY_DATE_FORMAT)
    new_date += timedelta(days=1)
    dates.append(new_date.strftime(DISPLAY_DATE_FORMAT))
    print("-----\nDate: " + str(new_date))

    # Use average doses, until TARGET reached
    # Then use all available doses for second dose
    if total_first_doses_given < TARGET_DOSES:
        first_dose_given = first_dose_avg
        second_dose_given = second_dose_avg
    else:
        if date_first_dose_target_reached is None:
            date_first_dose_target_reached = new_date
        first_dose_given = 0
        second_dose_given = first_dose_avg + second_dose_avg

    first_doses_given_per_day.append(first_dose_given)
    total_first_doses_given += first_dose_given
    first_doses_given_per_day_cumulative.append(total_first_doses_given)
    print("    First Dose:  " + str(first_dose_given))
    print("    Total First Doses Given: " + str(total_first_doses_given))

    second_doses_given_per_day.append(second_dose_given)
    total_second_doses_given += second_dose_given
    second_doses_given_per_day_cumulative.append(total_second_doses_given)
    print("    Second Dose: " + str(second_dose_given))
    print("    Total Second Dose Given: " + str(total_second_doses_given))

    dif = first_dose_given - second_dose_given
    differences.append(dif)
    print("    Difference between doses:    " + str(dif))
    second_dose_backlog.append(dif + second_dose_backlog[-1])

print("Backlog Cleared on date: " + dates[-1])
date_backlog_cleared = dates[-1]
"""
Splits dose capacity evenly between first and second doses, until all doses given
"""
# TODO Find a better model for distributing doses
while total_first_doses_given < TARGET_DOSES or total_second_doses_given < TARGET_DOSES:
    # Calculate the new date
    new_date = datetime.strptime(dates[-1], DISPLAY_DATE_FORMAT)
    new_date += timedelta(days=1)
    dates.append(new_date.strftime(DISPLAY_DATE_FORMAT))
    print("-----\nDate: " + str(new_date))


    # Split capacity evenly, until target reached
    # Then use all available doses for second dose
    if total_first_doses_given < TARGET_DOSES:
        first_dose_given = int((first_dose_avg + second_dose_avg) / 2)
        second_dose_given = int((first_dose_avg + second_dose_avg) / 2)
    else:
        if date_first_dose_target_reached is None:
            date_first_dose_target_reached = new_date.strftime(DISPLAY_DATE_FORMAT)
        first_dose_given = 0
        second_dose_given = int(first_dose_avg + second_dose_avg)


    first_doses_given_per_day.append(first_dose_given)
    total_first_doses_given += first_dose_given
    first_doses_given_per_day_cumulative.append(total_first_doses_given)
    print("    First Dose:  " + str(first_dose_given))
    print("    Total First Doses Given: " + str(total_first_doses_given))


    second_doses_given_per_day.append(second_dose_given)
    total_second_doses_given += second_dose_given
    second_doses_given_per_day_cumulative.append(total_second_doses_given)
    if total_second_doses_given > TARGET_DOSES and date_second_dose_target_reached is None:
        date_second_dose_target_reached = new_date.strftime(DISPLAY_DATE_FORMAT)

    print("    Second Dose: " + str(second_dose_given))
    print("    Total Second Dose Given: " + str(total_second_doses_given))

    dif = first_dose_given - second_dose_given
    differences.append(dif)
    print("    Difference between doses:    " + str(dif))

    second_dose_backlog.append(dif + second_dose_backlog[-1])

print("Finished Vaccines on: "+str(dates[-1]))
print("Backlog" + str(second_dose_backlog))
print("---------------")
print("Total First Given: " + str(total_first_doses_given))
print("Total Second Given: " + str(total_second_doses_given))
print("---------------")

if date_first_dose_target_reached is None:
    date_first_dose_target_reached=dates[-1]
if date_second_dose_target_reached is None:
    date_second_dose_target_reached=dates[-1]


print("First Dose Target Reached: " + str(date_first_dose_target_reached))
print("Second Dose Target Reached: " + str(date_second_dose_target_reached))
print("---------------")


# Build figure for plotting
fig, ax = plt.subplots(4, 1)
fig.set_size_inches(24, 24)
fig.subplots_adjust(top=0.9, bottom=0.1, hspace=0.2, wspace=0.2)

# Normalise for scale
differences = list(map(lambda x: x / 100000, differences))
ax[0].set_title("'Required' Second Doses Against Given Second Doses")
ax[0].plot(dates[1:], differences)
ax[0].set_xlabel("Date")
ax[0].set_ylabel("Doses (Per 100,000)")
ax[0].set_xticks(numpy.arange(0, len(dates) + 1, 7))


# Normalise for scale
second_dose_backlog = list(map(lambda x: x / 1000000, second_dose_backlog))
ax[1].set_title("Second Dose Backlog")
ax[1].plot(dates, second_dose_backlog)
ax[1].set_xlabel("Date")
ax[1].set_ylabel("Doses (Per 1,000,000)")
ax[1].set_xticks(numpy.arange(0, len(dates) + 1, 7))


# Normalise for scale
first_doses_given_per_day = list(map(lambda x: x / 100000, first_doses_given_per_day))
second_doses_given_per_day = list(map(lambda x: x / 100000, second_doses_given_per_day))
ax[2].set_title("Doses Per Day")
ax[2].plot(dates, first_doses_given_per_day, label="First Dose Per Day")
ax[2].plot(dates, second_doses_given_per_day, label="Second Dose Per Day")
ax[2].set_xlabel("Date")
ax[2].set_ylabel("Doses (Per 100,000)")
ax[2].legend()
ax[2].set_xticks(numpy.arange(0, len(dates) + 1, 7))

# Normalise for scale
first_doses_given_per_day_cumulative = list(map(lambda x: x / 1000000, first_doses_given_per_day_cumulative))
second_doses_given_per_day_cumulative = list(map(lambda x: x / 1000000, second_doses_given_per_day_cumulative))
print(first_doses_given_per_day_cumulative)
ax[3].set_title("Cumulative Doses")
ax[3].plot(dates, first_doses_given_per_day_cumulative, label="Cumulative First Dose Per Day")
ax[3].plot(dates, second_doses_given_per_day_cumulative, label="Cumulative Second Dose Per Day")
ax[3].set_xlabel("Date")
ax[3].set_ylabel("Doses (Per 10,000,000)")
ax[3].legend()
ax[3].set_xticks(numpy.arange(0, len(dates) + 1, 7))

# Add caption detailing some basic stats
caption_text = "(Using First Dose Average: " + str(first_dose_avg) + " and Second Dose Average: " + str(
    second_dose_avg) + ")"
caption_text+="\n(Using data from "+str(avg_start_date)+" to now)"
caption_text += "\nFirst Dose Total: " + str(total_first_doses_given) + " and Second Dose Total: " + str(
    total_second_doses_given) + ")"
caption_text += "\nFirst Dose Target Reached: " + str(
    date_first_dose_target_reached) + " and Second Dose Target Reached: " + str(date_second_dose_target_reached)
fig.text(0.5, 0.05, caption_text, ha="center")

# fig.savefig("plots")
fig.show()



