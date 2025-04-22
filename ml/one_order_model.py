import numpy as np
import pandas as pd
from pathlib import Path
from pickle import load
from sklearn.ensemble import RandomForestClassifier

class OneOrderModel:
  def __init__(self, model=None, labels=None):
    if not model:
      model = 'models/rfc.pkl'
    with open(model, 'rb') as f:
        self.one_order_model = load(f)

    if not labels:
      labels = 'cluster_table.csv'
    df = pd.read_csv(labels, index_col=0)
    d = df.to_dict("split")
    self.labels = dict(zip(d["index"], [di[0] for di in d["data"]]))

  def predict(self, X):
    data = X.copy()
    customers = X['customer_unique_id'].to_frame()
    data.drop(columns=['customer_unique_id'], inplace=True)
    data = pd.get_dummies(data, columns=['upper_category'], dtype = float)
    customers['probability'] = pd.Series(self.one_order_model.predict(data))
    customers['probability'] = customers['probability'].map(lambda x: self.labels[x])
    return customers

# usage
# m = OneOrderModel()
# m.predict(data)