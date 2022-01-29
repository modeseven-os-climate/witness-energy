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
from energy_models.core.techno_type.disciplines.renewable_techno_disc import RenewableTechnoDiscipline
from energy_models.models.renewable.renewable_simple_techno.renewable_simple_techno import RenewableSimpleTechno


class RenewableSimpleTechnoDiscipline(RenewableTechnoDiscipline):
    """
        Generic Renewable Techno used in the WITNESS Coarse process
        It has a high price per kWh without CO2 but a low CO2 emissions per kWh
        It has properties similar to electricity technologies
    """

    techno_name = 'RenewableSimpleTechno'
    lifetime = 30
    construction_delay = 3

    techno_infos_dict_default = {'maturity': 0,
                                 'Opex_percentage': 0.12,
                                 'WACC': 0.058,
                                 'learning_rate': 0.00,
                                 'lifetime': lifetime,
                                 'lifetime_unit': 'years',
                                 'Capex_init': 6000,
                                 'Capex_init_unit': '$/kW',
                                 'full_load_hours': 8760.0,
                                 'capacity_factor': 0.90,
                                 'techno_evo_eff': 'no',
                                 'efficiency': 1.0,
                                 'CO2_from_production': 0.0,
                                 'CO2_from_production_unit': 'kg/kg',
                                 'construction_delay': construction_delay, }

    techno_info_dict = techno_infos_dict_default
    initial_production = 6590.0
    invest_before_year_start = pd.DataFrame(
        {'past years': np.arange(-construction_delay, 0), 'invest': [634.0, 635.0, 638.0]})

    initial_age_distribution = pd.DataFrame({'age': np.arange(1, lifetime),
                                             'distrib': [4.14634146, 6.2195122, 2.77439024, 6.92073171, 6.92073171,
                                                         3.44512195, 2.77439024, 2.07317073, 4.84756098, 3.44512195,
                                                         1.37195122, 2.07317073, 1.37195122, 2.77439024, 3.44512195,
                                                         1.37195122, 4.14634146, 2.07317073, 4.14634146, 2.77439024,
                                                         2.77439024, 2.07317073, 4.14634146, 2.77439024, 3.44512195,
                                                         6.2195122, 4.14634140, 2.77439024, 2.5304878],
                                             })

    DESC_IN = {'techno_infos_dict': {'type': 'dict',
                                     'default': techno_infos_dict_default},
               'initial_production': {'type': 'float', 'unit': 'TWh', 'default': initial_production},
               'initial_age_distrib': {'type': 'dataframe', 'unit': '%', 'default': initial_age_distribution,
                                       'dataframe_descriptor': {'age': ('int',  [0, 100], False),
                                                                'distrib': ('float',  None, True)},
                                       'dataframe_edition_locked': False},
               'invest_before_ystart': {'type': 'dataframe', 'unit': 'G$', 'default': invest_before_year_start,
                                        'dataframe_descriptor': {'past years': ('int',  [-20, -1], False),
                                                                 'invest': ('float',  None, True)},
                                        'dataframe_edition_locked': False}}
    # -- add specific techno outputs to this
    DESC_IN.update(RenewableTechnoDiscipline.DESC_IN)

    DESC_OUT = RenewableTechnoDiscipline.DESC_OUT

    _maturity = 'Research'

    def init_execution(self):
        inputs_dict = self.get_sosdisc_inputs()
        self.techno_model = RenewableSimpleTechno(self.techno_name)
        self.techno_model.configure_parameters(inputs_dict)