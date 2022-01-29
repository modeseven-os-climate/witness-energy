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
from energy_models.core.techno_type.base_techno_models.electricity_techno import ElectricityTechno
from energy_models.core.stream_type.energy_models.methane import Methane
from energy_models.core.stream_type.carbon_models.carbon_capture import CarbonCapture


class CCGasT(ElectricityTechno):

    def compute_other_primary_energy_costs(self):
        """
        Compute primary costs which depends on the technology 
        """
        # Cost of methane for 1 kWH
        self.cost_details[Methane.name] = list(
            self.prices[Methane.name] * self.techno_infos_dict['methane_needs'])

        return self.cost_details[Methane.name]

    def compute_consumption_and_production(self):
        """
        Compute the consumption and the production of the technology for a given investment
        Maybe add efficiency in consumption computation ? 
        """

        self.compute_primary_energy_production()

        co2_prod = self.get_theoretical_co2_prod()
        self.production[f'{CarbonCapture.flue_gas_name} ({self.mass_unit})'] = co2_prod * \
            self.production[f'{ElectricityTechno.energy_name} ({self.product_energy_unit})']

        # Consumption
        self.consumption[f'{Methane.name} ({self.product_energy_unit})'] = self.techno_infos_dict['methane_needs'] * \
            self.production[f'{ElectricityTechno.energy_name} ({self.product_energy_unit})']

    def get_theoretical_co2_prod(self, unit='kg/kWh'):
        ''' 
        Get co2 needs in kg co2 /kWh 
        '''
        methane_data = Methane.data_energy_dict
        # kg of C02 per kg of methane burnt
        methane_co2 = methane_data['CO2_per_use']
        # Amount of methane in kwh for 1 kwh of elec
        methane_need = self.techno_infos_dict['methane_needs']
        calorific_value = methane_data['calorific_value']  # kWh/kg

        co2_prod = methane_co2 / calorific_value * methane_need
        return co2_prod