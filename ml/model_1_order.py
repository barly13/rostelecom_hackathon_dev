# need sklearn 1.6.1
import numpy as np
import pandas as pd
from pathlib import Path
from pickle import load
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression


def prepare_data_for_one_order_model(compiled_data, current_date):
  tmp = compiled_data.groupby('customer_unique_id').count().reset_index()
  id_with_1_order = tmp[tmp['review_score'] == 1]['customer_unique_id'].values
  data = compiled_data[compiled_data['customer_unique_id'].isin(id_with_1_order)].drop(columns=['customer_unique_id']).copy()
  data['days_after_order'] = (current_date - data['order_purchase_timestamp']).map(lambda x: x.days)
  data = data[['review_score', 'payment_value', 'days_after_order']]
  return data


class OneOrderModel:
  def __init__(self, model_dir=""):
    with open(Path(model_dir) / Path("models/model_for_1_order.pkl"), "rb") as f:
        self.one_order_model = load(f)

  def predict(self, X):
    return  self.one_order_model.predict(X)
  
  def predict_proba(self, X):
    return self.one_order_model.predict_proba(X)[:, 1]


if __name__ == '__main__':
  from clear_data_app.clear_data_frames import ClearDataFrames
  from utils import compile_data_to_one_place

  data = ClearDataFrames()
  data.clear_data()

  current_date = data.orders['order_purchase_timestamp'].map(lambda x: pd.Timestamp(x)).max()

  m = OneOrderModel('./models')
  test_data = prepare_data_for_one_order_model(compile_data_to_one_place(data), current_date)
  print(m.predict(test_data))