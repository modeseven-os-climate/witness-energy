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

from energy_models.sos_processes.witness_sub_process_builder import WITNESSSubProcessBuilder
from energy_models.core.energy_process_builder import INVEST_DISCIPLINE_OPTIONS


class ProcessBuilder(WITNESSSubProcessBuilder):
    def get_builders(self):
        coupling_name = "EnergyModelEval"
        designvariable_name = "DesignVariableDisc"
        func_manager_name = "FunctionManagerDisc"
        self.invest_discipline = INVEST_DISCIPLINE_OPTIONS[0]
        # retrieve energy process
        chain_builders = self.ee.factory.get_builder_from_process(
            'energy_models.sos_processes.energy.MDA', 'energy_process_v0',
            techno_dict=self.techno_dict, invest_discipline=self.invest_discipline)

        # design variables builder
        design_var_path = 'energy_models.core.design_variables_translation_bspline.design_var_disc.Design_Var_Discipline'
        design_var_builder = self.ee.factory.get_builder_from_module(
            f'{designvariable_name}', design_var_path)
        chain_builders.append(design_var_builder)

        # function manager builder
        fmanager_path = 'sos_trades_core.execution_engine.func_manager.func_manager_disc.FunctionManagerDisc'
        fmanager_builder = self.ee.factory.get_builder_from_module(
            f'{func_manager_name}', fmanager_path)
        chain_builders.append(fmanager_builder)

        # modify namespaces defined in the child process
        for ns in self.ee.ns_manager.ns_list:
            self.ee.ns_manager.update_namespace_with_extra_ns(
                ns, coupling_name, after_name=self.ee.study_name)

        ns_dict = {'ns_optim': f'{self.ee.study_name}'}
        self.ee.ns_manager.add_ns_def(ns_dict)

        # create coupling builder
        coupling_builder = self.ee.factory.create_builder_coupling(
            coupling_name)
        coupling_builder.set_builder_info('cls_builder', chain_builders)
        coupling_builder.set_builder_info('with_data_io', True)

        return coupling_builder
