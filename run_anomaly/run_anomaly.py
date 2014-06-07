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
import json

from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic.frameworks.opf.predictionmetricsmanager import MetricsManager

from nupic.algorithms.anomaly_likelihood import AnomalyLikelihood

def runAnomaly(options):
  """
  Create and run a CLA Model on the given dataset (based on the hotgym anomaly
  client in NuPIC).
  """
  # Load the model params JSON
  with open("model_params.json") as fp:
    modelParams = json.load(fp)

  # Update the min/max value for the encoder
  sensorParams = modelParams['modelParams']['sensorParams']
  sensorParams['encoders']['value']['maxval'] = options.max
  sensorParams['encoders']['value']['minval'] = options.min

  model = ModelFactory.create(modelParams)
  model.enableInference({'predictedField': 'value'})
  with open (options.inputFile) as fin:
    
    # Open file and setup headers
    # Here we write the log likelihood value as the 'anomaly score'
    # The actual CLA outputs are labeled 'raw anomaly score'
    reader = csv.reader(fin)
    csvWriter = csv.writer(open(options.outputFile,"wb"))
    csvWriter.writerow(["timestamp", "value",
                        "raw anomaly score", "likelihood", "anomaly_score"])
    headers = reader.next()
    
    # The anomaly likelihood object
    anomalyLikelihood = AnomalyLikelihood()
    
    # Iterate through each record in the CSV file
    print "Starting processing at",datetime.datetime.now()
    for i, record in enumerate(reader, start=1):
      
      # Convert input data to a dict so we can pass it into the model
      inputData = dict(zip(headers, record))
      inputData["value"] = float(inputData["value"])
      inputData["dttm"] = dateutil.parser.parse(inputData["dttm"])
      
      # Send it to the CLA and get back the raw anomaly score
      result = model.run(inputData)
      anomalyScore = result.inferences['anomalyScore']
      
      # Compute the Anomaly Likelihood
      likelihood = anomalyLikelihood.anomalyProbability(
        inputData["value"], anomalyScore, inputData["dttm"])
      logLikelihood = anomalyLikelihood.computeLogLikelihood(likelihood)
      if likelihood > 0.9999:
        print "Anomaly detected:",inputData['dttm'],inputData['value'],likelihood

      # Write results to the output CSV file
      csvWriter.writerow([inputData["dttm"], inputData["value"],
                          anomalyScore, likelihood, logLikelihood])

      # Progress report
      if (i%1000) == 0: print i,"records processed"

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
                    dest="inputFile", default="data/cpu_cc0c5.csv")
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



