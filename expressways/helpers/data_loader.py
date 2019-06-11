import pandas as pd   
from pandas import ExcelFile

from expressways.core.models import Road, Occurrence, SubOccurrence, OccurrenceConfiguration, DesignComponent, EffectIntervention

class DataLoader(object):
    @classmethod
    def load_to_configuration(self, filepath):
        df = pd.read_excel(filepath, sheet_name='Occurrence_Proforma_Upload')
        print(df.columns)
        print(df.index)
        Occurrence.objects.all().delete()
        SubOccurrence.objects.all().delete()
        OccurrenceConfiguration.objects.all().delete()
        # Reading through the rows
        for i in df.index:
            config = self.get_or_update_configuration(df.iloc[i])
            for component in DesignComponent.objects.values('name'):
                continue
                # self.add_intervention(config, component['name'], df.iloc[i])

        print('OCc count: ', OccurrenceConfiguration.objects.all().count())

    @classmethod
    def get_occurrence(self, name):
        obj, created = Occurrence.objects.get_or_create(name=name)
        return obj

    @classmethod
    def get_sub_occurrence(self, occurrence, name):
        obj, created = SubOccurrence.objects.get_or_create(
            name=name,
            defaults={'occurrence': occurrence}
        )
        return obj

    @classmethod
    def get_road(self):
        obj, created = Road.objects.get_or_create(
            name='Expressways Test Road'
        )
        return obj 

    @classmethod
    def get_or_update_configuration(self, data):
        occurrence = self.get_occurrence(data['Operational occurrence'])
        road = self.get_road()
        sub_occurrence = self.get_sub_occurrence(occurrence, data['Operational sub-occurrence'])
        lane_closures = data['TMCI:Lane(s) impacted or closed, incl. SMV/WCH?']
        flow = data['TMCI:Flow Level']
        speed_limit = data['TMCI:Speed (mph)']
        frequency = data['Baseline:Average frequency (per mile / year)']
        duration = data['Baseline:Duration (bin) of occurrence (based on average duration)']
        
        if (not pd.isnull(lane_closures) 
            and (not pd.isnull(flow)) 
            and (not pd.isnull(speed_limit))
            and (not pd.isnull(frequency))
            and (not pd.isnull(duration))
        ):
            obj, created = OccurrenceConfiguration.objects.get_or_create(
                road=road,
                sub_occurrence=sub_occurrence,
                lane_closures=lane_closures,
                flow=flow,
                speed_limit=speed_limit,
                frequency=frequency,
                duration=duration,
            )
            return obj

    @classmethod
    def get_design_component(self, name):
        obj = DesignComponent.objects.get(name=name)
        return obj

    @classmethod
    def add_intervention(self, config, component_name, data):
        if component_name == 'WCH & Slow Moving Vehicle Prohibition':
            component = self.get_design_component(component_name)
            freq_value = data['WCH:Impact Assumption:Frequency']
            freq_text = data['WCH:Evidence Source:Frequency']
            dur_value = data['WCH:Impact Assumption:Duration']
            dur_text = data['WCH:Evidence Source:Duration']
        elif component_name == 'Emergency Areas':
            component = self.get_design_component(component_name)
            freq_value = data['EA:Impact Assumption:Frequency']
            freq_text = data['EA:Evidence Source:Frequency']
            dur_value = data['EA:Impact Assumption:Duration']
            dur_text = data['EA:Evidence Source:Duration']
        elif component_name == 'Traffic Officer Service':
            component = self.get_design_component(component_name)
            freq_value = data['TOS:Impact Assumption:Frequency']
            freq_text = data['TOS:Evidence Source:Frequency']
            dur_value = data['TOS:Impact Assumption:Duration']
            dur_text = data['TOS:Evidence Source:Duration']
        elif component_name == 'VMS':
            component = self.get_design_component(component_name)
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