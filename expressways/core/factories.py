import factory as f
import factory.django as fdj
from django.contrib.auth.models import User

from .models import *

class UserFactory(fdj.DjangoModelFactory):
    class Meta:
        model = User

    class Params:
        superuser = f.Trait(
            username = 'test-admin',
            email = 'test-admin@xp.com',
        )

    username = f.Sequence('person{0}'.format)
    email = f.Sequence('person{0}@xpress.com'.format)
    password = f.PostGenerationMethodCall('set_password', '123P@s$w0rd')

class OccurrenceFactory(fdj.DjangoModelFactory):
    class Meta:
        model = Occurrence

    name = 'Debris in Road'
    
class SubOccurrenceFactory(fdj.DjangoModelFactory):
    class Meta:
        model = SubOccurrence

    name = 'Debris Block Lane'
    occurrence = f.SubFactory(OccurrenceFactory)

class DesignComponentFactory(fdj.DjangoModelFactory):
    class Meta:
        model = DesignComponent

    name = 'Traffic Officer Service'

class ConfigurationFactory(fdj.DjangoModelFactory):
    class Meta:
        model = OccurrenceConfiguration

    sub_occurrence = f.SubFactory(SubOccurrenceFactory)
    lane_closures = 'II'
    duration = 15
    flow = 300
    speed_limit = 70
    frequency = 30

class EffectInterventionFactory(fdj.DjangoModelFactory):
    class Meta:
        model = EffectIntervention

    design_component = f.SubFactory(DesignComponentFactory)
    configuration_effect = f.SubFactory(ConfigurationFactory)
    frequency_change = 30
    duration_change = 20
    justification = 'Test effect'

class ConfigWithEffectFactory(ConfigurationFactory):
    effect = f.RelatedFactory(
        EffectInterventionFactory, 
        'configuration_effect',
    )

class ConfigWithMultEffectsFactory(ConfigurationFactory):
    effect1 = f.RelatedFactory(
        EffectInterventionFactory, 
        'configuration_effect', 
        design_component__name='VMS'
    )
    effect2 = f.RelatedFactory(
        EffectInterventionFactory, 
        'configuration_effect', 
        design_component__name='Emergency Areas'
    )
