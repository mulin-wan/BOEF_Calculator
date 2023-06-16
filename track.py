# track.py
import csv
import json

class Track:
    def __init__(self):
        self.track_params = []

    def load_rail_section_properties(self):
        with open('Rail_Section_Properties.json', 'r') as file:
            self.rail_props = json.load(file)

    def load_track_parameters(self, filename):
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row = {**row, **self.get_rail_section_properties(row["rail_section"])}
                self.track_params.append(row)

    def get_rail_section_properties(self, rail_section):
        rail_properties = self.rail_props[rail_section]
        property_names = self.rail_props["@RailSectionProperties"].split(", ")
        return dict(zip(property_names, rail_properties))

    def clear_all(self): # New method to clear all data
        self.track_params = []
