from datetime import datetime, timedelta

import numpy
from matplotlib import pyplot as plt

DISPLAY_DATE_FORMAT = "%d-%m"
IMPORT_DATE_FORMAT = "%Y-%m-%d"
# The total number of doses to administer
TARGET_DOSES = 53000000


class Predictor:
    def __init__(self, data: dict, start_date="2021-01-11", avg_start_date="2021-04-07"):
        """

        :param data:
        :param start_date: The date to start counting from
        :param avg_start_date: The date to start the "average" dose calculations from
        """
        self.data = data

        # The dates upon the targets being reached
        self.date_first_dose_target_reached = None
        self.date_second_dose_target_reached = None
        self.date_backlog_cleared = None

        # Stores the differences between first and second doses per day
        self.differences = []

        # dates = ["10/01"]
        # Stores the list of dates for pretty display
        self.dates = ["01-10"]

        # Calculates the initial backlog of doses, before data collection properly started
        start_index = list(self.data["dates"]).index(start_date)
        print("Start Date Index: " + str(start_index))
        initial_first_dose = self.data["cumulative_first_dose"][start_index]
        initial_second_dose = self.data["cumulative_second_dose"][start_index]

        print("Initial first dose:" + str(initial_first_dose))
        print("Initial second dose:" + str(initial_second_dose))

        self.avg_start_date = avg_start_date
        avg_start_index = list(data["dates"]).index(avg_start_date)
        self.first_dose_avg = int(numpy.average(data["first_dose_per_day"][avg_start_index]))
        self.second_dose_avg = int(numpy.average(data["second_dose_per_day"][avg_start_index]))
        self.total_dose_avg = self.first_dose_avg + self.second_dose_avg
        print("Avg Dose Start Index: " + str(avg_start_index))
        print("    First Dose Avg: " + str(self.first_dose_avg))
        print("    Second Dose Avg: " + str(self.second_dose_avg))
        print("    Total Dose Avg: " + str(self.total_dose_avg))

        # A list of the backlog of second doses required to administer, per day
        self.second_dose_backlog = [data["cumulative_first_dose"][0] - data["cumulative_second_dose"][0]]

        # The doses given per day,
        # This is separate from the data to account for predicted dose values
        self.first_doses_given_per_day = [0]
        self.second_doses_given_per_day = [0]

        # The total doses given, per day
        # This is separate from the data to account for predicted dose values
        self.first_doses_given_per_day_cumulative = list(data["cumulative_first_dose"])[1:]
        self.second_doses_given_per_day_cumulative = list(data["cumulative_second_dose"])[1:]

        # The sum of all doses given
        self.total_first_doses_given = initial_first_dose
        self.total_second_doses_given = initial_second_dose

    def import_existing_data(self):
        for index in range(1, len(self.data["dates"]) - 1):
            print("-----\nDate: " + str(self.data["dates"][index]))

            first_dose_given = self.data["first_dose_per_day"][index]
            self.first_doses_given_per_day.append(first_dose_given)
            self.total_first_doses_given += first_dose_given
            print("    First Dose:  " + str(first_dose_given))
            print("    Total First Dose Given: " + str(self.total_first_doses_given))

            # The calculated value should be the same as the original value
            assert self.total_first_doses_given == self.first_doses_given_per_day_cumulative[index]

            second_dose_given = self.data["second_dose_per_day"][index]
            self.second_doses_given_per_day.append(second_dose_given)
            self.total_second_doses_given += second_dose_given
            print("    Second Dose: " + str(second_dose_given))
            print("    Total Second Dose Given: " + str(self.total_second_doses_given))

            dif = first_dose_given - second_dose_given
            self.differences.append(dif)
            print("    Difference between doses:    " + str(dif))

            self.second_dose_backlog.append(dif + self.second_dose_backlog[-1])

            date = datetime.strptime(self.data["dates"][index], IMPORT_DATE_FORMAT)
            date = date.strftime(DISPLAY_DATE_FORMAT)
            self.dates.append(date)

    def clear_backlog(self):
        """
        Extrapolates from existing data to predict when the backlog will be cleared
        """
        # TODO Change to finishing when only 12 weeks of backlog available
        # TODO Compare against first doses 12 weeks ago
        while self.second_dose_backlog[-1] > 0:
            # Calculate the new date
            new_date = datetime.strptime(self.dates[-1], DISPLAY_DATE_FORMAT)
            new_date += timedelta(days=1)
            self.dates.append(new_date.strftime(DISPLAY_DATE_FORMAT))
            print("-----\nDate: " + str(new_date))

            # Use average doses, until TARGET reached
            # Then use all available doses for second dose
            if self.total_first_doses_given < TARGET_DOSES:
                first_dose_given = self.first_dose_avg
                second_dose_given = self.second_dose_avg
            else:
                if self.date_first_dose_target_reached is None:
                    self.date_first_dose_target_reached = new_date
                first_dose_given = 0
                second_dose_given = self.first_dose_avg + self.second_dose_avg

            self.first_doses_given_per_day.append(first_dose_given)
            self.total_first_doses_given += first_dose_given
            self.first_doses_given_per_day_cumulative.append(self.total_first_doses_given)
            print("    First Dose:  " + str(first_dose_given))
            print("    Total First Doses Given: " + str(self.total_first_doses_given))

            self.second_doses_given_per_day.append(second_dose_given)
            self.total_second_doses_given += second_dose_given
            self.second_doses_given_per_day_cumulative.append(self.total_second_doses_given)
            print("    Second Dose: " + str(second_dose_given))
            print("    Total Second Dose Given: " + str(self.total_second_doses_given))

            dif = first_dose_given - second_dose_given
            self.differences.append(dif)
            print("    Difference between doses:    " + str(dif))
            self.second_dose_backlog.append(dif + self.second_dose_backlog[-1])

    def finish_final_doses(self):
        """
        Splits dose capacity evenly between first and second doses, until all doses given
        """
        # TODO Find a better model for distributing doses
        while self.total_first_doses_given < TARGET_DOSES or self.total_second_doses_given < TARGET_DOSES:
            # Calculate the new date
            new_date = datetime.strptime(self.dates[-1], DISPLAY_DATE_FORMAT)
            new_date += timedelta(days=1)
            self.dates.append(new_date.strftime(DISPLAY_DATE_FORMAT))
            print("-----\nDate: " + str(new_date))

            # Split capacity evenly, until target reached
            # Then use all available doses for second dose
            if self.total_first_doses_given < TARGET_DOSES:
                first_dose_given = int(self.total_dose_avg / 2)
                second_dose_given = int(self.total_dose_avg / 2)
            else:
                if self.date_first_dose_target_reached is None:
                    self.date_first_dose_target_reached = new_date.strftime(DISPLAY_DATE_FORMAT)
                first_dose_given = 0
                second_dose_given = int(self.total_dose_avg)

            self.first_doses_given_per_day.append(first_dose_given)
            self.total_first_doses_given += first_dose_given
            self.first_doses_given_per_day_cumulative.append(self.total_first_doses_given)
            print("    First Dose:  " + str(first_dose_given))
            print("    Total First Doses Given: " + str(self.total_first_doses_given))

            self.second_doses_given_per_day.append(second_dose_given)
            self.total_second_doses_given += second_dose_given
            self.second_doses_given_per_day_cumulative.append(self.total_second_doses_given)
            if self.total_second_doses_given > TARGET_DOSES and self.date_second_dose_target_reached is None:
                self.date_second_dose_target_reached = new_date.strftime(DISPLAY_DATE_FORMAT)

            print("    Second Dose: " + str(second_dose_given))
            print("    Total Second Dose Given: " + str(self.total_second_doses_given))

            dif = first_dose_given - second_dose_given
            self.differences.append(dif)
            print("    Difference between doses:    " + str(dif))

            self.second_dose_backlog.append(dif + self.second_dose_backlog[-1])

    def plot_results(self):

        # Build figure for plotting
        fig, ax = plt.subplots(4, 1)
        fig.set_size_inches(24, 24)
        fig.subplots_adjust(top=0.9, bottom=0.1, hspace=0.2, wspace=0.2)

        # Normalise for scale
        differences = list(map(lambda x: x / 100000, self.differences))
        ax[0].set_title("'Required' Second Doses Against Given Second Doses")
        ax[0].plot(self.dates[1:], differences)
        ax[0].set_xlabel("Date")
        ax[0].set_ylabel("Doses (Per 100,000)")
        ax[0].set_xticks(numpy.arange(0, len(self.dates) + 1, 7))

        # Normalise for scale
        second_dose_backlog = list(map(lambda x: x / 1000000, self.second_dose_backlog))
        ax[1].set_title("Second Dose Backlog")
        ax[1].plot(self.dates, second_dose_backlog)
        ax[1].set_xlabel("Date")
        ax[1].set_ylabel("Doses (Per 1,000,000)")
        ax[1].set_xticks(numpy.arange(0, len(self.dates) + 1, 7))

        # Normalise for scale
        first_doses_given_per_day = list(map(lambda x: x / 100000, self.first_doses_given_per_day))
        second_doses_given_per_day = list(map(lambda x: x / 100000, self.second_doses_given_per_day))
        ax[2].set_title("Doses Per Day")
        ax[2].plot(self.dates, first_doses_given_per_day, label="First Dose Per Day")
        ax[2].plot(self.dates, second_doses_given_per_day, label="Second Dose Per Day")
        ax[2].set_xlabel("Date")
        ax[2].set_ylabel("Doses (Per 100,000)")
        ax[2].legend()
        ax[2].set_xticks(numpy.arange(0, len(self.dates) + 1, 7))

        # Normalise for scale
        first_doses_given_per_day_cumulative = list(
            map(lambda x: x / 1000000, self.first_doses_given_per_day_cumulative))
        second_doses_given_per_day_cumulative = list(
            map(lambda x: x / 1000000, self.second_doses_given_per_day_cumulative))
        print(first_doses_given_per_day_cumulative)
        ax[3].set_title("Cumulative Doses")
        ax[3].plot(self.dates, first_doses_given_per_day_cumulative, label="Cumulative First Dose Per Day")
        ax[3].plot(self.dates, second_doses_given_per_day_cumulative, label="Cumulative Second Dose Per Day")
        ax[3].set_xlabel("Date")
        ax[3].set_ylabel("Doses (Per 10,000,000)")
        ax[3].legend()
        ax[3].set_xticks(numpy.arange(0, len(self.dates) + 1, 7))

        # Add caption detailing some basic stats
        caption_text = "(Using First Dose Average: " + str(self.first_dose_avg) + " and Second Dose Average: " + str(
            self.second_dose_avg) + ")"
        caption_text += "\n(Using data from " + str(self.avg_start_date) + " to now)"
        caption_text += "\nFirst Dose Total: " + str(self.total_first_doses_given) + " and Second Dose Total: " + str(
            self.total_second_doses_given) + ")"
        caption_text += "\nFirst Dose Target Reached: " + str(
            self.date_first_dose_target_reached) + " and Second Dose Target Reached: " + str(
            self.date_second_dose_target_reached)
        fig.text(0.5, 0.05, caption_text, ha="center")

        # fig.savefig("plots")
        fig.show()

    def run(self):
        self.import_existing_data()
        print("Finished importing existing data")
        print("     Total First Given: " + str(self.total_first_doses_given))

        print("Clearing Backlog")

        print("Backlog Cleared on date: " + self.dates[-1])
        self.date_backlog_cleared = self.dates[-1]

        self.finish_final_doses()

        print("Finished Vaccines on: " + str(self.dates[-1]))
        print("Backlog" + str(self.second_dose_backlog))
        print("---------------")
        print("Total First Given: " + str(self.total_first_doses_given))
        print("Total Second Given: " + str(self.total_second_doses_given))
        print("---------------")

        if self.date_first_dose_target_reached is None:
            self.date_first_dose_target_reached = self.dates[-1]
        if self.date_second_dose_target_reached is None:
            self.date_second_dose_target_reached = self.dates[-1]

        print("First Dose Target Reached: " + str(self.date_first_dose_target_reached))
        print("Second Dose Target Reached: " + str(self.date_second_dose_target_reached))
        print("---------------")
        self.plot_results()
