import tkinter as tk
from tkinter import filedialog
from colors.colors import red, green
__version__ = "0.0.1"

GOLD = 226


def enter_exit():
    input(("--------------------\n"
           "Press Enter to exit."))


def main():
    root = tk.Tk()
    root.withdraw()

    file_path_1 = filedialog.askopenfilename()
    file_path_2 = filedialog.askopenfilename()

    if not file_path_1[-4:] == ".txt" or not file_path_2[-4:] == ".txt":  # last 4 chars
        print(red("ERROR 101: Data type must be a .txt file."))
        enter_exit()
        exit(1)

    with open(file_path_1, "r") as file:
        list_1 = file.read().split("\n")

    with open(file_path_2, "r") as file:
        list_2 = file.read().split("\n")

    '''
    print(list_1)
    print(len(list_1))
    print(list_2)
    print(len(list_2))
    '''

    for follower_name in list_1:
        if follower_name not in list_2:
            print(green(f"Found: {follower_name}"))

    enter_exit()


if __name__ == "__main__":
    main()
