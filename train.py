import json

class Train:
    def __init__(self, car_params):
        self.car_params = car_params
        self.train_sequence = []

    def add(self, car_name):
        self.train_sequence.append(self.car_params[car_name])

    def remove(self):
        if self.train_sequence:
            self.train_sequence.pop()

    def clear_all(self):
        self.train_sequence = []
    
    def couple(self, car1, car2):
        car1_data = car1
        car2_data = car2
        
        car1_last_half = car1_data["wheel_num"] // 2
        car2_first_half = car2_data["wheel_num"] // 2

        coupled_car = {
            "static_load_values": car1_data["static_load_values"][-car1_last_half:] + car2_data["static_load_values"][:car2_first_half],
            "diameter_values": car1_data["diameter_values"][-car1_last_half:] + car2_data["diameter_values"][:car2_first_half],
            "distance_values": car1_data["distance_values"][-(car1_last_half-1):] + [car1_data["coupler_lengths"][1] + car2_data["coupler_lengths"][0]] + car2_data["distance_values"][:(car2_first_half-1)],
            "wheel_num": car1_last_half + car2_first_half,
            "coupler_lengths": [car1_data["coupler_lengths"][0], car2_data["coupler_lengths"][1]]
        }

        return coupled_car