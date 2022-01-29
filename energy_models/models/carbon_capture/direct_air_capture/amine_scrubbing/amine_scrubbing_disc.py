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

from energy_models.models.carbon_capture.direct_air_capture.amine_scrubbing.amine import Amine
from energy_models.core.techno_type.disciplines.carbon_capture_techno_disc import CCTechnoDiscipline


class AmineScrubbingDiscipline(CCTechnoDiscipline):
    """**EnergyModelsDiscipline** is the :class:`~gems.core.discipline.MDODiscipline`
    implementing the computation of Energy Models outputs."""

    techno_name = 'direct_air_capture.AmineScrubbing'
    lifetime = 35
    construction_delay = 3
    techno_infos_dict_default = {'maturity': 0,
                                 'reaction': 'RNH2(Amine) + CO2 <--> (RNHCOO-) + (H+)',
                                 # Husebye, J., Brunsvold, A.L., Roussanaly, S. and Zhang, X., 2012.
                                 # Techno economic evaluation of amine based CO2 capture: impact of CO2 concentration and steam supply.
                                 # Energy Procedia, 23, pp.381-390.
                                 # Opex % : fig 5 - 6 :
                                 # https://reader.elsevier.com/reader/sd/pii/S1876610212010934?token=1A3181CEE6756AFE741AAACDFC004EAA641316AEC4BE6238B4712D20B90F53690774128290A7E3032F7D5AF0F8CC38A9
                                 'Opex_percentage': 0.25,
                                 'elec_demand': 0.25,
                                 'elec_demand_unit': 'kWh/kgCO2',
                                 # Fasihi, M., Efimova, O. and Breyer, C., 2019.
                                 # Techno-economic assessment of CO2 direct air capture plants.
                                 # Journal of cleaner production, 224, pp.957-980.
                                 # for now constant in time but should increase
                                 # with time 10%/10year according to Fasihi2019
                                 'heat_demand': 1.75,
                                 'heat_demand_unit': 'kWh/kgCO2',
                                 'WACC': 0.1,  # Weighted averaged cost of capital for the carbon capture plant
                                 'learning_rate': 0.1,
                                 'maximum_learning_capex_ratio': 0.33,
                                 'lifetime': lifetime,  # should be modified
                                 'lifetime_unit': 'years',
                                 # 0.6577,  # 730 euro/tCO2 in Fashi2019 Capex
                                 # initial at year 2020 1.11 euro/$
                                 'Capex_init': 0.88,  # average for solid techno, Fashi2019
                                 'Capex_init_unit': '$/kgCO2',
                                 'efficiency': 0.9,
                                 'CO2_capacity_peryear': 3.6E+8,  # kg CO2 /year
                                 'CO2_capacity_peryear_unit': 'kg CO2/year',
                                 'real_factor_CO2': 1.0,
                                 'transport_cost': 0.0,
                                 'transport_cost_unit': '$/kgCO2',
                                 # Keith, D.W., Holmes, G., Angelo, D.S. and Heidel, K., 2018.
                                 # A process for capturing CO2 from the atmosphere.
                                 # Joule, 2(8), pp.1573-1594.
                                 # Vo, T.T., Wall, D.M., Ring, D., Rajendran, K. and Murphy, J.D., 2018.
                                 # Techno-economic analysis of biogas upgrading via amine scrubber, carbon capture and ex-situ methanation.
                                 # Applied energy, 212, pp.1191-1202.
                                 # from Keith2018 3.18 GJ/tCaO in theory 5.25
                                 # GJ/tCO2 in practice (Climeworks)
                                 # according to Vo2018 4GJ/tCO2 or Fasihi2016:
                                 # 1.51 in practice
                                 'enthalpy': 1.124,
                                 'enthalpy_unit': 'kWh/kgC02',
                                 'energy_efficiency': 0.78,
                                 'construction_delay': construction_delay,
                                 'techno_evo_eff': 'no',
                                 'CO2_from_production': 0.0,
                                 'CO2_from_production_unit': 'kg/kg',
                                 }

    # source :
    # Husebye, J., Brunsvold, A.L., Roussanaly, S. and Zhang, X., 2012.
    # Techno economic evaluation of amine based CO2 capture: impact of CO2 concentration and steam supply.
    # Energy Procedia, 23, pp.381-390.
    # https://reader.elsevier.com/reader/sd/pii/S1876610212010934?token=1A3181CEE6756AFE741AAACDFC004EAA641316AEC4BE6238B4712D20B90F53690774128290A7E3032F7D5AF0F8CC38A9
    # Buijs, W. and De Flart, S., 2017.
    # Direct air capture of CO2 with an amine resin: A molecular modeling study of the CO2 capturing process.
    # Industrial & engineering chemistry research, 56(43), pp.12297-12304.
    # https://pubs.acs.org/doi/pdf/10.1021/acs.iecr.7b02613

    techno_info_dict = techno_infos_dict_default

    initial_capture = 5.0e-3  # in Mt at year_start
    invest_before_year_start = pd.DataFrame(
        {'past years': np.arange(-construction_delay, 0), 'invest': np.array([0.05093, 0.05093, 15.0930]) * 0.8 / 3000})

    initial_age_distribution = pd.DataFrame({'age': np.arange(1, lifetime - 1),
                                             'distrib': [10.0, 10.0, 10.0, 10.0, 10.0,
                                                         10.0, 10.0, 10.0,
                                                         10.0, 10.0, 0.0,
                                                         0.0, 0.0, 0.0,
                                                         0.0, 0.0, 0.0,
                                                         0.0, 0.0, 0.0,
                                                         0.0, 0.0, 0.0,
                                                         0.0, 0.0, 0.0,
                                                         0.0, 0.0, 0.0,
                                                         0.0, 0.0, 0.0,
                                                         0.0]
                                             })

    DESC_IN = {'techno_infos_dict': {'type': 'dict',
                                     'default': techno_infos_dict_default},
               'initial_production': {'type': 'float', 'unit': 'MtCO2', 'default': initial_capture},
               'initial_age_distrib': {'type': 'dataframe', 'unit': '%', 'default': initial_age_distribution,
                                       'dataframe_descriptor': {'age': ('int',  [0, 100], False),
                                                                'distrib': ('float',  None, True)},
                                       'dataframe_edition_locked': False},
               'invest_before_ystart': {'type': 'dataframe', 'unit': 'G$', 'default': invest_before_year_start,
                                        'dataframe_descriptor': {'past years': ('int',  [-20, -1], False),
                                                                 'invest': ('float',  None, True)},
                                        'dataframe_edition_locked': False}}
    # -- add specific techno outputs to this
    DESC_IN.update(CCTechnoDiscipline.DESC_IN)

    DESC_OUT = CCTechnoDiscipline.DESC_OUT

    _maturity = 'Research'

    def init_execution(self):
        inputs_dict = self.get_sosdisc_inputs()
        self.techno_model = Amine(self.techno_name)
        self.techno_model.configure_parameters(inputs_dict)

    def compute_sos_jacobian(self):
        # Grad of price vs energyprice

        CCTechnoDiscipline.compute_sos_jacobian(self)

        grad_dict = self.techno_model.grad_price_vs_energy_price()

        self.set_partial_derivatives_techno(
            grad_dict, None)