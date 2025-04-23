import pandas as pd
import numpy as np
import json


def compile_data_to_one_place(data, current_date=None):
  if current_data is None:
    current_date = data.orders['order_purchase_timestamp'].map(lambda x: pd.Timestamp(x)).max()

  with open('product_table.json') as f:
    product_table = json.load(f)

  with open('category_table.json') as f:
    product_clusters = json.load(f)

  geo = pd.read_csv('mean_zip.csv')
  geo.drop(columns=['city', 'state'], inplace=True)

  d = data.orders_items.copy()
  d['upper_category'] = d['product_id'].map(lambda x: product_table[x] if x in product_table else 'miss')
  d = d.merge(data.sellers[['seller_id', 'seller_zip_code_prefix']], how='left', on='seller_id')
  d.fillna({'seller_zip_code_prefix': 0.0}, inplace=True)

  tmp = d.groupby(['order_id', 'upper_category'], as_index=False)['price'].sum()
  idx = tmp.groupby('order_id')['price'].idxmax()
  result_cat = tmp.loc[idx].reset_index(drop=True)[['order_id', 'upper_category']]
  result_seller = d.groupby(['order_id'], as_index=False)['seller_zip_code_prefix'].first()
  d = result_cat.merge(result_seller, on='order_id')

  d = d.merge(data.order_reviews.drop_duplicates(subset=['order_id'])[['order_id', 'review_score']], on='order_id', how='inner')
  mean_score = d['review_score'].dropna().values.mean()
  d.fillna({'review_score': mean_score}, inplace=True)
  d = d.merge(data.order_payments.drop_duplicates(subset=['order_id'])[['order_id', 'payment_value']], on='order_id', how='inner')

  tmp_orders = data.orders.copy()
  tmp_orders = tmp_orders.merge(data.customers.drop(columns=['customer_city', 'customer_state']), on='customer_id').drop(columns=['order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date', 'customer_id'])
  tmp_orders = tmp_orders[~tmp_orders['order_status'].isin(['unavailable', 'canceled'])]
  tmp_orders = tmp_orders.drop(columns=['order_status'])
  tmp_orders['order_purchase_timestamp'] = tmp_orders['order_purchase_timestamp'].map(lambda x: pd.Timestamp(x))

  d = d.merge(tmp_orders, on='order_id', how='inner').drop(columns=['order_id'])



  tmp = d.groupby('customer_unique_id').count().reset_index()
  id_with_1_order = tmp[tmp['review_score'] == 1]['customer_unique_id'].values
  several_orders = d[~d['customer_unique_id'].isin(id_with_1_order)]
  collapsed_ds = pd.DataFrame(columns=several_orders.columns)
  for id, orders_group in several_orders.groupby('customer_unique_id'):
    orders_group = orders_group.sort_values(by='order_purchase_timestamp')
    collapsed_ds.loc[len(collapsed_ds)] = orders_group.iloc[0]
    cat_table = dict.fromkeys(product_clusters.keys(), 0.0)
    cat_table['miss'] = 0.0
    cat_table[collapsed_ds.iloc[-1]['upper_category']] = float(collapsed_ds.iloc[-1]['payment_value'])
    size = 1
    for i in range(1, orders_group.shape[0]):
      row = len(collapsed_ds) - 1
      t_delta = (orders_group.iloc[i]['order_purchase_timestamp'] - collapsed_ds.iloc[row]['order_purchase_timestamp']).days
      if t_delta >= 1 or i == orders_group.shape[0] - 1:
        collapsed_ds.at[row, 'review_score'] /= size
        size = 1
        collapsed_ds.at[row, 'upper_category'] = max(cat_table, key=cat_table.get)
        cat_table = dict.fromkeys(cat_table, 0.0)
        if  t_delta >= 1:
          collapsed_ds.loc[len(collapsed_ds)] = orders_group.iloc[i]
          cat_table[collapsed_ds.iloc[-1]['upper_category']] = float(collapsed_ds.iloc[-1]['payment_value'])
      else:
        cat_table[orders_group.iloc[i]['upper_category']] += orders_group.iloc[i]['payment_value']
        collapsed_ds.at[row, 'payment_value'] += float(orders_group.iloc[i]['payment_value'])
        collapsed_ds.at[row, 'review_score'] += orders_group.iloc[i]['review_score']
        size += 1

  tmp = collapsed_ds.groupby('customer_unique_id').count().reset_index()
  id_with_1_order_additional = tmp[tmp['review_score'] == 1]['customer_unique_id'].values
  one_order = d[d['customer_unique_id'].isin(np.concat([id_with_1_order, id_with_1_order_additional]))]

  one_order = one_order.merge(geo, how='left', left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix').drop(columns=['seller_zip_code_prefix', 'geolocation_zip_code_prefix'])
  one_order = one_order.rename(columns={'lat_d_mean':'s_lat_d', 'lng_d_mean':'s_lng_d'})
  one_order = one_order.merge(geo, how='left', left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix').drop(columns=['customer_zip_code_prefix', 'geolocation_zip_code_prefix'])
  one_order = one_order.rename(columns={'lat_d_mean':'c_lat_d', 'lng_d_mean':'c_lng_d'})
  mask = one_order[['s_lat_d', 's_lng_d', 'c_lat_d', 'c_lng_d']].isna().any(axis=1)
  one_order.loc[mask, ['s_lat_d', 's_lng_d', 'c_lat_d', 'c_lng_d']] = 0, 0, 0, 0
  one_order['distance'] = ((one_order['s_lat_d'] - one_order['c_lat_d'])**2 + (one_order['s_lng_d'] - one_order['c_lng_d'])**2)**0.5
  one_order.drop(columns=['s_lat_d', 's_lng_d', 'c_lat_d', 'c_lng_d'], inplace=True)
  one_order['time_delta'] = (current_date - one_order['order_purchase_timestamp']).map(lambda x: x.days)
  one_order['payment_value'] = np.log10(one_order['payment_value'].astype(float))
  one_order.drop(columns='order_purchase_timestamp', inplace=True)
  one_order = one_order.reindex(sorted(one_order.columns), axis=1)
  return one_order

  
if __name__ == '__main__':
  from clear_data_app.clear_data_frames import ClearDataFrames

  data = ClearDataFrames()
  data.clear_data()

  current_date = data.orders['order_purchase_timestamp'].map(lambda x: pd.Timestamp(x)).max()
  compiled_dataset = compile_data_to_one_place(data, current_date)