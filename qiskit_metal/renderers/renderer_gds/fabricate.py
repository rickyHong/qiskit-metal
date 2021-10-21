# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
"""Edit gdspy library for fabrication.  This class should be instantiated
by for each layer since each layer can be either a positive or negative mask.

To be used by QGDSRenderer only.
"""

import logging
from typing import Union
import gdspy


class Fabricate():

    def __init__(self, lib: gdspy.GdsLibrary, chip_name: str, layer: int):
        self.lib = lib
        self.chip_name = chip_name
        self.layer = layer
        self.neg_datatype = None
        self.pos_datatype = None
        self.nocheese_sub_layer = None
        self.cheese_sub_layer = None
        self.top_name = 'TOP'

    def fabricate_negative_mask(self,
                                neg_datatype: int,
                                nocheese_sub_layer: int,
                                cheese_sub_layer: int,
                                top_name: str = 'TOP'):
        self.neg_datatype = neg_datatype
        self.nocheese_sub_layer = nocheese_sub_layer
        self.cheese_sub_layer = cheese_sub_layer
        self.top_name = top_name

        cell_layer = self._both_pos_and_neg_masks()
        self._unique_neg_fab(cell_layer)

        a = 5  # for breakpoint

    def fabricate_positive_mask(self,
                                pos_datatype: int,
                                nocheese_sub_layer: int,
                                cheese_sub_layer: int,
                                top_name: str = 'TOP'):
        self.pos_datatype = pos_datatype
        self.nocheese_sub_layer = nocheese_sub_layer
        self.cheese_sub_layer = cheese_sub_layer
        self.top_name = top_name

        cell_layer = self._both_pos_and_neg_masks()

        self._unique_pos_fab(cell_layer)

        a = 5  # for breakpoint

    def _unique_pos_fab(self, cell_layer: gdspy.library.Cell):
        self._remove_cheese_diff_cell()

        #There may or may not be cheesing.

        cell_with_cheese = self._get_cheese_cell()
        if cell_with_cheese is None:
            # Cheesing didn't happen
            a = 5  # for breakpoint
            #datatypes_in_cell = cell_layer.get_datatypes()  #returns a set.
            cell_layer.flatten(
                single_layer=self.layer,
                single_datatype=self.pos_datatype,
                single_texttype="Flatten datatype 0 and Cheese_diff.")
            self._remove_no_subtract_cell()
            a = 5  # for breakpoint
        else:
            # Cheesing happened

            a = 5  # for breakpoint

        a = 5  # for breakpoint

    def _unique_neg_fab(self, cell_layer: gdspy.library.Cell):

        # flatten the cells with datatype 0 and Cheese_diff and put into self.neg_datatype

        cell_layer.flatten(
            single_layer=self.layer,
            single_datatype=self.neg_datatype,
            single_texttype="Flatten datatype 0 and Cheese_diff.")

        self._remove_cheese_diff_cell()

    def _both_pos_and_neg_masks(self) -> gdspy.library.Cell:
        self._remove_nocheese_cell()
        self._remove_onehole_cell()

        cell_name = f'{self.top_name}_{self.chip_name}_{self.layer}'
        cell_layer = self.lib.cells[cell_name]
        return cell_layer

    def _get_cheese_cell(self) -> gdspy.library.Cell:
        cell_name_with_cheese = f'{self.top_name}_{self.chip_name}_{self.layer}_Cheese_{self.cheese_sub_layer}'
        if cell_name_with_cheese in self.lib.cells:
            return self.lib.cells[cell_name_with_cheese]
        else:
            return None

    def _remove_no_subtract_cell(self):
        cell_name = f'{self.top_name}_{self.chip_name}_{self.layer}_no_subtract'
        if cell_name in self.lib.cells:
            self.lib.remove(cell_name)

    def _remove_onehole_cell(self):
        cell_name = f'{self.top_name}_{self.chip_name}_{self.layer}_one_hole'
        if cell_name in self.lib.cells:
            self.lib.remove(cell_name)

    def _remove_nocheese_cell(self):
        cell_name = f'{self.top_name}_{self.chip_name}_{self.layer}_NoCheese_{self.nocheese_sub_layer}'
        if cell_name in self.lib.cells:
            self.lib.remove(cell_name)

    def _remove_cheese_diff_cell(self):
        cell_name = f'{self.top_name}_{self.chip_name}_{self.layer}_Cheese_diff'
        if cell_name in self.lib.cells:
            self.lib.remove(cell_name)
