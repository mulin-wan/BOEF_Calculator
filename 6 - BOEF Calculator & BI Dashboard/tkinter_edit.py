# tkinter_edit.py
import matplotlib.pyplot as plt
import tkinter as tk
import pandas as pd
from tkinter import filedialog
from tkinter import ttk
from bending_moment import BendingMomentCalculator

class Application(tk.Frame):
    def __init__(self, master=None, train=None, track=None, calculator=None):
        super().__init__(master)
        self.master = master
        self.master.title("BOEF Calculator v2.0")  # set the window title here
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

    def calculate(self):
        bending_moment_calculator = BendingMomentCalculator(self.train, self.track)
        combined_values_list, max_bending_moments, max_bending_stress_list, tie_plate_area_list, req_section_modulus_list = bending_moment_calculator.calculate_max_bending_moments_along_route(self.speed)

        # Read the input csv file
        df_input = pd.read_csv(self.input_file_path)  # use the loaded file

        # Copy the parameters from the input csv file
        foot_data = df_input["foot"]
        section_id = df_input["SectionID"]
        tie_length = df_input["tie_length"]
        tie_width = df_input["tie_width"]
        tie_plate_width = df_input["tie_plate_width"]
        tie_plate_length = df_input["tie_plate_length"]
        tie_spacing = df_input["tie_spacing"]
        rail_section = df_input["rail_section"]
        alb_bending_stress = df_input["allowable_bending_stress"]
        alb_rail_tie_bearing_stress = df_input["allowable_rail/tie_bearing_stress"]
        alb_ballast_subgrade_stress = df_input["allowable_ballast/subgrade_stress"]
        longitude = df_input["longitude"]
        latitude = df_input["latitude"]
        actual_ballast_thickness = df_input["actual_ballast_thickness"]
        track = df_input["track"]
        side = df_input["rail_side"]
        track_modulus = df_input["track_modulus"]

        # Calculate dynamic parameters for each foot
        max_deflection = [bending_moment_calculator.max_dynamic_deflection(combined_values) for combined_values in combined_values_list]
        max_pressure = [bending_moment_calculator.max_dynamic_pressure(combined_values) for combined_values in combined_values_list]
        max_seat_force = [bending_moment_calculator.max_dynamic_railseat_force(max_pressure_val, tie_spacing_val) for max_pressure_val, tie_spacing_val in zip(max_pressure, tie_spacing)]
        
        # Calculated rail section modulus
        cal_section_modulus = [bending_moment_calculator.calculate_rail_section_modulus(max_bending_moment, alb_bending_stress_value) for max_bending_moment, alb_bending_stress_value in zip(max_bending_moments, alb_bending_stress)]
        req_tie_plate_size_nonlinear = [bending_moment_calculator.req_tie_plate_size_nonlinear(max_seat_force, alb_rail_tie_bearing_stress) for max_seat_force, alb_rail_tie_bearing_stress in zip(max_seat_force, alb_rail_tie_bearing_stress)]
        
        # Rail/Tie bearing stress
        cal_rail_tie_bearing_stress = [bending_moment_calculator.calculate_rail_tie_bearing_stress(max_seat_force, tie_plate_area_list) for max_seat_force, tie_plate_area_list in zip(max_seat_force, tie_plate_area_list)]
        nonlinear_rail_tie_bearing_stress = [bending_moment_calculator.non_linear_rail_tie_bearing_stress(max_seat_force, tie_plate_area_list) for max_seat_force, tie_plate_area_list in zip(max_seat_force, tie_plate_area_list)]
        
        # Tie/Ballast bearing stress
        cal_tie_ballast_bearing_stress = [bending_moment_calculator.calculated_tie_ballast_bearing_stress(max_seat_force, tie_length, tie_width) for max_seat_force, tie_length, tie_width in zip(max_seat_force, tie_length, tie_width)]
        
        # Ballast thickness
        min_cal_ballast_thickness = [bending_moment_calculator.mimimum_calculated_ballast_thickness(cal_tie_ballast_bearing_stress, alb_ballast_subgrade_stress) for cal_tie_ballast_bearing_stress, alb_ballast_subgrade_stress in zip(cal_tie_ballast_bearing_stress, alb_ballast_subgrade_stress)]
        
        # Ballast/Subgrade stress
        actual_ballast_stress = [bending_moment_calculator.actual_ballast_subgrade_stress(cal_tie_ballast_bearing_stress, actual_ballast_thickness) for cal_tie_ballast_bearing_stress, actual_ballast_thickness in zip(cal_tie_ballast_bearing_stress, min_cal_ballast_thickness)]
        
        # Create a new DataFrame to store the output data
        df_output = pd.DataFrame({
            "foot": foot_data,
            "SectionID": section_id,
            "rail_section": rail_section,
            "tie_spacing": tie_spacing,
            "tie_plate_width": tie_plate_width,
            "tie_plate_length": tie_plate_length,
            "tie_plate_area": tie_plate_area_list,
            "max_bending_moment": max_bending_moments,
            "max_bending_stress": max_bending_stress_list,
            "max_deflection": max_deflection,
            "max_pressure": max_pressure,
            "max_seat_force": max_seat_force,
            "required_rail_section_modulus": req_section_modulus_list,
            "calculated_section_modulus": cal_section_modulus,
            "calculated_rail/tie_bearing_stress": cal_rail_tie_bearing_stress,
            "non-linear_rail/tie_bearing_stress": nonlinear_rail_tie_bearing_stress,
            "required_tie_plate_size_nonlinear": req_tie_plate_size_nonlinear,
            "calculated_tie/ballast_bearing_stress": cal_tie_ballast_bearing_stress,
            "minimum_calculated_ballast_thickness": min_cal_ballast_thickness,
            "actual_ballast_thickness": actual_ballast_thickness, 
            "actual_ballast_stress": actual_ballast_stress,
            "longitude": longitude,
            "latitude": latitude,
            "track": track,
            "rail_side": side,
            "track_modulus": track_modulus
        })

        #self.display_plot(max_bending_moments)
        self.display_plot(max_bending_moments, foot_data)

        # Write the output DataFrame to a CSV file
        # Open a dialog for the user to choose the output file path
        output_file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        # Check if a file path was chosen
        if output_file_path:
            # Write the output DataFrame to a CSV file
            df_output.to_csv(output_file_path, index=False)  # use the chosen output_file_path
            self.status_label['text'] = f"Output CSV saved successfully at {output_file_path}."
        else:
            self.status_label['text'] = "No output file selected."


    def display_plot(self, max_bending_moments, foot_data):
        plt.figure(figsize=(6, 5), dpi=100)
        ax = plt.gca()

        red_threshold = 50000
        yellow_threshold = 30000

        # Add threshold lines
        ax.axhline(red_threshold, color=(1, 0, 0), linestyle='--')  # Red: RGB(255, 0, 0)
        ax.axhline(yellow_threshold, color=(1, 153/255, 0), linestyle='--')  # Yellow: RGB(255, 153, 0)

        # Convert foot_data into a list
        foot_data_list = foot_data.tolist()

        # Split data into red, yellow, and green segments
        for i, max_bending_moment in enumerate(max_bending_moments):
            if max_bending_moment > red_threshold:
                color = (1, 0, 0)  # Red: RGB(255, 0, 0)
            elif max_bending_moment > yellow_threshold:
                color = (1, 153/255, 0)  # Yellow: RGB(255, 153, 0)
            else:
                color = (36/255, 231/255, 128/255)  # Green: RGB(36, 231, 128)

            if i < len(max_bending_moments) - 1:
                ax.plot([foot_data_list[i], foot_data_list[i + 1]], [max_bending_moments[i], max_bending_moments[i + 1]], color=color)

        ax.set_xlabel('Foot')
        ax.set_ylabel('Max Bending Moment')
        ax.set_title('Max Bending Moment along Route')
        plt.show()
