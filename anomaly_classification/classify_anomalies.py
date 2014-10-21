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
A simple example showing how to use classification for detecting known
anomalies even if they occur again. There are two different methods shown here.
"""

import csv
import pprint

from nupic.data.datasethelpers import findDataset
from nupic.frameworks.opf.modelfactory import ModelFactory


import model_params

_DATA_PATH = "test1.csv"

_OUTPUT_PATH = "anomaly_scores.csv"

_ANOMALY_THRESHOLD = 0.9


def createModel():
  return ModelFactory.create(model_params.MODEL_PARAMS)


def classifyAnomaliesManually():
  """
  In this function we explicitly label specific portions of the data stream that
  we happen to know are anomalous. Any later record that matches the pattern
  will get labeled as "myAnomaly"
  """
  model = createModel()
  model.enableInference({'predictedField': 'sinx'})

  # Here we will get the classifier instance so we can add and query labels.
  classifierRegion = model._getAnomalyClassifier()
  classifierRegionPy = classifierRegion.getSelf()

  # We need to set this classification type. It is supposed to be the default
  # but is not for some reason.
  classifierRegionPy.classificationVectorType = 2

  with open (findDataset(_DATA_PATH)) as fin:
    reader = csv.reader(fin)
    headers = reader.next()
    csvWriter = csv.writer(open(_OUTPUT_PATH,"wb"))
    csvWriter.writerow(["x", "sinx", "anomaly_score", "anomalyLabel"])
    for i, record in enumerate(reader, start=1):
      modelInput = dict(zip(headers, record))
      modelInput["sinx"] = float(modelInput["sinx"])
      result = model.run(modelInput)
      anomalyScore = result.inferences['anomalyScore']
      anomalyLabel = result.inferences['anomalyLabel']

      # Convert the anomaly label into either 0 or 1
      if anomalyLabel == "[]":
        anomalyLabel = 0
      elif anomalyLabel == "['myAnomaly']":
        anomalyLabel = 1.0
        print "Anomaly detected at record",i

      # Manually tell the classifier to learn the first few artificial
      # anomalies. From there it should catch many of the following
      # anomalies, even though the anomaly sore might be low.
      if i == 2505:
        print "Adding labeled anomalies for record",i
        classifierRegion.executeCommand(["addLabel","2498","2503","myAnomaly"])
        anomalyLabel = 1.0

      if i == 2605:
        print "Adding labeled anomalies for record",i
        classifierRegion.executeCommand(["addLabel","2598","2603","myAnomaly"])
        anomalyLabel = 1.0

      if i == 2705:
        print "Adding labeled anomalies for record",i
        classifierRegion.executeCommand(["addLabel","2698","2703","myAnomaly"])
        anomalyLabel = 1.0

      csvWriter.writerow([i, modelInput["sinx"], anomalyScore, anomalyLabel])


  print "Anomaly scores have been written to",_OUTPUT_PATH
  print "The following labels were stored in the classifier:"
  labels = eval(classifierRegion.executeCommand(["getLabels"]))
  pprint.pprint(labels)



def classifyAnomaliesAutomatically():
  """
  In this function we use the automatic labeling feature. Here we can set an
  anomaly threshold. Any record whose anomaly score goes above the threshold
  is automatically sent to the classifier. Any later record that matches the
  pattern will get labeled as "Auto Threshold Classification (auto)"
  """
  model = createModel()
  model.enableInference({'predictedField': 'sinx'})

  # Setup the classifier to automatically classify records with
  # anomaly score >= 0.9
  classifierRegion = model._getAnomalyClassifier()
  classifierRegion.setParameter('anomalyThreshold',0.9)
  print "threshold for classifying anomalies is:", (
    classifierRegion.getParameter('anomalyThreshold'))

  with open (findDataset(_DATA_PATH)) as fin:
    reader = csv.reader(fin)
    headers = reader.next()
    csvWriter = csv.writer(open(_OUTPUT_PATH,"wb"))
    csvWriter.writerow(["x", "sinx", "anomaly_score", "anomalyLabel"])
    for i, record in enumerate(reader, start=1):
      modelInput = dict(zip(headers, record))
      modelInput["sinx"] = float(modelInput["sinx"])
      result = model.run(modelInput)
      anomalyScore = result.inferences['anomalyScore']
      anomalyLabel = result.inferences['anomalyLabel']

      # Convert the anomaly label into either 0 or 1
      if anomalyLabel == "[]":
        anomalyLabel = 0
      elif anomalyLabel == "['Auto Threshold Classification']":
        anomalyLabel = 1.0
      elif anomalyLabel == "['Auto Threshold Classification (auto)']":
        anomalyLabel = 1.0
      csvWriter.writerow([i, modelInput["sinx"], anomalyScore, anomalyLabel])

      if i>500 and anomalyScore > _ANOMALY_THRESHOLD:
        print "Anomaly detected at row [%d]. Anomaly score: %f." %(i,
                                                                 anomalyScore)

  print "Anomaly scores have been written to",_OUTPUT_PATH
  print "The following labels were stored in the classifier:"
  labels = eval(classifierRegion.executeCommand(["getLabels"]))
  pprint.pprint(labels)

if __name__ == "__main__":
  classifyAnomaliesManually()
  #classifyAnomaliesAutomatically()
