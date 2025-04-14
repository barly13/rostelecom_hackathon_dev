import numpy as np
import pandas as pd

def compile_data_to_one_place(data):
  dataset = data.orders.copy()
  dataset = dataset.merge(data.customers.drop(columns=['customer_zip_code_prefix', 'customer_city', 'customer_state']), on='customer_id').drop(columns=['order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date'])
  dataset = dataset[~dataset['order_status'].isin(['unavailable', 'canceled'])]
  dataset = dataset.drop(columns=['order_status'])
  dataset['order_purchase_timestamp'] = dataset['order_purchase_timestamp'].map(lambda x: pd.Timestamp(x))
  dataset = dataset.merge(data.order_reviews[['order_id', 'review_score']], on='order_id', how='left')
  mean_score = dataset['review_score'].dropna().values.mean()
  dataset.fillna({'review_score': mean_score}, inplace=True)
  dataset = dataset.merge(data.order_payments.drop_duplicates(subset=['order_id'])[['order_id', 'payment_value']], on='order_id').drop(columns=['customer_id', 'order_id'])
  return dataset