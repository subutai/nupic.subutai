Ensembles of HTM Models
=======================

This directory contains simple sample code for a predictor that is itself an 
ensemble of HTM models. The code runs 14 different HTM models on the 
Hotgym data. Individual HTM models are setup with various configurations. In
particular I varied the random number seed of the model and also randomly
changed the resolution of the scalar encoder. (See  the function createModel()
for the exact changes.) 

I used two different ensemble techniques. The "average ensemble" makes a
prediction that is simply the average of the individual model predictions.  The
"least squares ensemble" fits a rolling least square model of the  individual
predictions to the data. This essentially allows one to use the best (non 
uniform) averaging weights.


Results
=======

I measured the mean squared error for the last 2000 records. The individual 
model errors varied from 113 to 141.  The standard deviation of the errors 
varied from 285 to 420.

The "average ensemble" got an error of 84.5, which is almost 30 better than  the
best individual model. The standard deviation was also a lot better, at 200. 
The "least squares" ensemble got an error of 75,  which is 38 better than the 
best individual. The standard deviation was 183. 

Both simple ensembles therefore produce more accurate and tighter predictions
than any individual model.

I also looked at how an "optimal ensemble" would perform. Suppose you knew 
exactly which HTM model had the best prediction at each time step. How well 
could this ensemble perform?  This one has an error of 28,  which is far better
than anything above.  This shows that  there might still be quite a bit more 
room for improvement if you could create a better model selector.


Discussion
==========

This simple experiment shows that the basic machine learning rule of thumb of
using ensembles to improve performance applies to HTMs as well. You can get a
pretty decent improvement with simple ensembles even for streaming predictions.
The downside of course is the significant extra CPU cost of running all these
individual models.
 
I used  very simple ensembles here.  The optimal ensemble result suggests  that
there could be additional significant improvements possible.  A more complex
investigation could  involve looking at more sophisticated  techniques like
ADABOOST, pruning,  etc. You might want to look at using an  SVM or other
classifier (possible with some additional feature such as the  timestamp) to
select the HTM.    In addition  I would  recommend  fiddling  with a lot more
parameters than random seed and scalar encoder resolution. This will increase
the diversity of the individual models and should lead to better  results.

Cells near BG4306 in the attached spreadsheet contains a summary of the results.

Other notes: I ran 21 models and achieved incrementally better results than the 
above.  I also looked at MAPE error. The average ensemble had a better MAPE 
error. This is not too surprising since the least squares approach optimizes 
squared error. In general averaging is a very good simple default technique.


Here are some intro papers on ensembles and boosting:

[1] http://users.rowan.edu/~polikar/RESEARCH/PUBLICATIONS/csm06.pdf

[2] http://www.boosting.org/papers/MeiRae03.pdf

