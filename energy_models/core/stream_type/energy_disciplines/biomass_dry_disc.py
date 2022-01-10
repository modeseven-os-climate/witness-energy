'''
Copyright 2022 Airbus SAS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from energy_models.core.stream_type.energy_disc import EnergyDiscipline
from energy_models.core.stream_type.energy_models.biomass_dry import BiomassDry
from sos_trades_core.tools.post_processing.charts.two_axes_instanciated_chart import InstanciatedSeries, \
    TwoAxesInstanciatedChart


class BiomassDryDiscipline(EnergyDiscipline):

    DESC_IN = {'technologies_list': {'type': 'string_list',
                                     'possible_values': ['ManagedWood', 'UnmanagedWood', 'CropEnergy'],
                                     'visibility': EnergyDiscipline.SHARED_VISIBILITY,
                                     'namespace': 'ns_biomass_dry',
                                     'structuring': True},
               'data_fuel_dict': {'type': 'dict', 'visibility': EnergyDiscipline.SHARED_VISIBILITY,
                                  'namespace': 'ns_biomass_dry', 'default': BiomassDry.data_energy_dict},
               }
    DESC_IN.update(EnergyDiscipline.DESC_IN)

    energy_name = BiomassDry.name

    DESC_OUT = EnergyDiscipline.DESC_OUT  # -- add specific techno outputs to this

    def init_execution(self):
        inputs_dict = self.get_sosdisc_inputs()
        self.energy_model = BiomassDry(self.energy_name)
        self.energy_model.configure_parameters(inputs_dict)

    def get_chart_co2_emissions(self):
        '''
        surcharged from EnergyDiscipline to have emissions from technology production
        '''
        new_charts = []
        chart_name = f'Comparison of CO2 emissions due to production and use of {self.energy_name} technologies'
        new_chart = TwoAxesInstanciatedChart(
            'years', 'CO2 emissions (Gt)', chart_name=chart_name, stacked_bar=True)

        technology_list = self.get_sosdisc_inputs('technologies_list')

        co2_per_use = self.get_sosdisc_outputs(
            'CO2_per_use')

        energy_production = self.get_sosdisc_outputs('energy_production')
        for technology in technology_list:
            techno_emissions = self.get_sosdisc_inputs(
                f'{technology}.CO2_emissions')
            techno_production = self.get_sosdisc_inputs(
                f'{technology}.techno_production')
            year_list = techno_emissions['years'].values.tolist()
            emission_list = techno_emissions[technology].values * \
                techno_production[f'{self.energy_name} ({BiomassDry.unit})'].values
            serie = InstanciatedSeries(
                year_list, emission_list.tolist(), technology, 'bar')
            new_chart.series.append(serie)
            # if there is a better way to know which technology is zero
            # emissions
            if technology == 'UnmanagedWood':
                co2_per_use = co2_per_use['CO2_per_use'].values * \
                    techno_production[f'{self.energy_name} ({BiomassDry.unit})'].values
        serie = InstanciatedSeries(
            year_list, co2_per_use.tolist(), 'CO2 from use of brut production', 'bar')
        new_chart.series.append(serie)
        new_charts.append(new_chart)

        return new_charts
