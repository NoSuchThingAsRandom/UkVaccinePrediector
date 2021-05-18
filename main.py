import csv
from datetime import datetime, timedelta

import matplotlib
import numpy
from matplotlib.axes import Axes

from matplotlib import pyplot as plt, ticker
import calendar

# DATE_FORMAT="%d/%m/%Y"
DISPLAY_DATE_FORMAT = "%d-%m"
DATE_FORMAT = "%Y-%m-%d"


def toInt(x: str):
    if x.isdigit():
        return int(x)


def read_data(filename="data_2021-May-17.csv"):
    file = open(filename)
    csv_reader = csv.DictReader(file)
    raw_data = []
    for row in csv_reader:
        raw_data.append(row)
        pass
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

        weekday = calendar.day_name[datetime.strptime(day_dates[0], DATE_FORMAT).weekday()]
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

TARGET_DOSES = 53000000
first_dose_target_reached = None
second_dose_target_reached = None
total_required = 0
total_given = 0
average_dose = 0
offset = 7 * 12
differences = []
# dates = ["10/01"]
dates = ["01-10"]

start_date = "2021-01-10"
# start_date = "10/02/2021"
start_index = list(data["dates"]).index(start_date)
print("Start Date Index: " + str(start_index))
initial_first_dose = data["cumulative_first_dose"][start_index]
initial_second_dose = data["cumulative_second_dose"][start_index]

# avg_start_date = "07/04/2021"
avg_start_date = "2021-04-07"
avg_start_index = list(data["dates"]).index(avg_start_date)
first_dose_avg = int(numpy.average(data["first_dose_per_day"][avg_start_index]))
second_dose_avg = int(numpy.average(data["second_dose_per_day"][avg_start_index]))

print("Avg Dose Start Index: " + str(avg_start_index))
print("    First Dose Avg: " + str(first_dose_avg))
print("    Second Dose Avg: " + str(second_dose_avg))
print("    Total Dose Avg: " + str(first_dose_avg + second_dose_avg))

print("Initial first dose:" + str(initial_first_dose))
print("Initial first dose:" + str(initial_second_dose))

second_dose_backlog = [data["cumulative_first_dose"][0] - data["cumulative_second_dose"][0]]

first_given_per_day = [0]
second_given_per_day = [0]

first_given_per_day_cumulative = list(data["cumulative_first_dose"])[1:]
second_given_per_day_cumulative = list(data["cumulative_second_dose"])[1:]

total_first_given = initial_first_dose
total_second_given = initial_second_dose

# On existing data
for index in range(1, len(data["dates"]) - 1):
    print("-----\nDate: " + str(data["dates"][index]))

    fst_given = data["first_dose_per_day"][index]
    first_given_per_day.append(fst_given)
    total_first_given += fst_given
    print("    First:  " + str(fst_given))
    print("    Total First Given: " + str(total_first_given))

    print("Cumm Diff:" + str(total_first_given - first_given_per_day_cumulative[index]))

    snd_given = data["second_dose_per_day"][index]
    second_given_per_day.append(snd_given)
    total_second_given += snd_given
    print("    Second: " + str(snd_given))

    dif = fst_given - snd_given
    differences.append(dif)
    print("    Dif:    " + str(dif))
    second_dose_backlog.append(dif + second_dose_backlog[-1])
    date = datetime.strptime(data["dates"][index], DATE_FORMAT)
    date = date.strftime(DISPLAY_DATE_FORMAT)
    dates.append(date)

print(first_given_per_day_cumulative)
print("Total First Given: " + str(total_first_given))
# Clearing Backlog
print("-----\n" * 5)
print("Clearing Backlog")
while second_dose_backlog[-1] > 0:
    print(dates[-1])
    new_date = datetime.strptime(dates[-1], DISPLAY_DATE_FORMAT)
    new_date += timedelta(days=1)
    dates.append(new_date.strftime(DISPLAY_DATE_FORMAT))
    print("-----\nDate: " + str(new_date))

    if total_first_given < TARGET_DOSES:
        fst_given = first_dose_avg
        snd_given = second_dose_avg
    else:
        if first_dose_target_reached is None:
            first_dose_target_reached = new_date
        fst_given = 0
        snd_given = first_dose_avg + second_dose_avg

    first_given_per_day.append(fst_given)
    total_first_given += fst_given
    print("    Total First Given: " + str(total_first_given))
    first_given_per_day_cumulative.append(total_first_given)
    print("    First:  " + str(fst_given))

    second_given_per_day.append(snd_given)
    total_second_given += snd_given
    second_given_per_day_cumulative.append(total_second_given)
    print("    Second: " + str(snd_given))

    dif = fst_given - snd_given
    differences.append(dif)
    print("    Dif:    " + str(dif))
    second_dose_backlog.append(dif + second_dose_backlog[-1])


print("Backlog Cleared")

while total_first_given < TARGET_DOSES or total_second_given < TARGET_DOSES:
    new_date = datetime.strptime(dates[-1], DISPLAY_DATE_FORMAT)
    new_date += timedelta(days=1)
    dates.append(new_date.strftime(DISPLAY_DATE_FORMAT))
    print("-----\nDate: " + str(new_date))

    if total_first_given < TARGET_DOSES:
        fst_given = int((first_dose_avg + second_dose_avg) / 2)
        snd_given = int((first_dose_avg + second_dose_avg) / 2)
    else:
        if first_dose_target_reached is None:
            first_dose_target_reached = new_date
        fst_given = 0
        snd_given = int(first_dose_avg + second_dose_avg)
    first_given_per_day.append(fst_given)
    total_first_given += fst_given
    first_given_per_day_cumulative.append(total_first_given)
    print("    First:  " + str(fst_given))

    second_given_per_day.append(snd_given)
    total_second_given += snd_given
    second_given_per_day_cumulative.append(total_second_given)
    if total_second_given > TARGET_DOSES and second_dose_target_reached is None:
        second_dose_target_reached = new_date
    print("    Second: " + str(snd_given))

    dif = fst_given - snd_given
    differences.append(dif)
    print("    Dif:    " + str(dif))
    second_dose_backlog.append(dif + second_dose_backlog[-1])

print("Backlog" + str(second_dose_backlog))
print("---------------")
print("Total First Given: " + str(total_first_given))
print("Total Second Given: " + str(total_second_given))
print("---------------")

if first_dose_target_reached is not None:
    first_dose_target_reached = first_dose_target_reached.strftime(DISPLAY_DATE_FORMAT)
if second_dose_target_reached is not None:
    second_dose_target_reached = second_dose_target_reached.strftime(DISPLAY_DATE_FORMAT)

print("First Dose Target Reached: " + str(first_dose_target_reached))
print("Second Dose Target Reached: " + str(second_dose_target_reached))
print("---------------")

fig, ax = plt.subplots(4, 1)
fig.set_size_inches(24, 24)
fig.subplots_adjust(top=0.9, bottom=0.1, hspace=0.2, wspace=0.2)

differences = list(map(lambda x: x / 100000, differences))
ax[0].set_title("'Required' Second Doses Against Given Second Doses")
ax[0].plot(dates[1:], differences)
ax[0].set_xlabel("Date")
ax[0].set_ylabel("Doses (Per 100,000)")
ax[0].set_xticks(numpy.arange(0, len(dates) + 1, 7))

second_dose_backlog = list(map(lambda x: x / 1000000, second_dose_backlog))
ax[1].set_title("Second Dose Backlog")
ax[1].plot(dates, second_dose_backlog)
ax[1].set_xlabel("Date")
ax[1].set_ylabel("Doses (Per 1,000,000)")
ax[1].set_xticks(numpy.arange(0, len(dates) + 1, 7))

first_given_per_day = list(map(lambda x: x / 100000, first_given_per_day))
second_given_per_day = list(map(lambda x: x / 100000, second_given_per_day))
ax[2].set_title("Doses Per Day")
ax[2].plot(dates, first_given_per_day, label="First Dose Per Day")
ax[2].plot(dates, second_given_per_day, label="Second Dose Per Day")
ax[2].set_xlabel("Date")
ax[2].set_ylabel("Doses (Per 100,000)")
ax[2].legend()
ax[2].set_xticks(numpy.arange(0, len(dates) + 1, 7))

first_given_per_day_cumulative = list(map(lambda x: x / 1000000, first_given_per_day_cumulative))
second_given_per_day_cumulative = list(map(lambda x: x / 1000000, second_given_per_day_cumulative))
print(first_given_per_day_cumulative)
ax[3].set_title("Cumulative Doses")
ax[3].plot(dates, first_given_per_day_cumulative, label="Cumulative First Dose Per Day")
ax[3].plot(dates, second_given_per_day_cumulative, label="Cumulative Second Dose Per Day")
ax[3].set_xlabel("Date")
ax[3].set_ylabel("Doses (Per 10,000,000)")
ax[3].legend()
ax[3].set_xticks(numpy.arange(0, len(dates) + 1, 7))

caption_text = "(Using First Dose Average: " + str(first_dose_avg) + " and Second Dose Average: " + str(
    second_dose_avg) + ")"
caption_text += "\nFirst Dose Total: " + str(total_first_given) + " and Second Dose Total: " + str(
    total_second_given) + ")"
caption_text += "\nFirst Dose Target Reached: " + str(
    first_dose_target_reached) + " and Second Dose Target Reached: " + str(second_dose_target_reached)
fig.text(0.5, 0.05, caption_text, ha="center")

# fig.savefig("plots")
fig.show()
# print(week_avg_total)


# fig.legend()