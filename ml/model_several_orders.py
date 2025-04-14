# need sklearn 1.6.1
import numpy as np
import pandas as pd
from pathlib import Path
from pickle import load


def compile_info_about_customer(customer):
  rows = customer.shape[0]
  info = {
        'orders_count': rows,
        'last_score': customer.iloc[-1]['review_score'],
        'last_payment': customer.iloc[-1]['payment_value'],
        'last_days_between_orders': (customer.iloc[-1]['order_purchase_timestamp'] - customer.iloc[-2]['order_purchase_timestamp']).days if rows > 1 else np.nan, # rows > 1?
        'mean_score': customer.iloc[0:-1]['review_score'].mean() if rows > 1 else np.nan, # rows > 1?
        'mean_payment': customer.iloc[0:-1]['payment_value'].mean() if rows > 1 else np.nan, # rows > 1?
        'mean_days_between_orders': (customer.iloc[-2]['order_purchase_timestamp'] - customer.iloc[0]['order_purchase_timestamp']).days * 1.0 / (rows - 2) if rows > 2 else np.nan # rows > 2?
        }
  return info


def prepare_data_for_several_order_model(compiled_data, current_date):
  tmp = compiled_data.groupby('customer_unique_id').count().reset_index()
  id_with_ge2_orders = tmp[tmp['review_score'] > 1]['customer_unique_id'].values # dataset['review_score'] | we can use any column because they are same
  tmp_data = compiled_data[compiled_data['customer_unique_id'].isin(id_with_ge2_orders)]
  data = pd.DataFrame()

  for _, group in tmp_data.groupby('customer_unique_id'):
    group = group.sort_values(by='order_purchase_timestamp')
    i = group.shape[0] - 1
    row = compile_info_about_customer(group)
    row['days_after_order'] = (current_date - group.iloc[-1]['order_purchase_timestamp']).days

    if data.shape[0] == 0:
        data = pd.DataFrame(columns=row)
    data.loc[len(data)] = row

  return data


class SeveralOrdersModel:
  def __init__(self, models_dir=""):
    with open(Path(models_dir) / Path("sub_rfc.pkl"), "rb") as f:
        self.sub_rfc = load(f)
    with open(Path(models_dir) / Path("models/model_for_several_orders.pkl"), "rb") as f:
        self.several_orders_model = load(f)

  def predict(self, X):
    interim_data = pd.DataFrame(columns=['days_after_order', 'rfc'])
    interim_data['days_after_order'] = X['days_after_order']
    interim_data['rfc'] = self.sub_rfc.predict_proba(X.drop(columns=['days_after_order']))[:,1]
    preds = self.several_orders_model.predict(interim_data)
    return preds
  
  def predict_proba(self, X):
    interim_data = pd.DataFrame(columns=['days_after_order', 'rfc'])
    interim_data['days_after_order'] = X['days_after_order']
    interim_data['rfc'] = self.sub_rfc.predict_proba(X.drop(columns=['days_after_order']))[:,1]
    probas = self.several_orders_model.predict_proba(interim_data)[:, 1]
    return probas



if __name__ == '__main__':
  from clear_data_app.clear_data_frames import ClearDataFrames
  from utils import compile_data_to_one_place

  data = ClearDataFrames()
  data.clear_data()

  current_date = data.orders['order_purchase_timestamp'].map(lambda x: pd.Timestamp(x)).max()

  m = SeveralOrdersModel('./models')
  test_data = prepare_data_for_several_order_model(compile_data_to_one_place(data), current_date)
  print(m.predict(test_data))
