# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 19:30:11 2021

@author: Lance
"""

# Use this to import from another directory.
import sys
sys.path.insert(1, "..\\lendres\\")

import lendres
import lendres.Data
import lendres.Console

data = lendres.Data.LoadAndInspectData("datawitherrors.csv")
