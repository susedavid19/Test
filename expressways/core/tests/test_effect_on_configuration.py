from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

from expressways.core.factories import ConfigurationFactory, ConfigWithEffectFactory, ConfigWithMultEffectsFactory
from expressways.core.models import OccurrenceConfiguration, EffectIntervention

class TestEffectOnConfiguration(TestCase):
    def test_add_configuration_with_effect(self):
        """
        When occurrence configuration has defined effect intervention,
        it should be successfully saved into occurrenceConfiguration table and update effectIntervention table as well
        """
        self.assertEqual(OccurrenceConfiguration.objects.all().count(), 0)
        config = ConfigWithEffectFactory()
        self.assertEqual(OccurrenceConfiguration.objects.all().count(), 1)
        self.assertEqual(EffectIntervention.objects.all().count(), 1)
        effect = EffectIntervention.objects.first()
        self.assertEqual(effect.configuration_effect, config)

    def test_add_configuration_with_mult_effects(self):
        """
        When occurrence configuration has multiple interventions defined,
        it should be successfully saved into both occurrenceConfiguration and effectIntervention tables
        """
        self.assertEqual(OccurrenceConfiguration.objects.all().count(), 0)
        config_effects = ConfigWithMultEffectsFactory()
        self.assertEqual(OccurrenceConfiguration.objects.all().count(), 1)
        self.assertEqual(EffectIntervention.objects.all().count(), 2)
        self.assertEqual(EffectIntervention.objects.filter(design_component__name='VMS').count(), 1)
        self.assertEqual(EffectIntervention.objects.filter(design_component__name='Emergency Areas').count(), 1)

    def test_edit_existing_configuration(self):
        """
        Test type of effect field in current configuration
        """
        config = ConfigWithEffectFactory()
        effect = EffectIntervention.objects.get(configuration_effect=config)
        self.assertEqual(effect.frequency_change, 30)
        self.assertEqual(effect.duration_change, 20)
        self.assertEqual(effect.justification, 'Test effect')
        EffectIntervention.objects.filter(configuration_effect=config).update(frequency_change=-20)
        effect.refresh_from_db()
        self.assertEqual(effect.frequency_change, -20)
        EffectIntervention.objects.filter(configuration_effect=config).update(duration_change=-30)
        effect.refresh_from_db()
        self.assertEqual(effect.duration_change, -30)
        EffectIntervention.objects.filter(configuration_effect=config).update(duration_change=-150, frequency_change=-200)
        effect.refresh_from_db()
        try:
            effect.full_clean()
        except ValidationError as e:
            self.assertTrue('duration_change' in e.message_dict)
            self.assertTrue('frequency_change' in e.message_dict)

    def test_add_configuration_with_same_suboccurrence(self):
        """
        When there are multiple configurations with the same suboccurrence but not frequency value,
        both should be successfully saved into the occurrenceConfiguration table
        """
        self.assertEqual(OccurrenceConfiguration.objects.all().count(), 0)
        config1 = ConfigurationFactory(frequency=15)
        config2 = ConfigurationFactory(frequency=25)
        self.assertEqual(OccurrenceConfiguration.objects.all().count(), 2)
        self.assertEqual(OccurrenceConfiguration.objects.filter(sub_occurrence__name='Debris Block Lane', frequency=15).count(), 1)
        self.assertEqual(OccurrenceConfiguration.objects.filter(sub_occurrence__name='Debris Block Lane', frequency=25).count(), 1)
