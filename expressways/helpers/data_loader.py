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
    'Frequency': 13
}

class DataLoader:
    @classmethod
    def load_to_configuration(cls, file_path, sheet_name, *args, **kwargs):
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1, header=2)
        recs_created = 0

        # Reading through the rows
        for index, row in df.iterrows():
            # Check configuration completion status
            if row[0] == 'Complete':
                config, created = cls.get_or_update_configuration(row, index)
                if created:
                    recs_created += 1
        #     for component in DesignComponent.objects.values('name'):
        #         continue
                # self.add_intervention(config, component['name'], df.iloc[i])

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
                duration=int(duration),
                frequency=frequency,
                incidents_cleared=incidents_cleared
            )
            #if not created:
                #print(f'X -> {obj.sub_occurrence.name} {row_idx}')
            return obj, created

        else:
            return {}, False

    @classmethod
    def get_design_component(cls, name):
        obj = DesignComponent.objects.get(name=name)
        return obj

    @classmethod
    def add_intervention(cls, config, component_name, data):
        if component_name == 'WCH & Slow Moving Vehicle Prohibition':
            component = cls.get_design_component(component_name)
            freq_value = data['WCH:Impact Assumption:Frequency']
            freq_text = data['WCH:Evidence Source:Frequency']
            dur_value = data['WCH:Impact Assumption:Duration']
            dur_text = data['WCH:Evidence Source:Duration']
        elif component_name == 'Emergency Areas':
            component = cls.get_design_component(component_name)
            freq_value = data['EA:Impact Assumption:Frequency']
            freq_text = data['EA:Evidence Source:Frequency']
            dur_value = data['EA:Impact Assumption:Duration']
            dur_text = data['EA:Evidence Source:Duration']
        elif component_name == 'Traffic Officer Service':
            component = cls.get_design_component(component_name)
            freq_value = data['TOS:Impact Assumption:Frequency']
            freq_text = data['TOS:Evidence Source:Frequency']
            dur_value = data['TOS:Impact Assumption:Duration']
            dur_text = data['TOS:Evidence Source:Duration']
        elif component_name == 'VMS':
            component = cls.get_design_component(component_name)
            freq_value = data['VMS:Impact Assumption:Frequency']
            freq_text = data['VMS:Evidence Source:Frequency']
            dur_value = data['VMS:Impact Assumption:Duration']
            dur_text = data['VMS:Evidence Source:Duration']

        if (component
            and not pd.isnull(freq_value) 
            and (not pd.isnull(dur_value)) 
        ):
            obj, created = EffectIntervention.objects.get_or_create(
                design_component=component,
                configuration_effect=config,
                frequency_change=freq_value,
                duration_change=dur_value,
                justification=freq_text
            )
            return obj