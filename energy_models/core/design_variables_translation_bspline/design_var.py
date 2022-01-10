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

from numpy import arange
from pandas import DataFrame
from sos_trades_core.tools.bspline.bspline import BSpline

import numpy as np


class Design_var(object):
    """
    Class Design variable
    """
    ACTIVATED_ELEM_LIST = "activated_elem"
    VARIABLES = "variable"
    VALUE = "value"

    def __init__(self, inputs_dict):
        self.year_start = inputs_dict['year_start']
        self.year_end = inputs_dict['year_end']
        self.time_step = inputs_dict['time_step']

        self.energy_list = inputs_dict['energy_list']
        self.ccs_list = inputs_dict['ccs_list']

        self.technology_dict = {
            energy: inputs_dict[f'{energy}.technologies_list'] for energy in self.energy_list + self.ccs_list}
        self.output_dict = {}

        self.bspline_dict = {}
        self.dspace = inputs_dict['design_space']

    def configure(self, inputs_dict):
        '''
        Configure with inputs_dict from the discipline
        '''
        self.output_dict = {}

        list_ctrl = ['ccs_percentage_array']

        list_ctrl.extend(
            [key for key in inputs_dict if key.endswith('_array_mix')])

        years = arange(self.year_start, self.year_end + 1, self.time_step)

        list_t_years = np.linspace(0.0, 1.0, len(years))

        for full_elem in list_ctrl:
            elem = full_elem.split('.')[-1]
            l_activated = self.dspace.loc[self.dspace[self.VARIABLES]
                                          == elem, self.ACTIVATED_ELEM_LIST].to_list()[0]
            value_dv = self.dspace.loc[self.dspace[self.VARIABLES]
                                       == elem, self.VALUE].to_list()[0]
            elem_val = inputs_dict[full_elem]
            index_false = None
            if not all(l_activated):
                index_false = l_activated.index(False)
                elem_val = list(elem_val)
                elem_val.insert(index_false, value_dv[index_false])
                elem_val = np.asarray(elem_val)

            if len(inputs_dict[full_elem]) == len(years):
                self.bspline_dict[full_elem] = {
                    'bspline': None, 'eval_t': inputs_dict[full_elem], 'b_array': np.identity(len(years))}
            else:
                bspline = BSpline(n_poles=len(elem_val))
                bspline.set_ctrl_pts(elem_val)
                eval_t, b_array = bspline.eval_list_t(list_t_years)
                b_array = bspline.update_b_array(b_array, index_false)

                self.bspline_dict[full_elem] = {
                    'bspline': bspline, 'eval_t': eval_t, 'b_array': b_array}
        #######

        ccs_percentage = DataFrame(
            {'years': years, 'ccs_percentage': self.bspline_dict['ccs_percentage_array']['eval_t']}, index=years)
        dict_energy_mix = {'years': years}
        dict_energy_mix.update(
            {energy: self.bspline_dict[f"{energy}.{energy.replace('.', '_')}_array_mix"]['eval_t'] for energy in self.energy_list})
        invest_energy_mix = DataFrame(
            dict_energy_mix, index=years)

        for energy in self.energy_list + self.ccs_list:
            energy_wo_dot = energy.replace('.', '_')
            dict_techno_mix = {'years': years}
            dict_techno_mix.update(
                {techno: self.bspline_dict[f"{energy}.{techno}.{energy_wo_dot}_{techno.replace('.', '_')}_array_mix"]['eval_t'] for techno in self.technology_dict[energy]})
            self.output_dict[f'{energy}.invest_techno_mix'] = DataFrame(
                dict_techno_mix, index=years)

        dict_ccs_mix = {'years': years}
        dict_ccs_mix.update(
            {ccs: self.bspline_dict[f"{ccs}.{ccs.replace('.', '_')}_array_mix"]['eval_t'] for ccs in self.ccs_list})
        invest_ccs_mix = DataFrame(
            dict_ccs_mix, index=years)

        self.output_dict['ccs_percentage'] = ccs_percentage
        self.output_dict['invest_energy_mix'] = invest_energy_mix
        self.output_dict['invest_ccs_mix'] = invest_ccs_mix
