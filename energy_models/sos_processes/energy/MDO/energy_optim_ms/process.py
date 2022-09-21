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
from sos_trades_core.sos_processes.base_process_builder import BaseProcessBuilder


class ProcessBuilder(BaseProcessBuilder):

    # ontology information
    _ontology_data = {
        'label': 'Energy Optimisation Multi-Scenario Process',
        'description': '',
        'category': '',
        'version': '',
    }

    def get_builders(self):

        # scenario build map
        scenario_map = {'input_name': 'scenario_list',

                        'input_ns': 'ns_scatter_scenario',
                        'output_name': 'scenario_name',
                        'scatter_ns': 'ns_scenario',
                        'gather_ns': 'ns_scatter_scenario',
                        'ns_to_update': ['ns_syngas', 'ns_flue_gas', 'ns_energy_study', 'ns_energy_mix', 'ns_optim', 'ns_functions']}

        self.ee.smaps_manager.add_build_map(
            'scenario_list', scenario_map)

        builder_cdf_list = self.ee.factory.get_builder_from_process(
            'energy_models.sos_processes.energy.MDO', 'energy_optim_process')

        scatter_scenario_name = 'Multi-scenarios'
        # modify namespaces defined in the child process
        self.ee.ns_manager.update_namespace_list_with_extra_ns(
            scatter_scenario_name, after_name=self.ee.study_name)

        # Add new namespaces needed for the scatter multiscenario
        ns_dict = {'ns_scatter_scenario': f'{self.ee.study_name}.{scatter_scenario_name}',
                   'ns_post_processing': f'{self.ee.study_name}.Post_processing'}

        self.ee.ns_manager.add_ns_def(ns_dict)

        multi_scenario = self.ee.factory.create_very_simple_multi_scenario_builder(
            scatter_scenario_name, 'scenario_list', [builder_cdf_list], autogather=True, gather_node='Post-processing')

        mod_list = 'energy_models.core.trades_discipline.trades_discipline.TradesDiscipline'
        pareto_builder = self.ee.factory.get_builder_from_module(
            'Post-processing', mod_list)
        multi_scenario.append(pareto_builder)

        return multi_scenario
