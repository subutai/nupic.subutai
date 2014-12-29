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

"""A simple client to create a CLA model for hotgym."""

import csv
import copy
import datetime
import numpy

from nupic.data.datasethelpers import findDataset
from nupic.frameworks.opf.modelfactory import ModelFactory

import model_params


_DATA_PATH = "extra/hotgym/rec-center-hourly.csv"

#_NUM_RECORDS = 2000
_NUM_RECORDS = 4300


def createModel(seed=1956):
  params = model_params.MODEL_PARAMS
  params['modelParams']['spParams']['seed'] = seed

  # Randomly change encoder resolution to be in [0.78, 0.98], i.e. 0.88 +/- 0.1
  params['modelParams']['sensorParams']['encoders']['consumption'][
    'resolution'] = 0.78 + numpy.random.random()*.2

  return ModelFactory.create(model_params.MODEL_PARAMS)


def setupModel(model):
  model.enableInference({'predictedField': 'consumption'})


def runHotgym():
  models = []
  previousPredictions = []
  bestPrediction = 0.0
  lstPrediction = 0.0

  # Setup all the models. Here each model has a different SP seed.
  for i in range(14):
    models.append(createModel(1956+i))

  for m in models:
    setupModel(m)
    previousPredictions.append(0.0)

  # The best least squares predictor. Initialize with 1.0/len(models)
  bestFit = numpy.ones(len(models)) / len(models)

  print "Running ensemble with",len(models),"models. This could take a while!"

  # Matrix to hold the last month's worth of predictions and actuals
  lstNumRows = 2000
  a = numpy.zeros((lstNumRows,len(models)))
  b = numpy.zeros(lstNumRows)

  with open("output.csv","wb") as outputFile:
    csvWriter = csv.writer(outputFile)
    csvWriter.writerow(["timestamp", "consumption", "predictions"])
    with open (findDataset(_DATA_PATH)) as fin:
      reader = csv.reader(fin)
      headers = reader.next()
      reader.next()
      reader.next()
      for i, record in enumerate(reader, start=1):

        # Prepare input dict for feeding each model
        modelInput = dict(zip(headers, record))
        modelInput["consumption"] = float(modelInput["consumption"])
        modelInput["timestamp"] = datetime.datetime.strptime(
            modelInput["timestamp"], "%m/%d/%y %H:%M")

        # Run each model and get each prediction and running sum
        results = []
        predictions = []
        sum = 0
        lstSum = 0
        for k,m in enumerate(models):
          result = m.run(modelInput)
          prediction = result.inferences["multiStepBestPredictions"][1]
          results.append(result)
          predictions.append(prediction)
          sum += prediction
          lstSum += bestFit[k]*prediction

        # # Write results to the output CSV file
        if i>1:
          row = [modelInput["timestamp"], modelInput["consumption"]]
          row.extend(previousPredictions)
          row.append(bestPrediction)
          row.append(lstPrediction)
          csvWriter.writerow(row)

          # Keep a rolling store of the last lstNumRows of predictions and
          # actuals
          a[i%lstNumRows] = previousPredictions
          b[i%lstNumRows] = modelInput["consumption"]
          # Redo the least squares estimate on the last lstNumRows every week
          if (i > 300 + lstNumRows) and ( i% 24*7 == 0):
            print "Iteration: %d, doing least squares fit using " \
                  "the last %d predictions!" % (i,lstNumRows)
            x = numpy.linalg.lstsq(a,b)
            bestFit = x[0]
            # Print the weights and the average residual squared error
            print bestFit,x[1][0]/lstNumRows


        # Compute best prediction (to be used next timestamp)
        # Save current predictions for later output. This shifts the
        # predictions so that they are lined up with the timestamps they are
        # actually predicting.
        previousPredictions = copy.deepcopy(predictions)
        bestPrediction = sum / len(models)
        lstPrediction = lstSum

        if i%200 == 0: print "iteration:",i
        if i == _NUM_RECORDS:
          break


if __name__ == "__main__":
  runHotgym()
