# main.py
import json
from train import Train
from track import Track
#from updated_bd_moment_copy import BendingMomentCalculator
from bending_moment import BendingMomentCalculator
from tkinter import Tk
from tkinter_edit import Application

# Load train data from Module.json
def load_car_parameters():
    with open('Train.json', 'r') as file:
        car_params = json.load(file)
    return car_params

def main():
    # Load train data
    car_params = load_car_parameters()
    
    # Create Train and Track objects
    train = Train(car_params)
    track = Track()  # track parameters will be loaded later via GUI
    track.load_rail_section_properties()

    # Create a BendingMomentCalculator object using the Train and Track objects
    bending_moment_calculator = BendingMomentCalculator(train, track)
    
    # Create and start the tkinter GUI
    root = Tk()
    app = Application(master=root, train=train, track=track, calculator=bending_moment_calculator)
    app.mainloop()

if __name__ == '__main__':
    main()
