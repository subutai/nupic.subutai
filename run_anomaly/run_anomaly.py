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

"""
A simple client to run CLA anomaly detection using the OPF.
"""

from optparse import OptionParser
import sys
import csv
import math
import datetime
import dateutil.parser

from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic.frameworks.opf.predictionmetricsmanager import MetricsManager

import model_params

import anomaly_likelihood

def createModel():
  return ModelFactory.create(model_params.MODEL_PARAMS)


class AnomalyLikelihood(object):
  """
  Helper class for running anomaly likelihood computation.
  """
  
  def __init__(self, probationaryPeriod = 600, CLALearningPeriod = 300):
    """
    CLALearningPeriod - the number of iterations required for the CLA to
    learn some of the patterns in the dataset.
    
    probationaryPeriod - no anomaly scores are reported for this many
    iterations.  This should be CLALearningPeriod + some number of records
    for getting a decent likelihood estimation.
    
    """
    self._iteration          = 0
    self._historicalScores   = []
    self._distribution       = None
    self._probationaryPeriod = probationaryPeriod
    self._CLALearningPeriod  = CLALearningPeriod


  def _computeLogLikelihood(self, likelihood):
    """
    Compute a log scale representation of the likelihood value. Since the
    likelihood computations return low probabilities that often go into 4 9's or
    5 9's, a log value is more useful for visualization, thresholding, etc.
    """
    # The log formula is:
    # Math.log(1.0000000001 - likelihood) / Math.log(1.0 - 0.9999999999);
    return math.log(1.0000000001 - likelihood) / -23.02585084720009


  def likelihood(self, value, anomalyScore, dttm):
    """
    Given the current metric value, plus the current anomaly
    score, output the anomalyLikelihood for this record.
    """
    dataPoint = (dttm, value, anomalyScore)
    # We ignore the first probationaryPeriod data points
    if len(self._historicalScores) < self._probationaryPeriod:
      likelihood = 0.5
    else:
      # On a rolling basis we re-estimate the distribution every 100 iterations
      if self._distribution is None or (self._iteration % 100 == 0): 
        _, _, self._distribution = (
          anomaly_likelihood.estimateAnomalyLikelihoods(
            self._historicalScores,
            skipRecords = self._CLALearningPeriod)
          )
        
      likelihoods, _, self._distribution = (
        anomaly_likelihood.updateAnomalyLikelihoods([dataPoint],
          self._distribution)
      )
      likelihood = 1.0 - likelihoods[0]
      
    # Before we exit update historical scores and iteration
    self._historicalScores.append(dataPoint)
    self._iteration += 1

    return likelihood


def runAnomaly(options):
  """
  Create and run a CLA Model on the given dataset (based on the hotgym anomaly
  client in NuPIC).
  """
  
  # Update the min/max value for the encoder
  sensorParams = model_params.MODEL_PARAMS['modelParams']['sensorParams']
  sensorParams['encoders']['value']['maxval'] = options.max
  sensorParams['encoders']['value']['minval'] = options.min
  
  model = createModel()
  model.enableInference({'predictedField': 'value'})
  with open (options.inputFile) as fin:
    
    # Open file and setup headers
    reader = csv.reader(fin)
    csvWriter = csv.writer(open(options.outputFile,"wb"))
    csvWriter.writerow(["timestamp", "value",
                        "anomaly_score", "likelihood_score"])
    headers = reader.next()
    
    # The anomaly likelihood object
    anomalyLikelihood = AnomalyLikelihood()
    
    # Iterate through each record in the CSV file
    print "Starting processing at",datetime.datetime.now()
    for i, record in enumerate(reader, start=1):
      
      # Read the data and convert to a dict
      inputData = dict(zip(headers, record))
      inputData["value"] = float(inputData["value"])
      inputData["dttm"] = dateutil.parser.parse(inputData["dttm"])
      
      # Send it to the CLA and get back the raw anomaly score
      result = model.run(inputData)
      anomalyScore = result.inferences['anomalyScore']
      
      # Compute the Anomaly Likelihood
      likelihood = anomalyLikelihood.likelihood(inputData["value"],
                                                anomalyScore,
                                                inputData["dttm"]
                                                )

      # Write results to the CSV file
      csvWriter.writerow([inputData["dttm"], inputData["value"],
                          anomalyScore, likelihood])

      # Progress report
      if (i%500) == 0: print i,"records processed"

  print "Completed processing",i,"records at",datetime.datetime.now()
  print "Anomaly scores for",options.inputFile,
  print "have been written to",options.outputFile


if __name__ == "__main__":
  helpString = (
    "\n%prog [options] [uid]"
    "\n%prog --help"
    "\n"
    "\nRuns NuPIC anomaly detection on a csv file."
    "\nWe assume the data files have a timestamp field called 'dttm' and"
    "\na value field called 'value'. All other fields are ignored."
    "\nNote: it is important to set min and max properly according to data."
  )

  # All the command line options
  parser = OptionParser(helpString)
  parser.add_option("--inputFile",
                    help="Path to data file. (default: %default)", 
                    dest="inputFile", default="data/hotgym.csv")
  parser.add_option("--outputFile",
                    help="Output file. Results will be written to this file."
                    " (default: %default)", 
                    dest="outputFile", default="anomaly_scores.csv")
  parser.add_option("--max", default=100.0, type=float,
      help="Maximum number for the value field. [default: %default]")
  parser.add_option("--min", default=0.0, type=float,
      help="Minimum number for the value field. [default: %default]")
  
  options, args = parser.parse_args(sys.argv[1:])

  # Run it
  runAnomaly(options)



