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
import unittest
from time import sleep
from shutil import rmtree
from pathlib import Path
from sostrades_core.execution_engine.execution_engine import ExecutionEngine
#from energy_models.sos_processes.energy.MDA.energy_process_v0_mda.usecase import Study
from climateeconomics.sos_processes.iam.witness.witness.usecase_witness_wo_damage_gdp_input import Study as Study
import cProfile
import pstats
from io import StringIO
from os.path import join, dirname
from sostrades_core.tools.post_processing.post_processing_factory import PostProcessingFactory



class PostProcessEnergy(unittest.TestCase):
    def setUp(self):
        """
        setup of test
        """
        self.study_name = 'post-processing'
        self.repo = 'climateeconomics.sos_processes.iam.witness' #'energy_models.sos_processes.energy.MDA'
        self.proc_name = 'witness' #'energy_process_v0'

        self.ee = ExecutionEngine(self.study_name)
        builder = self.ee.factory.get_builder_from_process(repo=self.repo,
                                                           mod_id=self.proc_name)

        self.ee.factory.set_builders_to_coupling_builder(builder)
        # Added directly to witness process
        # self.ee.post_processing_manager.add_post_processing_module_to_namespace('ns_witness',
        #     'climateeconomics.sos_wrapping.sos_wrapping_witness.post_proc_ssp_comparison.post_processing_ssp_comparison')
        self.ee.configure()
        self.usecase = Study()
        self.usecase.study_name = self.study_name
        values_dict = self.usecase.setup_usecase()
        for values_dict_i in values_dict:
            self.ee.load_study_from_input_dict(values_dict_i)
            #print('values_dict_i', values_dict_i)
        self.ee.load_study_from_input_dict({f'{self.study_name}.sub_mda_class': 'MDAGaussSeidel',
                                            f'{self.study_name}.max_mda_iter': 2})
        self.methane_ns = f'{self.study_name}.EnergyMix.methane'
        self.biogas_ns = f'{self.study_name}.EnergyMix.biogas'

        self.namespaceList = [self.methane_ns, self.biogas_ns]

    def test_post_processing_plots(self):
        """
        Test to check the generation of plots to compare WITNESS to IPCC SSP baseline scenarios 1-5
        """
        self.ee.execute()

        # self.usecase.static_dump_data('.', self.ee, DirectLoadDump())
        # from sostrades_core.tools.rw.load_dump_dm_data import DirectLoadDump
        # self.usecase.static_load_data('.', self.ee, DirectLoadDump())

        ppf = PostProcessingFactory()

        #for itm in self.namespaceList:
        filters = ppf.get_post_processing_filters_by_namespace(self.ee, self.biogas_ns)
        #print('self.model_name', self.ee, self.usecase.study_name)
        graph_list = ppf.get_post_processing_by_namespace(self.ee, self.biogas_ns, filters,
                                                          as_json=False)
        # for graph in graph_list:
        #     graph.to_plotly().show()


if '__main__' == __name__:
    cls = PostProcessEnergy()
    cls.setUp()
    cls.test_post_processing_plots()