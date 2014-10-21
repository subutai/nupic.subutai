Introduction
============

A simple example showing how to use classification for detecting known
anomalies even if they occur again. There are two different methods shown here.

We generate data which consists of a sin wave with some regular artificially 
added anomalies.  The model initially shows this as anomalies, 
but then thanks to continuous learning the anomaly score goes to zero.
 
By using the anomaly classifier (a KNN classifier) we can explicitly store 
the state of the model at the time the anomaly occurs. If we do that we can 
detect the repeated occurrence of the anomalies, even though the anomaly 
score is zero. 

If you run the example, you will get a data file called anomaly_scores.csv  
This file contains the raw anomaly scores as one column. You will see that it
detects the anomaly but then goes to zero. In the anomalyLabel column you 
will see the anomalies that were detected by the classifier. In this column 
all the anomalies are detected. 
 
 
The code actually shows two different ways to do this. Please see the 
functions called classifyAnomaliesManually() and 
classifyAnomaliesAutomatically(). 