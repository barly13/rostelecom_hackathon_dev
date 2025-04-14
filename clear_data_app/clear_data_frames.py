import os

import numpy as np
import pandas as pd


class ClearDataFrames:
    def __init__(self):
        self.customers = None
        self.geolocation = None
        self.order_payments = None
        self.order_reviews = None
        self.orders = None
        self.orders_items = None
        self.product_category_name_translation = None
        self.products = None
        self.sellers = None

    def load_data(self):
        self.customers = pd.read_csv('./data/customers.csv') if os.path.exists('./data/customers.csv') \
            else pd.read_csv('data/customers.csv')
        self.geolocation = pd.read_csv('./data/geolocation.csv') if os.path.exists('./data/geolocation.csv') \
            else pd.read_csv('data/geolocation.csv')
        self.order_payments = pd.read_csv('./data/order_payments.csv') if os.path.exists('./data/order_payments.csv') \
            else pd.read_csv('data/order_payments.csv')
        self.order_reviews = pd.read_csv('./data/order_reviews.csv') if os.path.exists('./data/order_reviews.csv') \
            else pd.read_csv('data/order_reviews.csv')
        self.orders = pd.read_csv('./data/orders.csv') if os.path.exists('./data/orders.csv') \
            else pd.read_csv('data/orders.csv')
        self.orders_items = pd.read_csv('./data/orders_items.csv') if os.path.exists('./data/orders_items.csv') \
            else pd.read_csv('data/orders_items.csv')
        self.product_category_name_translation = pd.read_csv('./data/product_category_name_translation.csv') \
            if os.path.exists('./data/product_category_name_translation.csv') \
            else pd.read_csv('data/product_category_name_translation.csv')
        self.products = pd.read_csv('./data/products.csv') if os.path.exists('./data/products.csv') \
            else pd.read_csv('data/products.csv')
        self.sellers = pd.read_csv('./data/sellers.csv') if os.path.exists('./data/sellers.csv') \
            else pd.read_csv('data/sellers.csv')

    def load_clear_data(self):
        self.customers = pd.read_csv('../cohort_analysis/clear_data/customers.csv') if os.path.exists(
            '../cohort_analysis/clear_data/customers.csv') \
            else pd.read_csv('./data/customers.csv')
        self.geolocation = pd.read_csv('../cohort_analysis/clear_data/geolocation.csv') if os.path.exists(
            '../cohort_analysis/clear_data/geolocation.csv') \
            else pd.read_csv('./data/geolocation.csv')
        self.order_payments = pd.read_csv('../cohort_analysis/clear_data/order_payments.csv') if os.path.exists(
            '../cohort_analysis/clear_data/order_payments.csv') \
            else pd.read_csv('./data/order_payments.csv')
        self.order_reviews = pd.read_csv('../cohort_analysis/clear_data/order_reviews.csv') if os.path.exists(
            '../cohort_analysis/clear_data/order_reviews.csv') \
            else pd.read_csv('./data/order_reviews.csv')
        self.orders = pd.read_csv('../cohort_analysis/clear_data/orders.csv') if os.path.exists(
            '../cohort_analysis/clear_data/orders.csv') \
            else pd.read_csv('./data/orders.csv')
        self.orders_items = pd.read_csv('../cohort_analysis/clear_data/orders_items.csv') if os.path.exists(
            '../cohort_analysis/clear_data/orders_items.csv') \
            else pd.read_csv('data/orders_items.csv')
        self.product_category_name_translation = pd.read_csv(
            '../cohort_analysis/clear_data/product_category_name_translation.csv') \
            if os.path.exists('../cohort_analysis/clear_data/product_category_name_translation.csv') \
            else pd.read_csv('data/product_category_name_translation.csv')
        self.products = pd.read_csv('../cohort_analysis/clear_data/products.csv') if os.path.exists(
            '../cohort_analysis/clear_data/products.csv') \
            else pd.read_csv('data/products.csv')
        self.sellers = pd.read_csv('../cohort_analysis/clear_data/sellers.csv') if os.path.exists(
            '../cohort_analysis/clear_data/sellers.csv') \
            else pd.read_csv('data/sellers.csv')

    def clear_data(self):
        self.__clear_customers()
        self.__clear_products()
        self.__clear_reviews()
        self.__clear_payments()
        self.__clear_orders()
        self.__clear_orders_items()
        self.__clear_geolocation()
        self.__clear_product_category_name_translation()
        self.__clear_sellers()

    def __clear_customers(self):
        customers_with_orders = self.orders['customer_id'].unique()
        self.customers = self.customers[self.customers['customer_id'].isin(customers_with_orders)]

    def __clear_products(self):
        indices_to_drop = self.products[
            ~self.products['product_category_name'].isin(self.product_category_name_translation['product_category_name'])].index
        self.products.drop(indices_to_drop, inplace=True)
        self.products.rename(columns={
            'product_name_lenght': 'product_name_length',
            'product_description_lenght': 'product_description_length'
        }, inplace=True)
        self.products.dropna(inplace=True)

    def __clear_reviews(self):
        self.order_reviews.drop(columns=['Unnamed: 0'], inplace=True)

    def __clear_payments(self):
        self.order_payments.drop(columns=['Unnamed: 0'], inplace=True)
        self.order_payments.drop_duplicates(inplace=True)

        indices_to_drop = self.order_payments[~self.order_payments['order_id'].isin(self.orders['order_id'])].index
        self.order_payments.drop(indices_to_drop, inplace=True)

        indices_to_drop = self.order_payments[self.order_payments['payment_type'] == 'not_defined'].index
        self.order_payments.drop(indices_to_drop, inplace=True)

    def __clear_geolocation(self):
        used_zip_codes = pd.concat([
            self.sellers['seller_zip_code_prefix'],
            self.customers['customer_zip_code_prefix']
        ]).drop_duplicates()

        mask = ~self.geolocation['geolocation_zip_code_prefix'].isin(used_zip_codes)

        self.geolocation = self.geolocation[~mask].copy()
        self.geolocation.drop_duplicates(inplace=True)
        self.geolocation.drop(columns=['Unnamed: 0'], inplace=True)

        def calc_most_state(group):
            res_group = pd.Series({
                'most_state': group['geolocation_state'].value_counts().index[0],
            })
            return res_group

        geolocation_states = (self.geolocation.groupby('geolocation_zip_code_prefix')[['geolocation_state']]
                              .apply(calc_most_state).reset_index())
        self.geolocation = pd.merge(self.geolocation, geolocation_states, on='geolocation_zip_code_prefix', how='left')
        self.geolocation['geolocation_state'] = (self.geolocation['most_state']
                                                 .combine_first(self.geolocation['geolocation_state']))
        self.geolocation.drop(columns=['most_state'], inplace=True)
        q_percent = 0.25

        def find_outliers(group):
            if len(group) >= 2:
                # latitude
                group_unique = group.drop_duplicates(subset=['geolocation_lat', 'geolocation_lng'])
                lats = group['geolocation_lat']
                Q1 = np.quantile(lats, q_percent)
                Q3 = np.quantile(lats, 1 - q_percent)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                group = group[
                    (group['geolocation_lat'] >= lower_bound) &
                    (group['geolocation_lat'] <= upper_bound)
                    ]

                # longitude
                lngs = group['geolocation_lng']
                Q1 = np.quantile(lngs, q_percent)
                Q3 = np.quantile(lngs, 1 - q_percent)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                group = group[
                    (group['geolocation_lng'] >= lower_bound) &
                    (group['geolocation_lng'] <= upper_bound)
                    ]
                return group
            return group

        # self.geolocation = self.geolocation.groupby('geolocation_state').apply(find_outliers).reset_index(drop=True)
        self.geolocation = self.geolocation.groupby('geolocation_zip_code_prefix').apply(find_outliers).reset_index(drop=True)

    def __clear_orders(self):
        delivered = self.orders[self.orders['order_status'] == 'delivered']
        drop_i = delivered[delivered.isna().any(axis=1)].index  # delivered orders with NaN timestamps
        self.orders.drop(index=drop_i, inplace=True)
        self.orders.drop_duplicates(inplace=True)

    def __clear_orders_items(self):
        try:
            self.orders_items.drop(['freight_value.1', 'shipping_limit_date.1', 'price.1'], axis=1, inplace=True)
        except Exception:
            pass

        indices_to_drop = self.orders_items[~self.orders_items['order_id'].isin(self.orders['order_id'])].index
        self.orders_items.drop(indices_to_drop, inplace=True)

        self.orders_items.drop(columns=['Unnamed: 0'], inplace=True)

        self.orders_items.drop_duplicates(inplace=True)

    def __clear_product_category_name_translation(self):
        self.product_category_name_translation.drop(columns=['Unnamed: 0'], inplace=True)

    def __clear_sellers(self):
        self.sellers.drop(columns=['Unnamed: 0'], inplace=True)

        invalid_cities = [
            '04482255',
            'vendas@creditparts.com.br',
            'rio de janeiro / rio de janeiro',
            'sao paulo / sao paulo',
            'rio de janeiro \\rio de janeiro',
            'ribeirao preto / sao paulo',
            'sp',
            'carapicuiba / sao paulo',
            'mogi das cruzes / sp',
            'sp / sp',
            'auriflama/sp',
            'pinhais/pr',
            'cariacica / es',
            'jacarei / sao paulo',
            'sao sebastiao da grama/sp',
            'maua/sao paulo',
            ' ',
            'lages - sc'
        ]

        indices_to_drop = self.sellers[self.sellers['seller_city'].isin(invalid_cities)].index
        self.sellers.drop(indices_to_drop, inplace=True)