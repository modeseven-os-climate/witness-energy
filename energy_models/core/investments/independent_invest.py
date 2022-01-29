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

from .base_invest import BaseInvest
import pandas as pd
import numpy as np
from sos_trades_core.tools.base_functions.exp_min import compute_func_with_exp_min


class IndependentInvest(BaseInvest):
    '''
        Model to Distribute Absolute invest from design space to technologies
        Need to compute a constraint on investment sum 
    '''

    def __init__(self, name='Invest'):
        '''
        Constructor
        '''
        BaseInvest.__init__(self, name)
        #-- default value, can be changed if necessary

        self.invest_mix = None
        self.scaling_factor_energy_investment = 1e2

    def compute_invest_constraint_and_objective(self, inputs_dict):
        '''
        Compute Investment constraint
        '''

        energy_investment = inputs_dict['energy_investment']
        self.scaling_factor_energy_investment = inputs_dict['scaling_factor_energy_investment']
        invest_constraint_ref = inputs_dict['invest_constraint_ref']
        invest_objective_ref = inputs_dict['invest_objective_ref']
        energy_invest_df = pd.DataFrame({'years': energy_investment['years'].values,
                                         'energy_investment': energy_investment['energy_investment'].values * self.scaling_factor_energy_investment})

        self.compute_distribution_list(inputs_dict)

        techno_invests = inputs_dict['invest_mix'][self.distribution_list]

        techno_invest_sum = techno_invests.sum(axis=1).values

        delta = energy_invest_df['energy_investment'].values - \
            techno_invest_sum
        invest_constraint = delta / invest_constraint_ref

        invest_constraint_df = pd.DataFrame({'years': energy_investment['years'].values,
                                             'invest_constraint': invest_constraint})

        invest_objective = compute_func_with_exp_min(
            delta, 1e-6) / energy_invest_df['energy_investment'].values / invest_objective_ref
        return invest_constraint_df, invest_objective