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

import pandas as pd
import numpy as np

from energy_models.core.techno_type.disciplines.solid_fuel_techno_disc import SolidFuelTechnoDiscipline
from energy_models.models.solid_fuel.pelletizing.pelletizing import Pelletizing


class PelletizingDiscipline(SolidFuelTechnoDiscipline):

    techno_name = 'Pelletizing'
    # Wang, Y., Li, G., Liu, Z., Cui, P., Zhu, Z. and Yang, S., 2019.
    # Techno-economic analysis of biomass-to-hydrogen process in comparison with coal-to-hydrogen process.
    # Energy, 185, pp.1063-1075.
    # Rosenfeld, D.C., B�hm, H., Lindorfer, J. and Lehner, M., 2020.
    # Scenario analysis of implementing a power-to-gas and biomass gasification system in an integrated steel plant:
    # A techno-economic and environmental study. Renewable energy, 147,
    # pp.1511-1524.
    lifetime = 25  # Wang2019 Rosenfeld2020 says 20
    construction_delay = 3  # years
    techno_infos_dict_default = {'maturity': 5,
                                 'Opex_percentage': 0.0625,
                                 # production of CO2 in kg per kg of pellets
                                 # Wiley, A., 2009. Energy and Carbon Balance in Wood Pellet Manufacture.
                                 # Hunt, Guillot and Associates, Ruston,
                                 # Louisiana. https://www. hga-llc.
                                 # com/images/2014.
                                 'CO2_from_production': 0.116,
                                 'CO2_from_production_unit': 'kg/kg',
                                 # electricity to product 1kg of pellets
                                 'elec_demand': 0.1062,
                                 'elec_demand_unit': 'kWh/kg',
                                 'WACC': 0.01,
                                 'learning_rate':  0.2,
                                 'lifetime': lifetime,  # for now constant in time but should increase with time
                                 'lifetime_unit': 'years',
                                 # Capex in $
                                 'Capex_init': 29287037.04,
                                 'Capex_init_unit': 'euro',
                                 'full_load_hours': 8000.0,
                                 'euro_dollar': 1.08,
                                 'available_power': 400000000,  # 400000 ton/year
                                 'available_power_unit': 'kg/year',
                                 'efficiency': 0.85,  # boiler efficiency
                                 'techno_evo_eff': 'no',  # yes or no
                                 'construction_delay': construction_delay}
    # We do not invest on biomass gasification yet
    invest_before_year_start = pd.DataFrame(
        {'past years': np.arange(-construction_delay, 0), 'invest': [7.6745661, 8.9729523, 104.91]})
    # initial production : 45,21 million tonnes => x calorific value and
    # conversion in TWh
    initial_production = 217.04
    initial_age_distribution = pd.DataFrame({'age': np.arange(1, lifetime),
                                             'distrib': [10.39, 11.93, 1.13, 7.97, 7.14,
                                                         6.4, 5.73, 11.66, 11.66, 0.89,
                                                         0.89, 3.55, 3.55, 4.56, 2.53,
                                                         2.53, 1.27, 0.63, 0.63, 1.01,
                                                         1.01, 1.01, 1.01, 0.92]})

    DESC_IN = {'techno_infos_dict': {'type': 'dict',
                                     'default': techno_infos_dict_default},
               'initial_production': {'type': 'float', 'unit': 'TWh', 'default': initial_production},
               'initial_age_distrib': {'type': 'dataframe', 'unit': '%', 'default': initial_age_distribution},
               'invest_before_ystart': {'type': 'dataframe', 'unit': 'G$', 'default': invest_before_year_start,
                                        'dataframe_descriptor': {'past years': ('int',  [-20, -1], False),
                                                                 'invest': ('float',  None, True)},
                                        'dataframe_edition_locked': False}}
    # -- add specific techno inputs to this
    DESC_IN.update(SolidFuelTechnoDiscipline.DESC_IN)

    # -- add specific techno outputs to this
    pelletizing_flue_gas_ratio = np.array([0.12])
    DESC_OUT = {'flue_gas_co2_ratio': {
        'type': 'array', 'default': pelletizing_flue_gas_ratio}}
    DESC_OUT.update(SolidFuelTechnoDiscipline.DESC_OUT)

    def init_execution(self):
        inputs_dict = self.get_sosdisc_inputs()
        self.techno_model = Pelletizing(self.techno_name)
        self.techno_model.configure_parameters(inputs_dict)