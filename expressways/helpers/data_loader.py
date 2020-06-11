import pandas as pd
from pandas import ExcelFile

from expressways.core.models import Road, Occurrence, SubOccurrence, OccurrenceConfiguration, DesignComponent, EffectIntervention

PROFORMA_COLUMN = {
    'Operational occurrence': 2,
    'Operational sub-occurrence': 4,
    'Incidents cleared': 6,
    'Lane closure': 7,
    'Flow level': 8,
    'Speed': 10,
    'Duration': 12,
    'Frequency': 13,
    'WCH & Slow Moving Vehicle Prohibition': 15,
    'Emergency Areas': 19,
    'Traffic Officer Service': 23,
    'VMS': 27,
}

class DataLoader:
    @classmethod
    def load_to_configuration(cls, file_path, sheet_name, *args, **kwargs):
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1, header=2)
        recs_created = 0

        OccurrenceConfiguration.objects.all().delete()
        EffectIntervention.objects.all().delete()

        # Reading through the rows
        for index, row in df.iterrows():
            # Check configuration completion status
            if row[0] == 'Complete':
                config, created = cls.get_or_update_configuration(row, index)
                if created:
                    for component in DesignComponent.objects.values('name'):
                        cls.add_intervention(config, component['name'], row, index + 5)
                    recs_created += 1

        print('Records added: ', recs_created)

    @classmethod
    def get_occurrence(cls, name):
        obj, created = Occurrence.objects.get_or_create(name=name)
        return obj

    @classmethod
    def get_sub_occurrence(cls, occurrence, name):
        obj, created = SubOccurrence.objects.get_or_create(
            name=name,
            defaults={'occurrence': occurrence}
        )
        return obj

    @classmethod
    def get_road(cls):
        obj, created = Road.objects.get_or_create(
            name='Expressways Test Road'
        )
        return obj 

    @classmethod
    def format_frequency(cls, value):
        if pd.isnull(value):
            return 0
        else:
            return int(value)

    @classmethod
    def format_incidents_cleared(cls, value):
        if value == 'Yes':
            return True
        else:
            return False

    @classmethod
    def get_or_update_configuration(cls, data, row_idx):
        occurrence = cls.get_occurrence(data[PROFORMA_COLUMN['Operational occurrence']])
        road = cls.get_road()
        sub_occurrence = cls.get_sub_occurrence(occurrence, data[PROFORMA_COLUMN['Operational sub-occurrence']])
        lane_closures = data[PROFORMA_COLUMN['Lane closure']]
        flow = data[PROFORMA_COLUMN['Flow level']]
        speed_limit = data[PROFORMA_COLUMN['Speed']]
        duration = data[PROFORMA_COLUMN['Duration']]
        frequency = cls.format_frequency(data[PROFORMA_COLUMN['Frequency']])
        incidents_cleared = cls.format_incidents_cleared(data[PROFORMA_COLUMN['Incidents cleared']])
        
        if (not pd.isnull(lane_closures) 
            and (not pd.isnull(flow)) 
            and (not pd.isnull(speed_limit))
            and (not pd.isnull(duration))
        ):
            obj, created = OccurrenceConfiguration.objects.get_or_create(
                road=road,
                sub_occurrence=sub_occurrence,
                lane_closures=lane_closures,
                flow=flow,
                speed_limit=int(speed_limit),
                duration=float(duration),
                frequency=frequency,
                incidents_cleared=incidents_cleared
            )

            return obj, created

        else:
            return {}, False

    @classmethod
    def get_design_component(cls, name):
        obj = DesignComponent.objects.get(name=name)
        return obj

    @classmethod
    def format_justification(cls, freq_text, dur_text):
        justification = ''
        if freq_text:
            justification += f'For frequency change: {freq_text}'
        if dur_text:
            justification += f'\nFor duration change: {dur_text}'
        return justification

    @classmethod
    def format_change_value(cls, value):
        if value == 'N/A':
            return 0
        else:
            return float(value) * 100

    @classmethod
    def add_intervention(cls, config, component_name, data, idx):
        component = cls.get_design_component(component_name)
        comp_idx = PROFORMA_COLUMN[component_name]
        freq_value = cls.format_change_value(data[comp_idx])
        dur_value = cls.format_change_value(data[comp_idx + 1])
        freq_text = data[comp_idx + 2]
        dur_text = data[comp_idx + 3]
        
        if (freq_value != 0 or dur_value != 0):
            obj, created = EffectIntervention.objects.get_or_create(
                design_component=component,
                configuration_effect=config,
                frequency_change=int(freq_value),
                duration_change=int(dur_value),
                justification=cls.format_justification(freq_text, dur_text)
            )
            return obj
