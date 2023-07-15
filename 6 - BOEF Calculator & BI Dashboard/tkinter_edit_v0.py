# tkinter_edit.py
import matplotlib.pyplot as plt
import tkinter as tk
import pandas as pd
from tkinter import filedialog
from tkinter import ttk
from bending_moment import BendingMomentCalculator
import json

class Application(tk.Frame):
    def __init__(self, master=None, train=None, track=None, calculator=None):
        super().__init__(master)
        self.master = master
        self.master.title("BOEF Calculator v1.0")  # set the window title here
        self.train = train
        self.track = track
        self.calculator = calculator
        self.speed = 0  # Add this line to initialize the speed
        #self.input_file_path = None  # Add this line to initialize the input file path
        self.grid()
        self.create_widgets()
    
    # Add buttons
    def create_widgets(self):
        self.load_button = tk.Button(self) 
        self.load_button["text"] = "Load Track CSV"
        self.load_button["command"] = self.load_track_parameters # Load the track CSV file
        self.load_button.grid(row=0, column=0)

        self.add_button = tk.Button(self, text="Add", command=self.add) # Add a new car
        self.add_button.grid(row=0, column=1)

        self.speed_set_button = tk.Button(self, text="Speed Set", command=self.speed_set) # Speed set
        self.speed_set_button.grid(row=0, column=2)

        self.calculate_button = tk.Button(self, text="Calculate", command=self.calculate) # Calculate max bending moment
        self.calculate_button.grid(row=0, column=3)

        self.remove_button = tk.Button(self, text="Remove", command=self.remove) # Remove the last car
        self.remove_button.grid(row=0, column=4)

        self.clear_button = tk.Button(self, text="Clear", command=self.clear) # Clear all the inputs
        self.clear_button.grid(row=0, column=5)

        self.car_select = ttk.Combobox(self, values=["Locomotive 1", "Locomotive 2", "Wagon 1", "Wagon 2"]) # Select next input of car
        self.car_select.grid(row=1, column=0)

        self.train_sequence = tk.Label(self, text="Train Sequence: ") # Showing current sequence
        self.train_sequence.grid(row=2, column=0)

        self.status_label = tk.Label(self, text="")
        self.status_label.grid(row=4, column=0, columnspan=6, sticky="w")

    def load_track_parameters(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.track.load_track_parameters(filename)
            self.input_file_path = filename  # save the filename
            self.status_label['text'] = "Track parameters CSV file loaded successfully."
        else:
            self.status_label['text'] = "No file selected."

    def clear(self):
        self.train.clear_all()  
        self.track.clear_all()  
        self.speed = 0
        self.train_sequence['text'] = "Train Sequence: "
        self.status_label['text'] = "Inputs cleared."
    
    def add(self):
        car = self.car_select.get()
        self.train.add(car)
        self.train_sequence['text'] += car + ", "

    def remove(self):
        self.train.remove()
        train_sequence = self.train_sequence['text']
        last_comma = train_sequence.rfind(',')
        if last_comma != -1:  # Check if there's any comma in the string
            second_last_comma = train_sequence.rfind(',', 0, last_comma)
            if second_last_comma == -1:  # If there's only one car left
                self.train_sequence['text'] = "Train Sequence: "
            else:  # If there's more than one car
                self.train_sequence['text'] = train_sequence[:second_last_comma + 1] + " "

    # Set speed
    def speed_set(self):
        def submit():
            try:
                speed = float(speed_entry.get())
                self.speed = speed  # Store the speed for later use
                self.status_label['text'] = f"Speed set to {speed} mph."
                speed_window.destroy()
            except ValueError:
                self.status_label['text'] = "Invalid input for speed."

        speed_window = tk.Toplevel(self.master)
        speed_window.title("Set Speed")

        speed_label = tk.Label(speed_window, text="Enter speed:")
        speed_label.grid(row=0, column=0)

        speed_entry = tk.Entry(speed_window)
        speed_entry.grid(row=0, column=1)

        submit_button = tk.Button(speed_window, text="Submit", command=submit)
        submit_button.grid(row=1, column=0, columnspan=2)

    # def calculate(self):
    #     bending_moment_calculator = BendingMomentCalculator(self.train, self.track)
    #     dynamic_loads, wheel_params_list, combined_values_list, max_bending_moments = bending_moment_calculator.calculate_max_bending_moments_along_route(self.speed)

    #     # Read the input csv file
    #     df_input = pd.read_csv(self.input_file_path)  # use the loaded file

    #     # Copy the parameters from the input csv file
    #     foot_data = df_input["foot"]
    #     tie_plate_width = df_input["tie_plate_width"]
    #     tie_plate_length = df_input["tie_plate_length"]
    #     tie_spacing = df_input["tie_spacing"]
    #     #inertia_moment = df_input["inertia_moment"]

    #     # Calculate tie plate area
    #     #tie_plate_area = bending_moment_calculator.tie_plate_area(tie_plate_width, tie_plate_length)

    #     # Calculate dynamic parameters for each foot
    #     max_deflection = [bending_moment_calculator.max_dynamic_deflection(combined_values) for combined_values in combined_values_list]
    #     max_pressure = [bending_moment_calculator.max_dynamic_pressure(combined_values) for combined_values in combined_values_list]

    #     max_seat_force = [bending_moment_calculator.max_dynamic_railseat_force(max_pressure_val, tie_spacing_val) for max_pressure_val, tie_spacing_val in zip(max_pressure, tie_spacing)]
        
    #     # Create a new DataFrame to store the output data
    #     df_output = pd.DataFrame({
    #         "foot": foot_data,
    #         "max_bending_moment": max_bending_moments,
    #         "max_deflection": max_deflection,
    #         "max_pressure": max_pressure,
    #         "max_seat_force": max_seat_force
    #     })

    #     # Write the output DataFrame to a CSV file
    #     df_output.to_csv("/Users/mulinw/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/Courses/23spring/597/CSV_Version/Vitor_Version_Test/output.csv", index=False)  # replace "output.csv" with your desired output file path

    #     self.display_plot(max_bending_moments)

    def calculate(self):
        bending_moment_calculator = BendingMomentCalculator(self.train, self.track)
        dynamic_loads, wheel_params_list, combined_values_list, max_bending_moments = bending_moment_calculator.calculate_max_bending_moments_along_route(self.speed)

        # Read the input csv file
        df_input = pd.read_csv(self.input_file_path)  # use the loaded file

        # Copy the parameters from the input csv file
        foot_data = df_input["foot"]
        tie_plate_width = df_input["tie_plate_width"]
        tie_plate_length = df_input["tie_plate_length"]
        tie_spacing = df_input["tie_spacing"]
        rail_section = df_input["rail_section"]
        alb_bending_stress = df_input["red_allowable_bending_stress"]
        yellow_bending_stress = df_input["yellow_allowable_bending_stress"]
        longitude = df_input["longitude"]
        latitude = df_input["latitude"]

        # Calculate tie plate area
        if (tie_plate_width != 0).all() and (tie_plate_length != 0).all():
            tie_plate_area = bending_moment_calculator.tie_plate_area(tie_plate_width, tie_plate_length)
        else:
            # handle case where either tie_plate_width or tie_plate_length contain zeros
            tie_plate_area = 0

        # Get rail section parameters
        # inertia_moment = [float(track_data['I']) for track_data in self.track.track_params if track_data['rail_section'] == rail_section]
        # rail_c = [float(track_data['c']) for track_data in self.track.track_params if track_data['rail_section'] == rail_section]
        
        # create a mapping from rail section to 'I' value
        inertia_moment_mapping = {track_data['rail_section']: float(track_data['I']) for track_data in self.track.track_params}

        # map the 'rail_section' column to corresponding 'I' values
        inertia_moment = rail_section.map(inertia_moment_mapping)

        # do the same for 'c' value
        rail_c_mapping = {track_data['rail_section']: float(track_data['c']) for track_data in self.track.track_params}
        rail_c = rail_section.map(rail_c_mapping)
        
        print("inertia_moment", inertia_moment)
        print("inertia_moment_mapping", inertia_moment_mapping)
        print("rail_c", rail_c)
        print("rail_c_mapping", rail_c_mapping)
        # Test for loading the csv file and pass the rail_c and inertia moment
        # with open('Rail_Section_Properties.json', 'r') as file:
        #     rail_props = json.load(file)

        # for row in rail_section:
        #     rail_section = int(row[0])

        #     if rail_section in rail_props:
        #         section_features = rail_section[rail_section]
        #         rail_c_value = section_features['rail_c']
        #         moment_of_inertia_value = section_features['inertia_moment']
        

        # Calculate dynamic parameters for each foot
        max_deflection = [bending_moment_calculator.max_dynamic_deflection(combined_values) for combined_values in combined_values_list]
        max_pressure = [bending_moment_calculator.max_dynamic_pressure(combined_values) for combined_values in combined_values_list]
        max_seat_force = [bending_moment_calculator.max_dynamic_railseat_force(max_pressure_val, tie_spacing_val) for max_pressure_val, tie_spacing_val in zip(max_pressure, tie_spacing)]
        
        # Required rail section modulus
        #req_section_modulus = [bending_moment_calculator.required_rail_seciton_modulus(inertia_moment_val, rail_c_value) for inertia_moment_val, rail_c_value in zip(inertia_moment, rail_c)]
        cal_section_modulus = [bending_moment_calculator.calculated_rail_section_modulus(max_bending_moment, alb_bending_stress_value) for max_bending_moment, alb_bending_stress_value in zip(max_bending_moments, alb_bending_stress)]

        # Create a new DataFrame to store the output data
        df_output = pd.DataFrame({
            "foot": foot_data,
            "max_bending_moment": max_bending_moments,
            "max_deflection": max_deflection,
            "max_pressure": max_pressure,
            "max_seat_force": max_seat_force,
            #"required_section_modulus": req_section_modulus,
            "calculated_section_modulus": cal_section_modulus,
            "longitude": longitude,
            "latitude": latitude
        })

        self.display_plot(max_bending_moments)

        # Write the output DataFrame to a CSV file
        #df_output.to_csv("/Users/mulinw/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/Courses/23spring/597/CSV_Version/Vitor_Version_Test/output1.csv", index=False)  # replace "output.csv" with your desired output file path
        # Open a dialog for the user to choose the output file path
        output_file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        # Check if a file path was chosen
        if output_file_path:
            # Write the output DataFrame to a CSV file
            df_output.to_csv(output_file_path, index=False)  # use the chosen output_file_path
            self.status_label['text'] = f"Output CSV saved successfully at {output_file_path}."
        else:
            self.status_label['text'] = "No output file selected."
        


    def display_plot(self, max_bending_moments):
        plt.figure(figsize=(6, 5), dpi=100)
        ax = plt.gca()

        red_threshold = 500000
        yellow_threshold = 400000

        # Add threshold lines
        ax.axhline(red_threshold, color='red', linestyle='--')
        ax.axhline(yellow_threshold, color='yellow', linestyle='--')

        # Split data into red, yellow, and green segments
        for i, max_bending_moment in enumerate(max_bending_moments):
            if max_bending_moment > red_threshold:
                color = 'red'
            elif max_bending_moment > yellow_threshold:
                color = 'yellow'
            else:
                color = 'green'

            if i < len(max_bending_moments) - 1:
                ax.plot([i, i + 1], [max_bending_moments[i], max_bending_moments[i + 1]], color=color)

        ax.set_xlabel('Foot')
        ax.set_ylabel('Max Bending Moment')
        ax.set_title('Max Bending Moment along Route')
        plt.show()


