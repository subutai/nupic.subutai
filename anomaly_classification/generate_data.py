#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""A simple script to generate a CSV with artificial data."""

import csv
import math
import numpy

def generateData():
  """
  """
  fileHandle = open("data/test1.csv","w")
  writer = csv.writer(fileHandle)
  writer.writerow(["x","sinx"])

  prev = 0.0
  for i in range(4000):
    x = (i * math.pi) / 50.0
    m1 = math.sin(x)

    # Add an artificial repeating anomaly after a while
    if i >= 2450:
      position = x % (2*math.pi)
      if position >= 6.1 or position <= 0.2:
        m1 += 1.5
        print "Anomaly at:",i, x, m1

    writer.writerow([x,m1])
    
  fileHandle.close()
  

if __name__ == "__main__":
  generateData()
