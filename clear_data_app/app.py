from clear_data_frames import ClearDataFrames
from db_uploader import Uploader

uploader = Uploader()

# uploader.clear_data_in_tables()

dfs = ClearDataFrames()
dfs.load_data()
dfs.clear_data()

# uploader.upload_df_to_sql(dfs.product_category_name_translation, 'product_category_name_translation')
# uploader.upload_df_to_sql(dfs.products, 'products')
# uploader.upload_df_to_sql(dfs.customers, 'customers')
# uploader.upload_df_to_sql(dfs.orders, 'orders')
# uploader.upload_df_to_sql(dfs.order_reviews, 'order_reviews')
# uploader.upload_df_to_sql(dfs.order_payments, 'order_payments')
# uploader.upload_df_to_sql(dfs.sellers, 'sellers')
# uploader.upload_df_to_sql(dfs.geolocation, 'geolocation')
# uploader.upload_df_to_sql(dfs.orders_items, 'orders_items')

uploader.save_data_in_dir(dfs.product_category_name_translation, 'product_category_name_translation')
uploader.save_data_in_dir(dfs.products, 'products')
uploader.save_data_in_dir(dfs.customers, 'customers')
uploader.save_data_in_dir(dfs.orders, 'orders')
uploader.save_data_in_dir(dfs.order_reviews, 'order_reviews')
uploader.save_data_in_dir(dfs.order_payments, 'order_payments')
uploader.save_data_in_dir(dfs.sellers, 'sellers')
uploader.save_data_in_dir(dfs.geolocation, 'geolocation')
uploader.save_data_in_dir(dfs.orders_items, 'orders_items')