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

from energy_models.core.stream_type.ressources_models.methanol import Methanol
from energy_models.core.stream_type.energy_models.biodiesel import BioDiesel
from energy_models.core.stream_type.ressources_models.natural_oil import NaturalOil
from energy_models.core.techno_type.base_techno_models.biodiesel_techno import BioDieselTechno
from energy_models.core.stream_type.ressources_models.sodium_hydroxide import SodiumHydroxide
from energy_models.core.stream_type.ressources_models.potassium_hydroxide import PotassiumHydroxide
from energy_models.core.stream_type.ressources_models.water import Water
from energy_models.core.stream_type.energy_models.electricity import Electricity
from energy_models.core.stream_type.ressources_models.glycerol import Glycerol

import numpy as np


class Transesterification(BioDieselTechno):
    """Reaction: in Mt: 1.23 oil + 0.1 methanol = 1.22 biodiesel + 0.12 glycerol or
    in kg 1.0082 oil + 0.082 methanol = 1 biodiesel + 0.0984 glycerol"""

    def compute_other_primary_energy_costs(self):
        """
        Compute primary costs to produce 1kWh of biodiesel
        """
        # need in kg/kwh biodiesel
        self.cost_details[f'{Methanol.name}_needs'] = self.get_theoretical_methanol_needs(
        )
        # need in kg oil/kWh biodiesel
        self.cost_details[f'{NaturalOil.name}_needs'] = self.get_theoretical_natural_oil_needs(
        )
        # need in kg/kwh biodiesel
        self.cost_details[f'{SodiumHydroxide.name}_needs'] = self.get_theoretical_sodium_hydroxide_needs(
        )
        # need in kg/kwh biodiesel
        self.cost_details[f'{Water.name}_needs'] = self.get_theoretical_sodium_hydroxide_needs(
        )
        # need in kWh/kwh biodiesel
        self.cost_details[f'{Electricity.name}_needs'] = self.get_theoretical_electricity_needs(
        )

        # Cost of methanol for 1 kWH of biodiesel
        # $/kWh
        self.cost_details[f'{Methanol.name}'] = list(
            self.ressources_prices[f'{Methanol.name}'] * self.cost_details[f'{Methanol.name}_needs'] / self.cost_details['efficiency'])

        # Cost of natural oil for 1 kWH of biodiesel
        # $/kwh
        self.cost_details[f'{NaturalOil.name}'] = list(
            self.ressources_prices[f'{NaturalOil.name}'] * self.cost_details[f'{NaturalOil.name}_needs'] / self.cost_details['efficiency'])

        # Cost of sodium hydroxyde for 1 kWH of biodiesel
        # $/kwh
        # as potassium hydroxide can also be used, the price of the catalyst is the average of
        # potassium hydroxide and sodium hydroxide price
        catalyst_price = (self.ressources_prices[f'{SodiumHydroxide.name}'] +
                          self.ressources_prices[f'{PotassiumHydroxide.name}']) / 2
        self.cost_details[f'{SodiumHydroxide.name}'] = list(
            catalyst_price * self.cost_details[f'{SodiumHydroxide.name}_needs'] / self.cost_details['efficiency'])

        # Cost of 1kg of water for 1 kWH of biodiesel
        # $/kWh
        self.cost_details[f'{Water.name}'] = list(
            self.ressources_prices[f'{Water.name}'] * self.cost_details[f'{Water.name}_needs'] / self.cost_details['efficiency'])

        # Cost of electricity for 1 kWH of biodiesel
        self.cost_details[f'{Electricity.name}'] = list(
            self.prices[Electricity.name] * self.cost_details[f'{Electricity.name}_needs'] / self.cost_details['efficiency'])

        return self.cost_details[f'{Methanol.name}'] + self.cost_details[f'{NaturalOil.name}'] \
            + self.cost_details[f'{SodiumHydroxide.name}'] + self.cost_details[f'{Water.name}'] \
            + self.cost_details[f'{Electricity.name}']

    def grad_price_vs_energy_price(self):
        '''
        Compute the gradient of global price vs energy prices 
        Work also for total CO2_emissions vs energy CO2 emissions
        '''
        elec_needs = self.get_theoretical_electricity_needs(
        )
        efficiency = self.techno_infos_dict['efficiency']
        return {Electricity.name: np.identity(len(self.years)) * elec_needs / efficiency}

    def compute_consumption_and_production(self):
        """
        Compute the consumption and the production of the technology for a given investment
        Maybe add efficiency in consumption computation ?
        """

        self.compute_primary_energy_production()

        # Production
        self.production[f'{Glycerol.name} ({self.mass_unit})'] = 0.12 * self.production[f'{BioDiesel.name} ({self.product_energy_unit})'] / \
            self.data_energy_dict['calorific_value']

        # Consumption
        self.consumption[f'{Electricity.name} ({self.product_energy_unit})'] = self.cost_details[f'{Electricity.name}_needs'] * \
            self.production[f'{BioDiesel.name} ({self.product_energy_unit})'] / \
            self.cost_details['efficiency']  # in kWH
        self.consumption[f'{SodiumHydroxide.name} ({self.mass_unit})'] = self.cost_details[f'{SodiumHydroxide.name}_needs'] * \
            self.production[f'{BioDiesel.name} ({self.product_energy_unit})'] / \
            self.cost_details['efficiency']  # in kWH
        naturaloil_data = NaturalOil.data_energy_dict
        naturaloil_calorific_value = naturaloil_data['calorific_value']
        self.consumption[f'{NaturalOil.name} ({self.product_energy_unit})'] = self.cost_details[f'{NaturalOil.name}_needs'] * \
            self.production[f'{BioDiesel.name} ({self.product_energy_unit})'] * \
            naturaloil_calorific_value / self.cost_details['efficiency']

        self.consumption[f'{Methanol.name} ({self.mass_unit})'] = self.cost_details[f'{Methanol.name}_needs'] * \
            self.production[f'{BioDiesel.name} ({self.product_energy_unit})'] / \
            self.cost_details['efficiency']  # in kWH
        self.consumption[f'{Water.name} ({self.mass_unit})'] = self.cost_details[f'{Water.name}_needs'] * \
            self.production[f'{BioDiesel.name} ({self.product_energy_unit})'] / \
            self.cost_details['efficiency']  # in kWH

    def compute_CO2_emissions_from_input_ressources(self):
        '''
        Need to take into account  CO2 from electricity/fuel production
        '''

        self.carbon_emissions[f'{Electricity.name}'] = self.energy_CO2_emissions[f'{Electricity.name}'] * \
            self.cost_details[f'{Electricity.name}_needs'] / \
            self.cost_details['efficiency']

        self.carbon_emissions[SodiumHydroxide.name] = self.ressources_CO2_emissions[SodiumHydroxide.name] * \
            self.cost_details[f'{SodiumHydroxide.name}_needs'] / \
            self.cost_details['efficiency']

        self.carbon_emissions[f'{NaturalOil.name}'] = self.ressources_CO2_emissions[f'{NaturalOil.name}'] * \
            self.cost_details[f'{NaturalOil.name}_needs'] / \
            self.cost_details['efficiency']

        self.carbon_emissions[Methanol.name] = self.ressources_CO2_emissions[Methanol.name] * \
            self.cost_details[f'{Methanol.name}_needs'] / \
            self.cost_details['efficiency']

        return self.carbon_emissions[f'{Electricity.name}'] + self.carbon_emissions[SodiumHydroxide.name] + self.carbon_emissions[f'{NaturalOil.name}'] + self.carbon_emissions[Methanol.name]

    def get_theoretical_methanol_needs(self):
        """
        Get methanol needs in kg methanol / kWh biodiesel
        in kg 1.0082 oil + 0.082 methanol = 1 biodiesel + 0.0984 glycerol
        for 1kWh equivalent of biodiesel: 10.362 kg oil + 0.842 kg of methanol = 10.2778 kg of biodiesel + 1.0109 kg of glycerol
        """
        methanol_data = Methanol.data_energy_dict
        biodiesel_calorific_value = self.data_energy_dict['calorific_value']

        methanol_needs = 0.0819672311 / biodiesel_calorific_value

        return methanol_needs

    def get_theoretical_natural_oil_needs(self):
        """
        Get NaturalOil needs in kg oil /kWh biodiesel
        in kg 1.0082 oil + 0.082 NaturalOil = 1 biodiesel + 0.0984 glycerol
        for 1kWh equivalent of biodiesel: 10.362 kg oil + 0.842 kg of NaturalOil = 10.2778 kg of biodiesel + 1.0109 kg of glycerol
        """
        naturaloil_data = NaturalOil.data_energy_dict
        naturaloil_calorific_value = naturaloil_data['calorific_value']
        biodiesel_calorific_value = self.data_energy_dict['calorific_value']

        natural_oil_needs = 1.008196721 / biodiesel_calorific_value

        return natural_oil_needs

    def get_theoretical_sodium_hydroxide_needs(self):
        """
        Get SodiumHydroxide needs in kg SodiumHydroxide /kWh biodiesel
        in kg 1.0082 oil + 0.082 SodiumHydroxide = 1 biodiesel + 0.0984 glycerol
        for 1kWh equivalent of biodiesel: 10.362 kg oil + 0.842 kg of SodiumHydroxide = 10.2778 kg of biodiesel + 1.0109 kg of glycerol
        """
        naturaloil_data = SodiumHydroxide.data_energy_dict
        biodiesel_calorific_value = self.data_energy_dict['calorific_value']

        sodiumhydroxyde_needs = 0.01 / biodiesel_calorific_value

        return sodiumhydroxyde_needs

    def get_theoretical_water_needs(self):
        """
        Get water needs in kg water /kWh biodiesel
        in kg 1.0082 oil + 0.082 SodiumHydroxide = 1 biodiesel + 0.0984 glycerol
        for 1kWh equivalent of biodiesel: 10.362 kg oil + 0.842 kg of SodiumHydroxide = 10.2778 kg of biodiesel + 1.0109 kg of glycerol
        """
        water_data = SodiumHydroxide.data_energy_dict
        biodiesel_calorific_value = self.data_energy_dict['calorific_value']

        water_needs = 0.017 / biodiesel_calorific_value

        return water_needs

    def get_theoretical_electricity_needs(self):
        """
        Get electricity needs in kWh elec /kWh biodiesel
        in kg 1.0082 oil + 0.082 SodiumHydroxide +0.02kWh elec= 1 biodiesel + 0.0984 glycerol
        for 1kWh equivalent of biodiesel: 10.362 kg oil + 0.842 kg of SodiumHydroxide + = 10.2778 kg of biodiesel + 1.0109 kg of glycerol
        """
        biodiesel_calorific_value = self.data_energy_dict['calorific_value']

        elec_needs = 0.02 / biodiesel_calorific_value

        return elec_needs