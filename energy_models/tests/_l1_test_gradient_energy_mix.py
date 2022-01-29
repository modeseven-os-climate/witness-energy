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

import numpy as np
import pandas as pd
from os.path import dirname
from sos_trades_core.execution_engine.execution_engine import ExecutionEngine

from energy_models.sos_processes.energy.MDO_subprocesses.energy_optim_sub_process.usecase import Study
from energy_models.sos_processes.energy.MDA.energy_process_v0.usecase import Study as Study_open
from sos_trades_core.tests.core.abstract_jacobian_unit_test import AbstractJacobianUnittest
from sos_trades_core.tools.post_processing.post_processing_factory import PostProcessingFactory
from energy_models.core.energy_mix.energy_mix import EnergyMix


class EnergyMixJacobianTestCase(AbstractJacobianUnittest):
    """
    Energy mix jacobian test class
    """
    AbstractJacobianUnittest.DUMP_JACOBIAN = False
    parallel = True

    def analytic_grad_entry(self):
        return [

            self.test_01_energy_mix_discipline_jacobian_obj_constraints_wrt_state_variables,
            self.test_02_energy_mix_discipline_residual_vars_wrt_state_variables,
            self.test_03_gradient_energy_mix_with_open_loop,
            self.test_04_energy_mix_discipline_co2_emissions_gt,
            self.test_05_energy_mix_test_mean_price_grad,
            self.test_06_energy_mix_all_outputs,
            self._test_07_energy_mix_co2_tax,
            self._test_09_energy_mix_gradients_cutoff,
            self.test_08_energy_mix_gradients_exponential_limit,
            self.test_10_energy_mix_demand_dataframe,
            self.test_11_energy_mix_detailed_co2_emissions,
            self.test_12_energy_mix_detailed_co2_emissions_ratio_available_capture,
            self.test_13_energy_mix_co2_per_use_gradients]

    def setUp(self):
        '''
        Initialize third data needed for testing
        '''
        self.disc_name = 'energy_mix'
        self.year_start = 2020
        self.year_end = 2050
        self.years = np.arange(self.year_start, self.year_end + 1)
        self.energy_list = ['hydrogen.gaseous_hydrogen', 'methane']
        self.consumption_hydro = pd.DataFrame({'electricity (TWh)': np.array([5.79262302e+09, 5.96550630e+09, 6.13351314e+09, 6.29771389e+09,
                                                                              6.45887954e+09, 6.61758183e+09, 6.81571547e+09, 7.00833095e+09,
                                                                              7.19662898e+09, 7.38146567e+09, 7.56347051e+09, 7.58525158e+09,
                                                                              7.60184181e+09, 7.61413788e+09, 7.62282699e+09, 7.62844682e+09,
                                                                              7.63143167e+09, 7.63212186e+09, 7.63080121e+09, 7.62770511e+09,
                                                                              7.62303081e+09, 7.61658967e+09, 7.60887892e+09, 7.60002116e+09,
                                                                              7.59012249e+09, 7.57927528e+09, 7.56756653e+09, 7.55506132e+09,
                                                                              7.54182260e+09, 7.52790631e+09, 7.51336234e+09]) / 1.0e9,
                                               'methane (TWh)': np.array([1.30334018e+10, 1.34223892e+10, 1.38004046e+10, 1.41698563e+10,
                                                                          1.45324790e+10, 1.48895591e+10, 1.53353598e+10, 1.57687446e+10,
                                                                          1.61924152e+10, 1.66082977e+10, 1.70178086e+10, 1.70668161e+10,
                                                                          1.71041441e+10, 1.71318102e+10, 1.71513607e+10, 1.71640053e+10,
                                                                          1.71707213e+10, 1.71722742e+10, 1.71693027e+10, 1.71623365e+10,
                                                                          1.71518193e+10, 1.71373267e+10, 1.71199776e+10, 1.71000476e+10,
                                                                          1.70777756e+10, 1.70533694e+10, 1.70270247e+10, 1.69988880e+10,
                                                                          1.69691008e+10, 1.69377892e+10, 1.69050653e+10]) / 1.0e9,
                                               'water (Mt)': np.array([8.23100419e+09, 8.47666200e+09, 8.71539063e+09, 8.94871102e+09,
                                                                       9.17771870e+09, 9.40322607e+09, 9.68476326e+09, 9.95845946e+09,
                                                                       1.02260208e+10, 1.04886637e+10, 1.07472828e+10, 1.07782325e+10,
                                                                       1.08018063e+10, 1.08192784e+10, 1.08316251e+10, 1.08396106e+10,
                                                                       1.08438519e+10, 1.08448326e+10, 1.08429560e+10, 1.08385567e+10,
                                                                       1.08319147e+10, 1.08227622e+10, 1.08118056e+10, 1.07992193e+10,
                                                                       1.07851538e+10, 1.07697405e+10, 1.07531030e+10, 1.07353338e+10,
                                                                       1.07165222e+10, 1.06967480e+10, 1.06760818e+10]) / 1.0e9})

        self.production_hydro = pd.DataFrame({'hydrogen.gaseous_hydrogen': np.array([2.89631151e+10, 2.98275315e+10, 3.06675657e+10, 3.14885694e+10,
                                                                                     3.22943977e+10, 3.30879091e+10, 3.40785773e+10, 3.50416548e+10,
                                                                                     3.59831449e+10, 3.69073283e+10, 3.78173526e+10, 3.79262579e+10,
                                                                                     3.80092091e+10, 3.80706894e+10, 3.81141349e+10, 3.81422341e+10,
                                                                                     3.81571584e+10, 3.81606093e+10, 3.81540060e+10, 3.81385255e+10,
                                                                                     3.81151541e+10, 3.80829483e+10, 3.80443946e+10, 3.80001058e+10,
                                                                                     3.79506125e+10, 3.78963764e+10, 3.78378327e+10, 3.77753066e+10,
                                                                                     3.77091130e+10, 3.76395315e+10, 3.75668117e+10]) / 1.0e9,
                                              'hydrogen.gaseous_hydrogen SMR (TWh)': np.array([1.44815575e+10, 1.49137658e+10, 1.53337829e+10, 1.57442847e+10,
                                                                                               1.61471989e+10, 1.65439546e+10, 1.70392887e+10, 1.75208274e+10,
                                                                                               1.79915724e+10, 1.84536642e+10, 1.89086763e+10, 1.89631289e+10,
                                                                                               1.90046045e+10, 1.90353447e+10, 1.90570675e+10, 1.90711170e+10,
                                                                                               1.90785792e+10, 1.90803046e+10, 1.90770030e+10, 1.90692628e+10,
                                                                                               1.90575770e+10, 1.90414742e+10, 1.90221973e+10, 1.90000529e+10,
                                                                                               1.89753062e+10, 1.89481882e+10, 1.89189163e+10, 1.88876533e+10,
                                                                                               1.88545565e+10, 1.88197658e+10, 1.87834058e+10]) / 1.0e9,
                                              'CO2 (Mt)': np.array([1.45250457e+09, 1.49585518e+09, 1.53798303e+09, 1.57915649e+09,
                                                                    1.61956889e+09, 1.65936361e+09, 1.70904577e+09, 1.75734425e+09,
                                                                    1.80456012e+09, 1.85090806e+09, 1.89654591e+09, 1.90200753e+09,
                                                                    1.90616754e+09, 1.90925079e+09, 1.91142959e+09, 1.91283877e+09,
                                                                    1.91358722e+09, 1.91376029e+09, 1.91342913e+09, 1.91265278e+09,
                                                                    1.91148070e+09, 1.90986558e+09, 1.90793210e+09, 1.90571101e+09,
                                                                    1.90322891e+09, 1.90050897e+09, 1.89757299e+09, 1.89443730e+09,
                                                                    1.89111768e+09, 1.88762816e+09, 1.88398125e+09]) / 1.0e9,
                                              'hydrogen.gaseous_hydrogen Electrolysis (TWh)': np.array([1.44815575e+10, 1.49137658e+10, 1.53337829e+10, 1.57442847e+10,
                                                                                                        1.61471989e+10, 1.65439546e+10, 1.70392887e+10, 1.75208274e+10,
                                                                                                        1.79915724e+10, 1.84536642e+10, 1.89086763e+10, 1.89631289e+10,
                                                                                                        1.90046045e+10, 1.90353447e+10, 1.90570675e+10, 1.90711170e+10,
                                                                                                        1.90785792e+10, 1.90803046e+10, 1.90770030e+10, 1.90692628e+10,
                                                                                                        1.90575770e+10, 1.90414742e+10, 1.90221973e+10, 1.90000529e+10,
                                                                                                        1.89753062e+10, 1.89481882e+10, 1.89189163e+10, 1.88876533e+10,
                                                                                                        1.88545565e+10, 1.88197658e+10, 1.87834058e+10]) / 1.0e9,
                                              'O2 (Mt)': np.array([1.45250457e+09, 1.49585518e+09, 1.53798303e+09, 1.57915649e+09,
                                                                   1.61956889e+09, 1.65936361e+09, 1.70904577e+09, 1.75734425e+09,
                                                                   1.80456012e+09, 1.85090806e+09, 1.89654591e+09, 1.90200753e+09,
                                                                   1.90616754e+09, 1.90925079e+09, 1.91142959e+09, 1.91283877e+09,
                                                                   1.91358722e+09, 1.91376029e+09, 1.91342913e+09, 1.91265278e+09,
                                                                   1.91148070e+09, 1.90986558e+09, 1.90793210e+09, 1.90571101e+09,
                                                                   1.90322891e+09, 1.90050897e+09, 1.89757299e+09, 1.89443730e+09,
                                                                   1.89111768e+09, 1.88762816e+09, 1.88398125e+09]) / 1.0e9})

        self.prices_hydro = pd.DataFrame({'hydrogen.gaseous_hydrogen': np.array([0.076815, 0.07549102, 0.07433427, 0.07330841, 0.07238752,
                                                                                 0.07155253, 0.07050461, 0.06960523, 0.068821, 0.06812833,
                                                                                 0.06750997, 0.066893, 0.06635812, 0.06589033, 0.06547834,
                                                                                 0.06511344, 0.06478879, 0.06449895, 0.06423948, 0.06400678,
                                                                                 0.06379784, 0.06361016, 0.06344163, 0.06329045, 0.06315508,
                                                                                 0.0630342, 0.06292668, 0.06283151, 0.06274783, 0.06267487,
                                                                                 0.06261198]) * 1000.0})

        self.consumption = pd.DataFrame({'CO2 (Mt)': np.array([1.28473431e+09, 1.24026410e+09, 1.20920553e+09, 2.49446882e+10,
                                                               5.50034920e+10, 8.99877703e+10, 1.29098065e+11, 1.71931680e+11,
                                                               2.18234033e+11, 2.68123194e+11, 3.21458915e+11, 3.78134326e+11,
                                                               4.38214336e+11, 5.01623337e+11, 5.66820327e+11, 6.33674016e+11,
                                                               7.02070511e+11, 7.71909835e+11, 8.19285617e+11, 8.61586757e+11,
                                                               9.00230650e+11, 9.35836743e+11, 9.68739031e+11, 9.99135391e+11,
                                                               1.02697781e+12, 1.05232158e+12, 1.07519492e+12, 1.09560777e+12,
                                                               1.11355731e+12, 1.13049193e+12, 1.14650986e+12]) / 1.0e9,
                                         'hydrogen.gaseous_hydrogen (TWh)': np.array([7.83846196e+09, 7.56713887e+09, 7.37764337e+09, 1.52193327e+11,
                                                                                      3.35589060e+11, 5.49036255e+11, 7.87657231e+11, 1.04899505e+12,
                                                                                      1.33149645e+12, 1.63588179e+12, 1.96129539e+12, 2.30708521e+12,
                                                                                      2.67364729e+12, 3.06052031e+12, 3.45830226e+12, 3.86619212e+12,
                                                                                      4.28349500e+12, 4.70960091e+12, 4.99865154e+12, 5.25674061e+12,
                                                                                      5.49251596e+12, 5.70975699e+12, 5.91050148e+12, 6.09595672e+12,
                                                                                      6.26582979e+12, 6.42045801e+12, 6.56001356e+12, 6.68455710e+12,
                                                                                      6.79407140e+12, 6.89739345e+12, 6.99512256e+12]) / 1.0e9,
                                         'electricity (TWh)': np.array([1.24834354e+10, 2.26888500e+10, 3.13224798e+10, 4.16183686e+10,
                                                                        5.33137316e+10, 6.65015094e+10, 8.07396503e+10, 9.59308386e+10,
                                                                        1.12076605e+11, 1.29500242e+11, 1.48068984e+11, 1.67664859e+11,
                                                                        1.88614872e+11, 2.10307763e+11, 2.32534190e+11, 2.55258218e+11,
                                                                        2.78448193e+11, 3.02075958e+11, 3.26116264e+11, 3.50546301e+11,
                                                                        3.66620834e+11, 3.81434383e+11, 3.98191584e+11, 4.13453346e+11,
                                                                        4.27540649e+11, 4.40613006e+11, 4.52762555e+11, 4.64046630e+11,
                                                                        4.74445226e+11, 4.83975687e+11, 4.92647562e+11]) / 1.0e9,
                                         'biogas (TWh)': np.array([1.49773000e+11, 2.72214901e+11, 3.75798938e+11, 4.99326325e+11,
                                                                   6.39644238e+11, 7.97867754e+11, 9.68693252e+11, 1.15095316e+12,
                                                                   1.34466585e+12, 1.55371011e+12, 1.77649302e+12, 2.01159922e+12,
                                                                   2.26295200e+12, 2.52321765e+12, 2.78988452e+12, 3.06252149e+12,
                                                                   3.34074875e+12, 3.62422851e+12, 3.91265782e+12, 4.20576304e+12,
                                                                   4.39862108e+12, 4.57635017e+12, 4.77739870e+12, 4.96050534e+12,
                                                                   5.12952113e+12, 5.28635985e+12, 5.43212697e+12, 5.56751036e+12,
                                                                   5.69227000e+12, 5.80661398e+12, 5.91065688e+12]) / 1.0e9,
                                         'MEA (Mt)': np.array([7.43925657e+08, 1.35209717e+09, 1.86660126e+09, 2.48016441e+09,
                                                               3.17712645e+09, 3.96302600e+09, 4.81151986e+09, 5.71680869e+09,
                                                               6.67898370e+09, 7.71731095e+09, 8.82387839e+09, 9.99165585e+09,
                                                               1.12401304e+10, 1.25328754e+10, 1.38574154e+10, 1.52116089e+10,
                                                               1.65935696e+10, 1.80016196e+10, 1.94342541e+10, 2.08901139e+10,
                                                               2.18480439e+10, 2.27308280e+10, 2.37294403e+10, 2.46389349e+10,
                                                               2.54784398e+10, 2.62574611e+10, 2.69814895e+10, 2.76539416e+10,
                                                               2.82736254e+10, 2.88415743e+10, 2.93583576e+10]) / 1.0e9})

        self.production = pd.DataFrame({'methane': np.array([1.16605879e+11, 2.09714671e+11, 2.88496631e+11, 4.30619647e+11,
                                                             5.98336737e+11, 7.89664048e+11, 9.98944599e+11, 1.22447365e+12,
                                                             1.46574928e+12, 1.72596317e+12, 2.00361864e+12, 2.29742180e+12,
                                                             2.61049046e+12, 2.93708922e+12, 3.27218360e+12, 3.61517937e+12,
                                                             3.96555667e+12, 4.32285576e+12, 4.63840191e+12, 4.94722388e+12,
                                                             5.17232979e+12, 5.37976418e+12, 5.59946957e+12, 5.80044012e+12,
                                                             5.98550982e+12, 6.15624743e+12, 6.31355157e+12, 6.45796597e+12,
                                                             6.58930224e+12, 6.71065379e+12, 6.82230688e+12]) / 1.0e9,
                                        'methane Emethane (TWh)': np.array([2.60340125e+09, 2.51328627e+09, 2.45034882e+09, 5.05482199e+10,
                                                                            1.11459746e+11, 1.82352314e+11, 2.61605891e+11, 3.48404451e+11,
                                                                            4.42232103e+11, 5.43328106e+11, 6.51408261e+11, 7.66256003e+11,
                                                                            8.88002867e+11, 1.01649564e+12, 1.14861161e+12, 1.28408474e+12,
                                                                            1.42268423e+12, 1.56420749e+12, 1.66021035e+12, 1.74592990e+12,
                                                                            1.82423835e+12, 1.89639097e+12, 1.96306457e+12, 2.02466013e+12,
                                                                            2.08108035e+12, 2.13243727e+12, 2.17878808e+12, 2.22015293e+12,
                                                                            2.25652610e+12, 2.29084262e+12, 2.32330155e+12]) / 1.0e9,
                                        'invest': np.array([8.87150e+09, 9.04400e+09, 9.21650e+09, 9.38900e+09, 9.56150e+09,
                                                            9.73400e+09, 9.93880e+09, 1.01436e+10, 1.03484e+10, 1.05532e+10,
                                                            1.07580e+10, 1.07294e+10, 1.07008e+10, 1.06722e+10, 1.06436e+10,
                                                            1.06150e+10, 1.05864e+10, 1.05578e+10, 1.05292e+10, 1.05006e+10,
                                                            1.04720e+10, 1.04434e+10, 1.04148e+10, 1.03862e+10, 1.03576e+10,
                                                            1.03290e+10, 1.03004e+10, 1.02718e+10, 1.02432e+10, 1.02146e+10,
                                                            1.01860e+10]) / 1.0e9,
                                        'water (Mt)': np.array([4.20719806e+08, 4.06156873e+08, 3.95985935e+08, 8.16878967e+09,
                                                                1.80123301e+10, 2.94688458e+10, 4.22765332e+10, 5.63035194e+10,
                                                                7.14664343e+10, 8.78039430e+10, 1.05270118e+11, 1.23829961e+11,
                                                                1.43504730e+11, 1.64269664e+11, 1.85620121e+11, 2.07513107e+11,
                                                                2.29911326e+11, 2.52782037e+11, 2.68296474e+11, 2.82149087e+11,
                                                                2.94804040e+11, 3.06464185e+11, 3.17238898e+11, 3.27192980e+11,
                                                                3.36310708e+11, 3.44610188e+11, 3.52100660e+11, 3.58785381e+11,
                                                                3.64663427e+11, 3.70209111e+11, 3.75454601e+11]) / 1.0e9,
                                        'methane UpgradingBiogas (TWh)': np.array([1.14002477e+11, 2.07201385e+11, 2.86046282e+11, 3.80071427e+11,
                                                                                   4.86876991e+11, 6.07311734e+11, 7.37338708e+11, 8.76069197e+11,
                                                                                   1.02351718e+12, 1.18263506e+12, 1.35221038e+12, 1.53116579e+12,
                                                                                   1.72248759e+12, 1.92059358e+12, 2.12357198e+12, 2.33109463e+12,
                                                                                   2.54287243e+12, 2.75864827e+12, 2.97819156e+12, 3.20129399e+12,
                                                                                   3.34809144e+12, 3.48337321e+12, 3.63640500e+12, 3.77577999e+12,
                                                                                   3.90442947e+12, 4.02381016e+12, 4.13476348e+12, 4.23781304e+12,
                                                                                   4.33277614e+12, 4.41981116e+12, 4.49900533e+12]) / 1.0e9,
                                        'CO2 (Mt)': np.array([5.62582867e+09, 1.02250365e+10, 1.41158983e+10, 1.87558795e+10,
                                                              2.40265528e+10, 2.99698028e+10, 3.63864132e+10, 4.32325272e+10,
                                                              5.05088346e+10, 5.83610321e+10, 6.67292861e+10, 7.55604318e+10,
                                                              8.50018377e+10, 9.47780320e+10, 1.04794671e+11, 1.15035562e+11,
                                                              1.25486437e+11, 1.36134608e+11, 1.46968696e+11, 1.57978422e+11,
                                                              1.65222627e+11, 1.71898553e+11, 1.79450412e+11, 1.86328331e+11,
                                                              1.92676964e+11, 1.98568198e+11, 2.04043557e+11, 2.09128877e+11,
                                                              2.13815145e+11, 2.18110176e+11, 2.22018273e+11]) / 1.0e9})

        self.cost_details = pd.DataFrame({'methane': np.array([0.19333753, 0.1874625, 0.18467199, 0.21320619, 0.2308158,
                                                               0.24196874, 0.25146023, 0.25909781, 0.26565857, 0.27142873,
                                                               0.27673861, 0.27989425, 0.28277203, 0.28558565, 0.28905927,
                                                               0.29229019, 0.29530982, 0.29853801, 0.29984838, 0.30094081,
                                                               0.30355508, 0.3071769, 0.31104297, 0.31440867, 0.31709487,
                                                               0.32047716, 0.32392652, 0.32739837, 0.33021771, 0.33313758,
                                                               0.3361545]) * 1000.0})
        self.energy_demand = {}
        self.energy_demand['hydrogen.gaseous_hydrogen.energy_demand'] = pd.DataFrame({'years': self.years,
                                                                                      'demand': np.arange(50, 81)})
        self.energy_demand['methane.energy_demand'] = pd.DataFrame({'years': self.years,
                                                                    'demand': np.arange(20, 51)})
        self.energy_demand['biogas.energy_demand'] = pd.DataFrame({'years': self.years,
                                                                   'demand': np.arange(10, 41)})
        #---Ratios---
        demand_ratio_dict = dict(
            zip(EnergyMix.energy_list, np.linspace(0.2, 0.8, len(self.years))))
        demand_ratio_dict['years'] = self.years
        self.all_streams_demand_ratio = pd.DataFrame(demand_ratio_dict)

        resource_ratio_dict = dict(
            zip(EnergyMix.RESOURCE_LIST, np.linspace(0.9, 0.3, len(self.years))))
        resource_ratio_dict['years'] = self.years
        self.all_resource_ratio_usable_demand = pd.DataFrame(
            resource_ratio_dict)

    def test_01_energy_mix_discipline_jacobian_obj_constraints_wrt_state_variables(self):

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'
        func_manager_name = 'FunctionManagerDisc'

        repo = 'energy_models.sos_processes.energy.MDA'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_process_v0')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study_open(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)

        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-8
        full_values_dict[f'{name}.max_mda_iter'] = 50
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.EnergyMix')[0]
        energy_list = full_values_dict['Test.energy_list']

        inputs_names = [
            f'{name}.{model_name}.{energy}.energy_prices' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']]
        inputs_names.extend([
            f'{name}.{model_name}.{energy}.energy_production' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.{energy}.energy_consumption' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_consumption' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_production' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend([
            f'{name}.CCUS.{energy}.energy_prices' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.{energy}.CO2_emissions' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.syngas.syngas_ratio'])
        inputs_names.extend(
            [f'{name}.CO2_taxes'])

        outputs_names = [f'{name}.{func_manager_name}.co2_emissions_objective',
                         f'{name}.{func_manager_name}.energy_production_objective',
                         f'{name}.{func_manager_name}.primary_energies_production',
                         f'{name}.CCS_price',
                         f'{name}.{func_manager_name}.total_prod_solid_fuel_elec',
                         f'{name}.{func_manager_name}.total_prod_h2_liquid',
                         f'{name}.{func_manager_name}.syngas_prod_objective',
                         f'{name}.{func_manager_name}.carbon_storage_constraint'
                         ]
        outputs_names.extend(
            [f'{name}.{model_name}.{energy}.demand_violation' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        #AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_obj_constraints_wrt_state_variables.pkl',
                            discipline=disc, step=1.0e-16, derr_approx='complex_step', threshold=1e-5,
                            inputs=inputs_names, outputs=outputs_names, parallel=self.parallel)

    def test_02_energy_mix_discipline_residual_vars_wrt_state_variables(self):

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'

        repo = 'energy_models.sos_processes.energy.MDA'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_process_v0')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study_open(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)
        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-8
        full_values_dict[f'{name}.max_mda_iter'] = 50
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.EnergyMix')[0]
        energy_list = full_values_dict['Test.energy_list']

        inputs_names = [
            f'{name}.{model_name}.{energy}.energy_prices' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']]
        inputs_names.extend([
            f'{name}.{model_name}.{energy}.energy_production' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.{energy}.energy_consumption' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_consumption' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_production' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend([
            f'{name}.CCUS.{energy}.energy_prices' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.{energy}.CO2_emissions' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.syngas.syngas_ratio'])
        inputs_names.extend(
            [f'{name}.CO2_taxes'])

        outputs_names = [f'{name}.{model_name}.energy_prices',
                         f'{name}.{model_name}.energy_CO2_emissions']
        # AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energymix_output_vs_design_vars.pkl',
                            discipline=disc, step=1.0e-16, derr_approx='complex_step', threshold=1e-5,
                            inputs=inputs_names, outputs=outputs_names, parallel=self.parallel)

    def test_03_gradient_energy_mix_with_open_loop(self):

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'

        repo = 'energy_models.sos_processes.energy.MDO_subprocesses'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_optim_sub_process')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)
        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-8
        full_values_dict[f'{name}.sub_mda_class'] = 'MDANewtonRaphson'
        full_values_dict[f'{name}.max_mda_iter'] = 50
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        disc_energy_mix = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.EnergyModelEval.EnergyMix')[0]

        input_names = ['methane.energy_consumption', 'methane.energy_production', 'methane.energy_prices',
                       'methane.CO2_emissions', 'hydrogen.gaseous_hydrogen.energy_consumption', 'hydrogen.gaseous_hydrogen.energy_production',
                       'hydrogen.gaseous_hydrogen.energy_prices', 'hydrogen.gaseous_hydrogen.CO2_emissions', 'biogas.energy_consumption', 'biogas.energy_production',
                       'biogas.energy_prices', 'biogas.CO2_emissions', 'electricity.energy_consumption',
                       'electricity.energy_production', 'electricity.energy_prices',
                       'electricity.CO2_emissions', 'solid_fuel.energy_consumption', 'solid_fuel.energy_production',
                       'solid_fuel.energy_prices', 'solid_fuel.CO2_emissions', 'liquid_fuel.energy_production',
                       'liquid_fuel.energy_consumption', 'liquid_fuel.energy_prices',
                       'liquid_fuel.CO2_emissions', 'biodiesel.energy_consumption', 'biodiesel.energy_production',
                       'biodiesel.energy_prices', 'biodiesel.CO2_emissions',
                       'syngas.energy_consumption', 'syngas.energy_production', 'syngas.energy_prices',
                       'syngas.CO2_emissions', 'biomass_dry.energy_consumption', 'biomass_dry.energy_production',
                       'biomass_dry.energy_prices', 'biomass_dry.CO2_emissions',
                       'carbon_capture.energy_consumption', 'carbon_capture.energy_production', 'carbon_capture.energy_prices',
                       'carbon_storage.energy_consumption', 'carbon_storage.energy_production', 'carbon_storage.energy_prices',
                       'syngas_ratio', 'CO2_taxes']
        inputs_full_names = [disc_energy_mix.get_var_full_name(
            inp, disc_energy_mix._data_in) for inp in input_names]

        output_names = ['energy_prices', 'energy_CO2_emissions', 'co2_emissions_objective', 'energy_production_objective', 'methane.demand_violation', 'hydrogen.gaseous_hydrogen.demand_violation',
                        'biogas.demand_violation', 'electricity.demand_violation', 'solid_fuel.demand_violation', 'liquid_fuel.demand_violation', 'biodiesel.demand_violation', 'syngas.demand_violation', 'biomass_dry.demand_violation']
        outputs_full_names = [disc_energy_mix.get_var_full_name(
            out, disc_energy_mix._data_out) for out in output_names]

        # np.set_printoptions(threshold=1000000)
        #AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energy_mix_open_loop_objectives_demand.pkl',
                            discipline=disc_energy_mix, step=1.0e-16, derr_approx='complex_step', threshold=1e-5,
                            inputs=inputs_full_names, outputs=outputs_full_names, parallel=self.parallel)

#         # check gradient of 'energy_production' output
#
#         input_names = ['methane.energy_consumption',
#                        'hydrogen.gaseous_hydrogen.energy_consumption',
#                        'solid_fuel.energy_consumption',
#                        'biogas.energy_consumption',
#                        'electricity.energy_consumption',
#                        'liquid_fuel.energy_consumption',
#                        'biodiesel.energy_consumption',
#                        'syngas.energy_consumption',
#                        'biomass_dry.energy_consumption',
#                        'carbon_capture.energy_consumption',
#                        #'carbon_storage.energy_consumption'
#                        ]

#         inputs_full_names = [disc_energy_mix.get_var_full_name(
#             inp, disc_energy_mix._data_in) for inp in input_names]
#
#         input_col = {
#             'methane.energy_consumption': ['biogas (TWh)', 'electricity (TWh)'],
#             'hydrogen.gaseous_hydrogen.energy_consumption': ['electricity (TWh)', 'methane (TWh)', 'electricity (TWh)', 'syngas (TWh)'],
#             'solid_fuel.energy_consumption': ['electricity (TWh)', 'biomass_dry (TWh)'],
#             'biogas.energy_consumption': ['electricity (TWh)'],
#             'electricity.energy_consumption': ['methane (TWh)', 'electricity (TWh)', 'solid_fuel (TWh)'],
#             'liquid_fuel.energy_consumption': ['electricity (TWh)', 'syngas (TWh)'],
#             'biodiesel.energy_consumption': ['electricity (TWh)'],
#             'syngas.energy_consumption': ['methane (TWh)', 'electricity (TWh)', 'solid_fuel (TWh)', 'biomass_dry (TWh)'],
#             'biomass_dry.energy_consumption': ['electricity (TWh)'],
#             'carbon_capture.energy_consumption': ['electricity (TWh)'],
#             #'carbon_storage.energy_consumption': ['biomass_dry (TWh)']
#         }
#
#         output_names = ['energy_production']
#         outputs_full_names = [disc_energy_mix.get_var_full_name(
#             out, disc_energy_mix._data_out) for out in output_names]
#
#         # np.set_printoptions(threshold=1000000)
#
#         for input, input_name in zip(inputs_full_names, input_names):
#             for col in input_col[input_name]:
#
#                 self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energy_mix_open_loop_energy_production.pkl',
#                                     discipline=disc_energy_mix, step=1.0e-16, derr_approx='complex_step', threshold=1e-5,
#                                     inputs=[input], outputs=outputs_full_names,
# input_column=col, output_column='Total production')

    def test_04_energy_mix_discipline_co2_emissions_gt(self):

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'

        repo = 'energy_models.sos_processes.energy.MDA'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_process_v0')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study_open(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)

        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-8
        full_values_dict[f'{name}.max_mda_iter'] = 50
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{name}.{model_name}')[0]
        energy_list = full_values_dict['Test.energy_list']

        inputs_names = [
            f'{name}.{model_name}.{energy}.energy_prices' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']]
        inputs_names.extend([
            f'{name}.{model_name}.{energy}.energy_production' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.{energy}.energy_consumption' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_consumption' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_production' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend([
            f'{name}.CCUS.{energy}.energy_prices' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.{energy}.CO2_emissions' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.syngas.syngas_ratio'])
        #AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energymix_co2_emissions_gt.pkl',
                            discipline=disc, step=1.0e-16, derr_approx='complex_step', threshold=1e-5,
                            inputs=inputs_names, outputs=[f'{name}.{model_name}.co2_emissions_Gt'], parallel=self.parallel)

    def test_05_energy_mix_test_mean_price_grad(self):

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'

        repo = 'energy_models.sos_processes.energy.MDA'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_process_v0')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study_open(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)
        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-8
        full_values_dict[f'{name}.max_mda_iter'] = 50
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.EnergyMix')[0]
        energy_list = full_values_dict['Test.energy_list']

        inputs_names = [
            f'{name}.{model_name}.{energy}.energy_prices' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']]
        inputs_names.extend([
            f'{name}.{model_name}.{energy}.energy_production' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.{energy}.energy_consumption' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_consumption' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_production' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend([
            f'{name}.CCUS.{energy}.energy_prices' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.syngas.syngas_ratio'])
        outputs_names = [f'{name}.{model_name}.energy_mean_price']
        #AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energy_mean_price_energy_prices_production.pkl',
                            discipline=disc, step=1.0e-14, derr_approx='complex_step', threshold=1e-5,
                            inputs=inputs_names, outputs=outputs_names, parallel=self.parallel)

    def test_06_energy_mix_all_outputs(self):

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'
        func_manager_name = 'FunctionManagerDisc'
        repo = 'energy_models.sos_processes.energy.MDA'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_process_v0')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study_open(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)
        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-8
        full_values_dict[f'{name}.max_mda_iter'] = 50
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.EnergyMix')[0]
        energy_list = full_values_dict['Test.energy_list']

        inputs_names = [
            f'{name}.{model_name}.{energy}.energy_prices' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']]
        inputs_names.extend([
            f'{name}.{model_name}.{energy}.energy_production' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.{energy}.energy_consumption' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_consumption' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_production' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend([
            f'{name}.CCUS.{energy}.energy_prices' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.syngas.syngas_ratio'])

        energy_mix_output = [f'{name}.{model_name}.energy_production', f'{name}.{model_name}.co2_emissions_Gt',
                             f'{name}.{func_manager_name}.energy_production_objective',
                             f'{name}.{func_manager_name}.co2_emissions_objective',
                             f'{name}.{model_name}.energy_mean_price',
                             f'{name}.{model_name}.land_demand_df',
                             f'{name}.{func_manager_name}.primary_energies_production',
                             f'{name}.CCS_price',
                             f'{name}.{func_manager_name}.total_prod_minus_min_prod_constraint_df',
                             f'{name}.{model_name}.energy_prices_after_tax',
                             f'{name}.{func_manager_name}.carbon_storage_constraint']
        #AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energy_mix_outputs.pkl',
                            discipline=disc, step=1.0e-12, derr_approx='complex_step', threshold=1e-5,
                            inputs=inputs_names, outputs=energy_mix_output, parallel=self.parallel)

    def _test_07_energy_mix_co2_tax(self):

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'
        func_manager_name = 'FunctionManagerDisc'
        repo = 'energy_models.sos_processes.energy.MDA'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_process_v0')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study_open(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)
        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-8
        full_values_dict[f'{name}.max_mda_iter'] = 50
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.EnergyMix')[0]
        energy_list = full_values_dict['Test.energy_list']

        inputs_names = [
            f'{name}.CO2_taxes']

        energy_mix_output = [f'{name}.{model_name}.energy_mean_price',
                             f'{name}.{model_name}.energy_prices_after_tax']
        #AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energy_mix_co2_tax.pkl',
                            discipline=disc, step=1.0e-12, derr_approx='complex_step', threshold=1e-5,
                            inputs=inputs_names, outputs=energy_mix_output, parallel=self.parallel)

    def test_08_energy_mix_gradients_exponential_limit(self):
        '''
            Test on energy_mix gradients if the limit on minimum energy production is reached
            One should check on the post-proc that the total production is saturated by the limit for
            part of the time-range
            This tests is performed with the exp_min options on the mixes at energy and techno level
        '''
        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'
        func_manager_name = 'FunctionManagerDisc'
        repo = 'energy_models.sos_processes.energy.MDA'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_process_v0')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study_open(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        low_production_dict = {'Test.EnergyMix.energy_investment':
                               pd.DataFrame({'years': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030,
                                                       2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041,
                                                       2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050],
                                             'energy_investment': 0.0})}
        energy_list = values_dict[-1]['Test.energy_list']
        for energy in energy_list:
            for technology in usecase.techno_dict[energy]['value']:
                low_production_dict[f'Test.EnergyMix.{energy}.{technology}.invest_level'] = 10
                low_production_dict[f'Test.EnergyMix.{energy}.{technology}.initial_production'] = 0.0001
                low_production_dict[f'Test.EnergyMix.{energy}.{technology}.initial_age_distribution'] = pd.DataFrame({
                    'age': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
                    'distrib': 0.001})
                invest_before_ystart = self.ee.dm.get_value(
                    f'Test.EnergyMix.{energy}.{technology}.invest_before_ystart')
                invest_before_ystart['invest'] = 10
                low_production_dict[f'Test.EnergyMix.{energy}.{technology}.invest_before_ystart'] = invest_before_ystart

        ccs_list = values_dict[-1]['Test.ccs_list']
        del energy
        for energy in ccs_list:

            for technology in usecase.techno_dict[energy]['value']:
                low_production_dict[f'Test.CCUS.{energy}.{technology}.invest_level'] = 10
                low_production_dict[f'Test.CCUS.{energy}.{technology}.initial_production'] = 0.0001
                low_production_dict[f'Test.CCUS.{energy}.{technology}.initial_age_distribution'] = pd.DataFrame({
                    'age': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
                    'distrib': 0.001})
                invest_before_ystart = self.ee.dm.get_value(
                    f'Test.CCUS.{energy}.{technology}.invest_before_ystart')
                invest_before_ystart['invest'] = 10
                low_production_dict[f'Test.CCUS.{energy}.{technology}.invest_before_ystart'] = invest_before_ystart

        low_production_dict['Test.minimum_energy_production'] = 5e3

        values_dict.append(low_production_dict)

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)

        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-12
        full_values_dict[f'{name}.sub_mda_class'] = 'GSorNewtonMDA'
        full_values_dict[f'{name}.max_mda_iter'] = 50

        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        ppf = PostProcessingFactory()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.EnergyMix')[0]
        filters = ppf.get_post_processing_filters_by_discipline(disc)
        graph_list = ppf.get_post_processing_by_discipline(
            disc, filters, as_json=False)

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.EnergyMix')[0]
        energy_list = full_values_dict['Test.energy_list']

        inputs_names = [
            f'{name}.CO2_taxes']
        inputs_names.extend([
            f'{name}.{model_name}.{energy}.energy_prices' for energy in energy_list])
        inputs_names = [
            f'{name}.{model_name}.{energy}.energy_production' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']]
        inputs_names.extend(
            [f'{name}.{model_name}.{energy}.energy_consumption' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_consumption' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_production' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.syngas.syngas_ratio'])
        energy_mix_output = [f'{name}.{model_name}.energy_production',
                             f'{name}.{model_name}.co2_emissions_Gt',
                             f'{name}.{func_manager_name}.energy_production_objective',
                             f'{name}.{func_manager_name}.co2_emissions_objective',
                             f'{name}.{model_name}.energy_mean_price',
                             f'{name}.{model_name}.land_demand_df',
                             f'{name}.{func_manager_name}.primary_energies_production',
                             f'{name}.{func_manager_name}.total_prod_minus_min_prod_constraint_df',
                             f'{name}.CCS_price',
                             f'{name}.{model_name}.energy_prices_after_tax',
                             f'{name}.{func_manager_name}.co2_emissions_objective',
                             f'{name}.{func_manager_name}.energy_production_objective',
                             f'{name}.{func_manager_name}.primary_energies_production',
                             f'{name}.{func_manager_name}.carbon_storage_constraint']

        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energy_mix_outputs_limit.pkl',
                            discipline=disc, step=1.0e-16, derr_approx='complex_step', threshold=1e-3,
                            inputs=inputs_names, outputs=energy_mix_output)

    def _test_09_energy_mix_gradients_cutoff(self):
        '''
            Same test as test 08 except:
            this test is performed with the cutoffs options on the mixes at energy and techno level
        '''

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'
        func_manager_name = 'FunctionManagerDisc'
        repo = 'energy_models.sos_processes.energy.MDA'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_process_v0')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study_open(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        low_production_dict = {'Test.EnergyMix.energy_investment':
                               pd.DataFrame({'years': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030,
                                                       2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041,
                                                       2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050],
                                             'energy_investment': 0.0})}
        energy_list = values_dict[-1]['Test.energy_list']
        for energy_dict in values_dict:
            for key in energy_dict.keys():
                if 'technologies_list' in key:
                    try:
                        energy = [
                            energy for energy in energy_list if energy in key][0]
                        technologies_list = energy_dict[key]
                    except:
                        #energy is CCS
                        continue
            for technology in technologies_list:
                low_production_dict[f'Test.EnergyMix.{energy}.{technology}.invest_level'] = 10
                low_production_dict[f'Test.EnergyMix.{energy}.{technology}.initial_production'] = 0.0001
                low_production_dict[f'Test.EnergyMix.{energy}.{technology}.initial_age_distribution'] = pd.DataFrame({
                    'age': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
                    'distrib': 0.001})
                invest_before_ystart = self.ee.dm.get_value(
                    f'Test.EnergyMix.{energy}.{technology}.invest_before_ystart')
                invest_before_ystart['invest'] = 10
                low_production_dict[f'Test.EnergyMix.{energy}.{technology}.invest_before_ystart'] = invest_before_ystart
            low_production_dict[f'Test.EnergyMix.{energy}.exp_min'] = False

        low_production_dict[f'Test.EnergyMix.exp_min'] = False

        ccs_list = values_dict[-1]['Test.ccs_list']
        del energy
        technologies_list = []
        for energy_dict in values_dict:
            for key in energy_dict.keys():
                if 'technologies_list' in key:
                    try:
                        energy = [
                            energy for energy in ccs_list if energy in key][0]
                        technologies_list = energy_dict[key]
                    except:
                        #energy is CCS
                        continue
            for technology in technologies_list:
                low_production_dict[f'Test.CCUS.{energy}.{technology}.invest_level'] = 10
                low_production_dict[f'Test.CCUS.{energy}.{technology}.initial_production'] = 0.0001
                low_production_dict[f'Test.CCUS.{energy}.{technology}.initial_age_distribution'] = pd.DataFrame({
                    'age': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
                    'distrib': 0.001})
                invest_before_ystart = self.ee.dm.get_value(
                    f'Test.CCUS.{energy}.{technology}.invest_before_ystart')
                invest_before_ystart['invest'] = 10
                low_production_dict[f'Test.CCUS.{energy}.{technology}.invest_before_ystart'] = invest_before_ystart

        low_production_dict['Test.minimum_energy_production'] = 5e3
        values_dict.append(low_production_dict)

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)

        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-8
        full_values_dict[f'{name}.max_mda_iter'] = 50
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        ppf = PostProcessingFactory()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.EnergyMix')[0]
        filters = ppf.get_post_processing_filters_by_discipline(disc)
        graph_list = ppf.get_post_processing_by_discipline(
            disc, filters, as_json=False)

#         for graph in graph_list:
#             try:
#                 if graph.chart_name == 'Net Energies Total Production and Limit':
#                     graph.to_plotly().show()
#             except:
#                 pass

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.EnergyMix')[0]
        energy_list = full_values_dict['Test.energy_list']

        inputs_names = [
            f'{name}.CO2_taxes']
        inputs_names.extend([
            f'{name}.{model_name}.{energy}.energy_prices' for energy in energy_list])
        inputs_names = [
            f'{name}.{model_name}.{energy}.energy_production' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']]
        inputs_names.extend(
            [f'{name}.{model_name}.{energy}.energy_consumption' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_consumption' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_production' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.{model_name}.syngas.syngas_ratio'])
        energy_mix_output = [f'{name}.{model_name}.energy_production',
                             f'{name}.{model_name}.co2_emissions_Gt',
                             f'{name}.{func_manager_name}.energy_production_objective',
                             f'{name}.{func_manager_name}.co2_emissions_objective',
                             f'{name}.{model_name}.energy_mean_price',
                             f'{name}.{model_name}.land_demand_df',
                             f'{name}.{func_manager_name}.primary_energies_production',
                             f'{name}.{func_manager_name}.total_prod_minus_min_prod_constraint_df',
                             f'{name}.CCS_price',
                             f'{name}.{model_name}.energy_prices_after_tax',
                             f'{name}.{func_manager_name}.co2_emissions_objective',
                             f'{name}.{func_manager_name}.energy_production_objective',
                             f'{name}.{func_manager_name}.primary_energies_production',
                             f'{name}.{func_manager_name}.carbon_storage_constraint']

        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energy_mix_outputs_cutoff.pkl',
                            discipline=disc, step=1.0e-12, derr_approx='complex_step', threshold=1e-5,
                            inputs=inputs_names, outputs=energy_mix_output, parallel=self.parallel)

    def test_10_energy_mix_demand_dataframe(self):
        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'
        func_manager_name = 'FunctionManagerDisc'
        repo = 'energy_models.sos_processes.energy.MDA'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_process_v0')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study_open(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)

        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-8
        full_values_dict[f'{name}.max_mda_iter'] = 50
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.EnergyMix')[0]
        energy_list = full_values_dict['Test.energy_list']

        inputs_names = [
            f'{name}.{model_name}.{energy}.energy_consumption' for energy in energy_list]

        energy_mix_output = [f'{name}.{model_name}.All_Demand']
        #AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energy_mix_demand_df.pkl',
                            discipline=disc, step=1.0e-12, derr_approx='complex_step', threshold=1e-5,
                            inputs=inputs_names, outputs=energy_mix_output, parallel=self.parallel)

    def test_11_energy_mix_detailed_co2_emissions(self):

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'

        repo = 'energy_models.sos_processes.energy.MDA'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_process_v0')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study_open(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)

        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-12
        full_values_dict[f'{name}.max_mda_iter'] = 50
        #full_values_dict[f'{name}.sub_mda_class'] = 'MDANewtonRaphson'
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{name}.{model_name}')[0]
        energy_list = full_values_dict['Test.energy_list']

        inputs_names = [
            f'{name}.{model_name}.{energy}.energy_production' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']]
        inputs_names.extend(
            [f'{name}.{model_name}.{energy}.energy_consumption' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_consumption' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_production' for energy in ['carbon_capture', 'carbon_storage']])
        #AbstractJacobianUnittest.DUMP_JACOBIAN = True

        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energymix_detailed_co2_emissions.pkl',
                            discipline=disc, step=1.0e-16, derr_approx='complex_step',
                            inputs=inputs_names,  outputs=[f'{name}.{model_name}.co2_emissions',
                                                           f'{name}.{model_name}.co2_emissions_Gt',
                                                           f'{name}.FunctionManagerDisc.co2_emissions_objective',
                                                           f'{name}.{model_name}.ratio_available_carbon_capture'])

    def test_12_energy_mix_detailed_co2_emissions_ratio_available_capture(self):
        '''
        Test when the carbon capture needed by the technos (FT) is higher than the one rally captured
        '''
        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'

        repo = 'energy_models.sos_processes.energy.MDA'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_process_v0')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study_open(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)

        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-8
        full_values_dict[f'{name}.max_mda_iter'] = 50

        #full_values_dict[f'{name}.sub_mda_class'] = 'MDANewtonRaphson'
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{name}.{model_name}')[0]
        energy_list = full_values_dict['Test.energy_list']
        consumption_liquid_fuel = self.ee.dm.get_value(
            f'{name}.{model_name}.liquid_fuel.energy_consumption')
        consumption_liquid_fuel['carbon_capture (Mt)'] *= 1.0e6
        inputs_names = [
            f'{name}.{model_name}.{energy}.energy_production' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']]
        inputs_names.extend(
            [f'{name}.{model_name}.{energy}.energy_consumption' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_consumption' for energy in ['carbon_capture', 'carbon_storage']])
        inputs_names.extend(
            [f'{name}.CCUS.{energy}.energy_production' for energy in ['carbon_capture', 'carbon_storage']])
        #AbstractJacobianUnittest.DUMP_JACOBIAN = True

        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energymix_detailed_co2_emissions_ratio_available_capture.pkl',
                            discipline=disc, step=1.0e-16, derr_approx='complex_step',
                            inputs=inputs_names,  outputs=[f'{name}.{model_name}.co2_emissions',
                                                           f'{name}.{model_name}.co2_emissions_Gt',
                                                           f'{name}.FunctionManagerDisc.co2_emissions_objective',
                                                           f'{name}.{model_name}.ratio_available_carbon_capture'], parallel=self.parallel)

    def test_13_energy_mix_co2_per_use_gradients(self):
        '''
        Test CO2 per use gradients 
        '''
        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        name = 'Test'
        model_name = 'EnergyMix'
        func_manager_name = 'FunctionManagerDisc'
        repo = 'energy_models.sos_processes.energy.MDA'
        builder = self.ee.factory.get_builder_from_process(
            repo, 'energy_process_v0')

        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()
        usecase = Study_open(execution_engine=self.ee)
        usecase.study_name = self.name
        values_dict = usecase.setup_usecase()

        self.ee.display_treeview_nodes()
        full_values_dict = {}
        for dict_v in values_dict:
            full_values_dict.update(dict_v)

        full_values_dict[f'{name}.epsilon0'] = 1.0
        full_values_dict[f'{name}.tolerance'] = 1.0e-8
        full_values_dict[f'{name}.max_mda_iter'] = 50

        #full_values_dict[f'{name}.sub_mda_class'] = 'MDANewtonRaphson'
        self.ee.load_study_from_input_dict(full_values_dict)

        self.ee.execute()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{name}.{model_name}')[0]
        energy_list = full_values_dict['Test.energy_list']

        inputs_names = [
            f'{name}.{model_name}.{energy}.CO2_per_use' for energy in energy_list if energy not in ['carbon_capture', 'carbon_storage']]

        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_energymix_mix_co2_per_use_gradients',
                            discipline=disc, step=1.0e-16, derr_approx='complex_step',
                            inputs=inputs_names,  outputs=[f'{name}.{model_name}.energy_production',
                                                           f'{name}.{model_name}.co2_emissions_Gt',
                                                           f'{name}.{model_name}.co2_emissions',
                                                           f'{name}.{model_name}.energy_CO2_emissions',
                                                           f'{name}.{model_name}.energy_mean_price',
                                                           f'{name}.{model_name}.land_demand_df',
                                                           f'{name}.{func_manager_name}.primary_energies_production',
                                                           f'{name}.{func_manager_name}.total_prod_minus_min_prod_constraint_df',
                                                           f'{name}.CCS_price',
                                                           f'{name}.{model_name}.energy_prices_after_tax',
                                                           f'{name}.{func_manager_name}.co2_emissions_objective',
                                                           f'{name}.{func_manager_name}.energy_production_objective',
                                                           f'{name}.{func_manager_name}.primary_energies_production',
                                                           f'{name}.{model_name}.ratio_available_carbon_capture'], parallel=self.parallel)


if '__main__' == __name__:
    #AbstractJacobianUnittest.DUMP_JACOBIAN = True
    cls = EnergyMixJacobianTestCase()
    cls.setUp()
    cls.test_11_energy_mix_detailed_co2_emissions()