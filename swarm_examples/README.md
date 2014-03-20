
An example demonstrating swarming for anomaly detection models, using multiple
fields. We assume you have read the following wiki page:

https://github.com/numenta/nupic/wiki/Running-Swarms


Files
=====

The data file is contained in the `data` subdirectory.  It contains an x
value plus the following fields.

metric1 contains sin(x).

metric2 contains sin(x(t-1)). In other words metric1 will be a perfect predictor
of metric2 at time x+1.

metric3 is metric 1 plus about 10% noise.

metric4 is random noise

metric5 is metric4 from the previous time step. In other words, metric4 is
going to be a perfect predictor for metric5, even though the signal is random.

The script `generate_data.py` was used to create the data file. You can modify
the script if you want to try different variations.


Basic swarm with one field
==========================

Run a basic swarm using the following command:

```
%> run_swarm.py basic_search_def.json --overwrite --maxWorkers 5
```

Note: The argument to maxWorkers controls the level of parallelism used
in the swarm. If you specify 5 it will launch 5 simultaneous processes. Usually
you want to set this to the number of cores you have on your system.

This will produce a lot of output (see
https://github.com/numenta/nupic/wiki/Running-Swarms for an explanation of the
output).  For now look for lines at the end which look something like this:

```
Best results on the optimization metric multiStepBestPredictions:multiStep:errorMetric='altMAPE':steps=[1]:window=1000:field=metric1 (maximize=False):
[69] Experiment _GrokModelInfo(jobID=1037, modelID=3428, status=completed, completionReason=eof, updateCounter=22, numRecords=1500) (modelParams|clParams|alpha_0.0201204914671.modelParams|tpParams|minThreshold_10.modelParams|tpParams|activationThreshold_13.modelParams|tpParams|pamLength_2.modelParams|sensorParams|encoders|metric2:n_106.modelParams|sensorParams|encoders|metric1:n_494.modelParams|spParams|synPermInactiveDec_0.0838352357968):
  multiStepBestPredictions:multiStep:errorMetric='altMAPE':steps=[1]:window=1000:field=metric1:    1.63305668121
```

This shows the error from the best model discovered by the swarm. It tells us
that the MAPE error for the best model was 1.633%. (Note: your results may be
slightly different due to randomness.)

In addition it will produce a directory called `model_0` which contains
the parameters of the best CLA model. Now, run this model on the dataset to get
all the predictions:

```
%> python $NTA/share/opf/bin/OpfRunExperiment.py model_0
```

This will produce an output file called
`model_0/inference/DefaultTask.TemporalAnomaly.predictionLog.csv`

You can plot the x column against the fields 'metric1' and
multiStepBestPredictions.1 to show the actual vs predicted values.
The image basic_results.jpg shows an example of this.


Multiple fields example 1
=========================

The file `multi1_search_def.json` contains parameters that will tell the swarm to
searh all field combinations. In this case we will still predict the same
field, metric1 but it will try to see if any other fields help improve the error.

```
%> run_swarm.py multi1_search_def.json --overwrite --maxWorkers 5
```

```
Field Contributions:
{   u'metric1': 0.0,
    u'metric2': 24.248407536411587,
    u'metric3': -43.99394069125886,
    u'metric4': -266.9527814828809,
    u'metric5': -216.28549625834893}
```






Multiple fields example 2:
=========================


The file `test3_search_def.json` contains parameters that will tell the swarm to
searh all field combinations. In this case we will tell the CLA predict the
field, metric2. Now remember that metric2 is just metric1 from the previous
time step.

```
%> run_swarm.py test3_search_def.json --overwrite --maxWorkers 5
```

```
Best results on the optimization metric multiStepBestPredictions:multiStep:errorMetric='altMAPE':steps=[1]:window=1000:field=metric2 (maximize=False):
[46] Experiment _GrokModelInfo(jobID=1038, modelID=3566, status=completed, completionReason=eof, updateCounter=22, numRecords=1500) (modelParams|clParams|alpha_0.0351293137955.modelParams|tpParams|minThreshold_10.modelParams|tpParams|activationThreshold_13.modelParams|tpParams|pamLength_2.modelParams|sensorParams|encoders|metric2:n_500.modelParams|sensorParams|encoders|metric1:n_145.modelParams|spParams|synPermInactiveDec_0.0771153642407):
  multiStepBestPredictions:multiStep:errorMetric='altMAPE':steps=[1]:window=1000:field=metric2:    0.913722715504
```


Field Contributions:
{   u'metric1': 58.04834257521399,
    u'metric2': 0.0,
    u'metric3': -8.9984071264884,
    u'metric4': -169.10294900144498,
    u'metric5': -269.60989468137325}
    



Multiple fields example 3:

Predict metric 5. This is a case where there is complete noise but strong
temporal correlation.

```
%> run_swarm.py test4_search_def.json --overwrite --maxWorkers 5
```

Field Contributions:
{   u'metric1': -2.3055948655605376,
    u'metric2': -0.5331590138027453,
    u'metric3': -2.4612375287911568,
    u'metric4': 91.73137670780368,
    u'metric5': 0.0}

Best results on the optimization metric multiStepBestPredictions:multiStep:errorMetric='altMAPE':steps=[1]:window=1000:field=metric5 (maximize=False):
[53] Experiment _GrokModelInfo(jobID=1039, modelID=3800, status=completed, completionReason=eof, updateCounter=22, numRecords=1500) (modelParams|sensorParams|encoders|metric4:n_104.modelParams|sensorParams|encoders|metric5:n_193.modelParams|clParams|alpha_0.0001.modelParams|tpParams|minThreshold_9.modelParams|tpParams|activationThreshold_12.modelParams|tpParams|pamLength_2.modelParams|spParams|synPermInactiveDec_0.1):
  multiStepBestPredictions:multiStep:errorMetric='altMAPE':steps=[1]:window=1000:field=metric5:    6.96976944652
