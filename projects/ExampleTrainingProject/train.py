# Databricks notebook source
#import numpy as np
#dbutils.widgets.removeAll()
#dbutils.widgets.dropdown("alpha", "0.5", [str(x)[:3] for x in np.arange(0,1.1,0.1)])
#dbutils.widgets.dropdown("l1_ratio", "0.5", [str(x)[:3] for x in np.arange(0,1.1,0.1)])

# COMMAND ----------

# MAGIC %md
# MAGIC # Training the Model
# MAGIC First, train a linear regression model that takes two hyperparameters: *alpha* and *l1_ratio*.
# MAGIC
# MAGIC > The data set used in this example is from http://archive.ics.uci.edu/ml/datasets/Wine+Quality
# MAGIC > P. Cortez, A. Cerdeira, F. Almeida, T. Matos and J. Reis.
# MAGIC > Modeling wine preferences by data mining from physicochemical properties. In Decision Support Systems, Elsevier, 47(4):547-553, 2009.

# COMMAND ----------

import os
import warnings
import sys

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet

import logging
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

# COMMAND ----------

import mlflow
import mlflow.sklearn

# COMMAND ----------

def eval_metrics(actual, pred):
  rmse = np.sqrt(mean_squared_error(actual, pred))
  mae = mean_absolute_error(actual, pred)
  r2 = r2_score(actual, pred)
  return rmse, mae, r2

# COMMAND ----------

# Checking wheel availability
import mylib.simple_file as sp
print(sp.say_hello())

try:
  alpha = float(dbutils.widgets.getArgument("alpha"))
except:
  alpha = 0.5
try:
  l1_ratio = float(dbutils.widgets.getArgument("l1_ratio"))
except:
  l1_ratio = 0.5

model_name = sys.argv[1] if len(sys.argv) > 1 and not ('PythonShell' in sys.argv[0]) else "model"

print(model_name)
print(sys.argv)

# add a way to execute the notebook from databricks directly

# if not ('MLFLOW_RUN_ID' in os.environ):
#  mlflow.set_experiment("/Shared/databricks_experiment_train")

# COMMAND ----------

warnings.filterwarnings("ignore")
np.random.seed(40)

# Read the wine-quality csv file from the URL
csv_url =\
  'http://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv'
try:
  data = pd.read_csv(csv_url, sep=';')
except Exception as e:
  logger.exception("Unable to download training & test CSV, check your internet connection. Error: %s", e)
  # Forcing code to exit since we do not have access to http://archive.ics.uci.edu
  # exit(0)

# Split the data into training and test sets. (0.75, 0.25) split.
train, test = train_test_split(data)

# The predicted column is "quality" which is a scalar from [3, 9]
train_x = train.drop(["quality"], axis=1)
test_x = test.drop(["quality"], axis=1)
train_y = train[["quality"]]
test_y = test[["quality"]]

# COMMAND ----------
with mlflow.start_run():
  lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
  lr.fit(train_x, train_y)

  predicted_qualities = lr.predict(test_x)

  (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

  print("Elasticnet model (alpha=%f, l1_ratio=%f):" % (alpha, l1_ratio))
  print("  RMSE: %s" % rmse)
  print("  MAE: %s" % mae)
  print("  R2: %s" % r2)

  mlflow.log_param("alpha", alpha)
  mlflow.log_param("l1_ratio", l1_ratio)
  mlflow.log_metric("rmse", rmse)
  mlflow.log_metric("r2", r2)
  mlflow.log_metric("mae", mae)

  mlflow.sklearn.log_model(lr, model_name, registered_model_name=model_name)
