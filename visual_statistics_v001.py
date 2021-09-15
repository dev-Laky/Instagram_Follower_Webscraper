from matplotlib import pyplot as plt
from main_v115 import Scraper, json, red

__version__ = "0.0.1"


class VisualStats:
    def __init__(self, autorun=True):
        self.x_runs = []
        self.y_followers = []
        self.z_FST = []
        self.q_download = []
        self.v_follower_per_sec = []
        self.b_data_per_follower = []
        if autorun:
            self.run()

    def run(self):
        Scraper.check_for_data()
        self.get_data()
        self.create_cs()

    def create_cs(self):
        plt.plot(self.x_runs, self.y_followers)
        plt.plot(self.x_runs, self.z_FST)
        plt.plot(self.x_runs, self.q_download)
        plt.plot(self.x_runs, self.v_follower_per_sec)
        plt.plot(self.x_runs, self.b_data_per_follower)
        plt.title("Data Visualization per Run")
        plt.xlabel("Runs")
        plt.ylabel("Data Values")
        plt.legend(["Follower Count", "Run-Time", "Downloadspeed", "Follower per Second", "Data per Follower"])
        plt.show()

    def get_data(self):
        with open(fr"{Scraper.data_dir}/{Scraper.file_id}.json", encoding="utf-8") as json_file:
            try:
                data_list = json.load(json_file)
                for n, data_package in enumerate(data_list):
                    try:
                        self.y_followers.append(data_package["followers"])
                        self.z_FST.append(data_package["FST"])
                        self.q_download.append(data_package["download"])
                        self.v_follower_per_sec.append(data_package["follower_per_sec"])
                        self.b_data_per_follower.append(data_package["data_per_follower"])
                        self.x_runs.append(n + 1)
                    except KeyError:
                        print(red(f"ERROR 101: KEY ERROR DETECTED AT PACKAGE {n + 1}"))
            except (json.decoder.JSONDecodeError, AttributeError) as exc:
                print(red("ERROR 202: DATA FILE IS CORRUPTED"))


if __name__ == '__main__':
    print(__version__)
    Scraper = Scraper(None, None, None)
    VisualStats(autorun=False).run()
