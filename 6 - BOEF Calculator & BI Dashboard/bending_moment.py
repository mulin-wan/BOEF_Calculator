# bending_moment.py
from train import Train
import numpy as np

# The BendingMomentCalculator class is used to calculate the maximum bending moments along a given route.
class BendingMomentCalculator:
    # The class is initialized with a Train object and a Track object.
    def __init__(self, train, track):
        self.train = train
        self.track = track

    def calculate_max_bending_moments_along_route(self, speed):
        track = self.track.track_params
        _, max_configuration = self.get_max_configuration(self.train, track, speed)

        max_bending_moments = []
        dynamic_loads = []
        wheel_params_list = []
        combined_values_list = []
        max_bending_stress_list = []
        tie_plate_area_list = []
        req_section_modulus_list = []

        for foot_data in track:
            dynamic_load, wheel_params, combined_values, bending_moment, bending_stress = self.calculate_bending_moment(max_configuration, foot_data, speed)
            tie_plate_area = self.tie_plate_area(foot_data)
            req_section_modulus = self.required_rail_seciton_modulus(foot_data)

            max_bending_moments.append(bending_moment)
            dynamic_loads.append(dynamic_load)
            wheel_params_list.append(wheel_params)
            combined_values_list.append(combined_values)
            max_bending_stress_list.append(bending_stress)
            tie_plate_area_list.append(tie_plate_area)
            req_section_modulus_list.append(req_section_modulus)

        # return dynamic_loads, wheel_params_list, combined_values_list, max_bending_moments, max_bending_stress_list, tie_plate_area_list, req_section_modulus_list
        return combined_values_list, max_bending_moments, max_bending_stress_list, tie_plate_area_list, req_section_modulus_list


    # This function calculates the maximum bending moment and the corresponding configuration by the first foot data.
    def get_max_configuration(self, train, track, speed):
        try:
            train_sequence = train.train_sequence
            max_bending_moment = -1  
            max_configuration = None

            for i in range(len(train_sequence)):
                _, _, _, bending_moment, _, = self.calculate_bending_moment(train_sequence[i], track[0], speed)

                if bending_moment > max_bending_moment:
                    max_bending_moment = bending_moment
                    max_configuration = train_sequence[i]

                if i != len(train_sequence) - 1:
                    coupled_car = self.train.couple(train_sequence[i], train_sequence[i+1])
                    _, _, _, bending_moment, _, = self.calculate_bending_moment(train_sequence[i], track[0], speed)

                    if bending_moment > max_bending_moment:
                        max_bending_moment = bending_moment
                        max_configuration = coupled_car
        except (TypeError, KeyError, ZeroDivisionError):
            return None, None

        return max_bending_moment, max_configuration

    # This function calculates the maximum bending moment for a given car, foot data, and speed.
    def calculate_bending_moment(self, car, foot_data, speed):
        try:
            x = self.create_x_array()
            theta = self.calculate_theta(car, speed)
            dynamic_load = self.calculate_dynamic_load(car, theta)
            wheel_params, I, c = self.calculate_wheel_params(car, dynamic_load, foot_data, x)
            combined_values = self.calculate_combined_values(wheel_params)
            max_bending_moment = self.calculate_max_bending_moment(combined_values)
            max_bending_stress = self.calculate_bending_stress(max_bending_moment, c, I)
        except(TypeError, KeyError, ZeroDivisionError):
            # Return a tuple of None values instead of a single None
            return None, None, None, None, None

        return dynamic_load, wheel_params, combined_values, max_bending_moment, max_bending_stress

    
#From now on we calculater all the needed parameters

    # This function extracts the parameters from the foot data.
    def get_parameters_from_foot_data(self, foot_data):
        parameters = {
            'track_modulus': None if foot_data['track_modulus'].strip() == '' else float(foot_data['track_modulus']),
            'rail_section': None if foot_data['rail_section'].strip() == '' else float(foot_data['rail_section']),
            'elasticity': None if foot_data['elasticity'].strip() == '' else float(foot_data['elasticity']),
            'tie_spacing': None if foot_data['tie_spacing'].strip() == '' else float(foot_data['tie_spacing']),
            'tie_width': None if foot_data['tie_width'].strip() == '' else float(foot_data['tie_width']),
            'tie_thickness': None if foot_data['tie_thickness'].strip() == '' else float(foot_data['tie_thickness']),
            'tie_length': None if foot_data['tie_length'].strip() == '' else float(foot_data['tie_length']),
            'tie_plate_width': None if foot_data['tie_plate_width'].strip() == '' else float(foot_data['tie_plate_width']),
            'tie_plate_length': None if foot_data['tie_plate_length'].strip() == '' else float(foot_data['tie_plate_length']),
            'inertia_moment': None if foot_data['I'] == '' else foot_data['I'],
            'zhead': None if foot_data['Zhead'] == '' else foot_data['Zhead'],
            'zbase': None if foot_data['Zbase'] == '' else foot_data['Zbase'],
            'c': None if foot_data['c'] == '' else foot_data['c']
        }
        return parameters


    # This function calculates the wheel rotation speed.
    def calculate_theta(self, car, speed):
        try:
            wheel_num = int(float(car['wheel_num']))
            theta = []
            for i in range(wheel_num):
                if float(car['diameter_values'][i]):
                    theta.append((33*speed) / (100*float(car['diameter_values'][i])))
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return theta

    # This function calculates the dynamic load on each wheel.
    def calculate_dynamic_load(self, car, theta):
        try:
            wheel_num = int(float(car['wheel_num']))
            dynamic_load = np.zeros(wheel_num)
            for i in range(wheel_num):
                if float(car['diameter_values'][i]):
                    dynamic_load[i] = int(float(car['static_load_values'][i]) + theta[i]*float(car['static_load_values'][i])) 
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return dynamic_load

    # This function calculates the parameters for each wheel based on the dynamic load and foot data.
    def calculate_wheel_params(self, car, dynamic_load, foot_data, x):
        try:
            parameters = self.get_parameters_from_foot_data(foot_data)
            track_modulus = parameters['track_modulus']
            elasticity = parameters['elasticity']
            inertia_moment = parameters['inertia_moment']
            rail_c = parameters['c']
            beta = (track_modulus / (4*elasticity*inertia_moment))**0.25

            wheel_num = int(float(car['wheel_num']))
            x_length = len(x)
            wheel_params = np.zeros((wheel_num, 3, x_length))

            cumulative_distance = 0
            for i in range(wheel_num):
                if i > 0:
                    cumulative_distance += car['distance_values'][i - 1]
                distance = cumulative_distance
                cosine = np.cos(beta * np.abs(x - distance))
                sine = np.sin(beta * np.abs(x - distance))
                wheel_params[i, 0, :] = (dynamic_load[i] * ((elasticity * inertia_moment) / (64 * track_modulus)) ** 0.25 * np.exp(-1 * beta * np.abs(x - distance)) * (cosine - sine))  # M
                wheel_params[i, 1, :] = (dynamic_load[i] / (8 * elasticity * inertia_moment * beta ** 3) * np.exp(-1 * beta * np.abs(x - distance)) * (cosine + sine))  # w
                wheel_params[i, 2, :] = ((-1 * track_modulus * dynamic_load[i]) / (8 * elasticity * inertia_moment * beta ** 3) * np.exp(-1 * beta * np.abs(x - distance)) * (cosine + sine))  # p
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return wheel_params, inertia_moment, rail_c

    # This function sums up the parameters for all wheels to get the combined values.
    def calculate_combined_values(self, wheel_params):
        try:
            x_length = wheel_params.shape[2]
            combined_values = np.zeros((3, x_length))
        
            for i in range(3):
                combined_values[i, :] = wheel_params[:, i, :].sum(axis=0)
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return combined_values

    # This function finds the maximum bending moment from the combined values.
    def calculate_max_bending_moment(self, combined_values):
        try:
            max_bending_moment = np.max([np.abs(np.min(combined_values[0, :])), np.max(combined_values[0, :])])
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return float(max_bending_moment)

    # This function calculates the bending stress from the max bending moment results.
    def calculate_bending_stress(self, max_bending_moment, rail_c, inertia_moment):
        try:
            cal_bending_stress = np.round((max_bending_moment * rail_c) / inertia_moment)
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return cal_bending_stress
    
    # This function creates an array for the x values.
    def create_x_array(self, x_start=0, x_interval=0.5, x_length=3100):
        try:
            x = np.arange(x_start, x_start + x_interval * x_length, x_interval)
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return x

    # This function calculates the area of the tie plate.
    def tie_plate_area(self, foot_data):
        try:
            parameters = self.get_parameters_from_foot_data(foot_data)
            tie_plate_length = parameters["tie_plate_length"]
            tie_plate_width = parameters["tie_plate_width"]
            tie_plate_area = tie_plate_length * tie_plate_width
        except(TypeError, KeyError, ZeroDivisionError):
            return None

        return tie_plate_area

    def max_dynamic_deflection(self, combined_values):
        try:
            max_deflection = np.round(float(np.max(combined_values[1,:])), 3)
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return max_deflection

    # This function calculates the maximum dynamic pressure.
    def max_dynamic_pressure(self, combined_values):
        try:
            max_pressure = np.round(np.max([np.abs(np.min(combined_values[2,:])), np.max(combined_values[2,:])]))
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return max_pressure

    # This function calculates the maximum dynamic rail seat force.
    def max_dynamic_railseat_force(self, max_pressure, tie_spacing):
        try:
            max_seat_force = np.round(max_pressure * tie_spacing)
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return max_seat_force

    # This function calculates the required rail section modulus.
    def required_rail_seciton_modulus(self, foot_data):
        try:
            parameters = self.get_parameters_from_foot_data(foot_data)
            inertia_moment = parameters["inertia_moment"]
            rail_c = parameters["c"]
            req_section_modulus = np.round(inertia_moment / rail_c, 2)
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return req_section_modulus

    # This function calculates the rail section modulus from the max bending moment results.
    def calculate_rail_section_modulus(self, max_bending_moment, alb_bending_stress):
        try:
            cal_section_modulus = np.round(max_bending_moment / alb_bending_stress, 2)
        except(TypeError, KeyError, ZeroDivisionError):
            return None        
        return cal_section_modulus

    # This function calculates the rail-tie bearing stress.
    def calculate_rail_tie_bearing_stress(self, max_seat_force, tie_plate_area):
        try:
            cal_tie_bearing_stress = np.round(max_seat_force / tie_plate_area, 2)
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return cal_tie_bearing_stress

    # This function calculates the nonlinear rail-tie bearing stress.
    def non_linear_rail_tie_bearing_stress(self, max_seat_force, tie_plate_area):
        try:
            nonlinear_tie_bearing_stress = np.round((1.5 * max_seat_force) / tie_plate_area, 2)
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return nonlinear_tie_bearing_stress

    # This function calculates required tie plate size
    def req_tie_plate_size_nonlinear(self, max_seat_force, alb_tie_bearing_stress):
        try:
            req_plate_size_nonlinear = np.round((1.5 * max_seat_force) / alb_tie_bearing_stress, 2)
        except(TypeError, KeyError, ZeroDivisionError):
            return None        
        return req_plate_size_nonlinear

    # This function calculates tie-ballast bearing stress
    def calculated_tie_ballast_bearing_stress(self, max_seat_force, tie_length, tie_width):
        try:
            cal_ballast_bearing_stress = np.round((1.5 * max_seat_force) / ((tie_length/3) * tie_width), 2)
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return cal_ballast_bearing_stress

    def mimimum_calculated_ballast_thickness(self, cal_ballast_bearing_stress, alb_ballast_stress):
        try:
            min_ballast_thickness = np.round(((16.8 * cal_ballast_bearing_stress) / alb_ballast_stress) ** 0.8, 2)
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return min_ballast_thickness

    def actual_ballast_subgrade_stress(self, cal_ballast_bearing_stress, actual_ballast_thickness):
        try:
            actual_ballast_stress = np.round((16.8 * cal_ballast_bearing_stress) / actual_ballast_thickness ** 1.25, 2)
        except(TypeError, KeyError, ZeroDivisionError):
            return None
        return actual_ballast_stress