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

from energy_models.core.techno_type.base_techno_models.electricity_techno import ElectricityTechno


class SolarThermal(ElectricityTechno):

    def compute_other_primary_energy_costs(self):
        """
        Compute primary costs which depends on the technology 
        """
        return 0

    def compute_land_use(self):
        '''
        Compute required land for solar_pv
        '''
        density_per_ha = self.techno_infos_dict['density_per_ha']

        self.techno_land_use[f'{self.name} (Gha)'] = \
            self.production[f'{self.energy_name} ({self.product_energy_unit})'] / \
            density_per_ha