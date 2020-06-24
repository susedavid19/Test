import pandas as pd
from pandas import ExcelFile

from expressways.core.models import *

PROFORMA_COLUMN = {
    'Operational occurrence': 2,
    'Operational sub-occurrence': 4,
    'Incidents cleared': 6,
    'Lane closure': 7,
    'Flow level': 8,
    'Speed': 10,
    'Frequency': 11,
    'Duration': 12,
    'References': 14,
    'WCH & Slow Moving Vehicle Prohibition': 15,
    'Emergency Areas': 19,
    'Traffic Officer Service': 23,
    'VMS': 27,
}

PROCESSED_DESIGN_COMPONENTS = [
    'WCH & Slow Moving Vehicle Prohibition',
    'Emergency Areas',
    'Traffic Officer Service',
    'VMS'
]

class DataLoader:
    def __init__(self, output_file, road_name):
        '''
        Initialise the data loader with new log file if supplied
        '''
        if output_file:
            self.log_required = True
            self.output_file = open(output_file, 'w+')
        else:
            self.log_required = False

        self.road_name = road_name
        self.error_raised = False

    def log_output(self, msg, err=False):
        '''
        Write the log message to the output file specified if log is required
        '''
        if self.log_required:
            self.output_file.write(msg)
        if err:
            self.error_raised = True

    def load_to_configuration(self, file_path, sheet_name, skiprows, header):
        '''
        Main method to read through excel file supplied and process the data within.
        '''
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skiprows, header=header)
        recs_created = 0
        self.log_output(f'Processing {sheet_name} sheet of file{file_path}\n{"-"*50}')

        # Reading through the rows
        for index, row in df.iterrows():
            # Check configuration completion status; if complete, proceed to setup the configuration
            if row[0] == 'Complete':
                config, created = self.get_or_update_configuration(row, index + 5)
                if created:
                    # If new configuration is added, proceed to setup related design components intervention
                    for component in PROCESSED_DESIGN_COMPONENTS:
                        self.add_intervention(config, component, row, index + 5)
                    recs_created += 1
            # Print out progress dot to screen
            if index % 10 == 0:
                print('.', end='', flush=True)

        self.log_output(f'\n{"-"*50}\nRecords added: {recs_created}\n')

        if self.error_raised:
            raise Exception('Invalid data detected. Check output log if available.')
        
        if self.log_required:
            self.output_file.close()

    def get_occurrence(self, name):
        '''
        Retrieve occurrence if exist under provided name; otherwise create new
        '''
        obj, created = Occurrence.objects.get_or_create(name=name)
        return obj

    def get_sub_occurrence(self, occurrence, name):
        '''
        Retrieve sub occurrence if exist under provided occurrence and name; otherwise create new
        '''
        obj, created = SubOccurrence.objects.get_or_create(
            name=name,
            defaults={'occurrence': occurrence}
        )
        return obj

    def get_road(self, name):
        '''
        Retrieve road if exist under provided name; otherwise create new
        '''
        obj, created = Road.objects.get_or_create(
            name=name
        )
        return obj 

    def format_frequency(self, value):
        '''
        Format frequency value to integer if not null
        '''
        if pd.isnull(value):
            return 0
        else:
            return int(value)

    def format_incidents_cleared(self, value):
        '''
        Format incidents cleared value to right boolean
        '''
        if value == 'Yes':
            return True
        else:
            return False

    def get_or_update_configuration(self, data, row_idx):
        '''
        Retrieve occurrence configuration if exist under provided data in particular row; otherwise create new
        '''
        occurrence = self.get_occurrence(data[PROFORMA_COLUMN['Operational occurrence']])
        road = self.get_road(self.road_name)
        sub_occurrence = self.get_sub_occurrence(occurrence, data[PROFORMA_COLUMN['Operational sub-occurrence']])
        lane_closures = data[PROFORMA_COLUMN['Lane closure']]
        flow = data[PROFORMA_COLUMN['Flow level']]
        speed_limit = data[PROFORMA_COLUMN['Speed']]
        duration = data[PROFORMA_COLUMN['Duration']]
        frequency = self.format_frequency(data[PROFORMA_COLUMN['Frequency']])
        incidents_cleared = self.format_incidents_cleared(data[PROFORMA_COLUMN['Incidents cleared']])
        references = data[PROFORMA_COLUMN['References']]
        
        if (pd.isnull(lane_closures) or lane_closures not in dict(LANE_CHOICES)):
            self.log_output(f'\nRow {row_idx}: Lane closure value [Col: {PROFORMA_COLUMN["Lane closure"]}] ({lane_closures}) is invalid', True)
        elif (pd.isnull(flow) or flow not in dict(FLOW_CHOICES)):
            self.log_output(f'\nRow {row_idx}: Flow value [Col: {PROFORMA_COLUMN["Flow level"]}] ({flow}) is invalid', True)
        elif (pd.isnull(speed_limit) or speed_limit not in dict(SPEED_CHOICES)):
            self.log_output(f'\nRow {row_idx}: Speed limit value [Col: {PROFORMA_COLUMN["Speed"]}] ({speed_limit}) is invalid', True)
        elif (pd.isnull(duration) or duration not in dict(DURATION_CHOICES)):
            self.log_output(f'\nRow {row_idx}: Duration value [Col: {PROFORMA_COLUMN["Duration"]}] ({duration}) is invalid', True)
        else:
            obj, created = OccurrenceConfiguration.objects.get_or_create(
                road=road,
                sub_occurrence=sub_occurrence,
                lane_closures=lane_closures,
                flow=flow,
                speed_limit=int(speed_limit),
                duration=float(duration),
                frequency=frequency,
                incidents_cleared=incidents_cleared,
                references=references,
            )

            if not created:
                self.log_output(f'\nRow {row_idx}: Item already exist (object id: {obj.id})')

            return obj, created

        return {}, False

    def get_design_component(self, name):
        '''
        Retrieve design component if exist under provided name; otherwise create new
        '''
        obj, created = DesignComponent.objects.get_or_create(name=name)
        return obj

    def format_justification(self, freq_text, dur_text):
        '''
        Combine both frequency and duration justification texts into single field value, if value exist
        '''
        justification = ''
        if freq_text:
            justification += f'For frequency change: {freq_text}'
        if dur_text:
            justification += f'\nFor duration change: {dur_text}'
        return justification

    def format_change_value(self, value):
        '''
        Format duration or frequency change value to required format if valid
        '''
        if value == 'N/A':
            return 0
        else:
            return float(value) * 100

    def add_intervention(self, config, component_name, data, idx):
        '''
        Retrieve design component intervention if exist under provided name, configuration and data in particular row; 
        otherwise create new
        '''
        component = self.get_design_component(component_name)
        comp_idx = PROFORMA_COLUMN[component_name]
        freq_value = self.format_change_value(data[comp_idx])
        dur_value = self.format_change_value(data[comp_idx + 1])
        freq_text = data[comp_idx + 2]
        dur_text = data[comp_idx + 3]
        
        if (freq_value != 0 or dur_value != 0):
            obj, created = EffectIntervention.objects.get_or_create(
                design_component=component,
                configuration_effect=config,
                frequency_change=int(freq_value),
                duration_change=int(dur_value),
                justification=self.format_justification(freq_text, dur_text)
            )
            return obj
