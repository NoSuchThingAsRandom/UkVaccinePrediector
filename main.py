import calendar
import csv
from datetime import datetime, timedelta

import numpy
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

# DATE_FORMAT="%d/%m/%Y"
import Predictor

DISPLAY_DATE_FORMAT = "%d-%m"
IMPORT_DATE_FORMAT = "%Y-%m-%d"


def toInt(x: str):
    if x.isdigit():
        return int(x)


def read_data(filename="data_2021-Jun-14.csv"):
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
predictor = Predictor.Predictor(data)
predictor.run()
