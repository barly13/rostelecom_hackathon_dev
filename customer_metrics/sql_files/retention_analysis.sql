with recursive periods as (
    select 
        date_trunc('month', min(date(order_purchase_timestamp))) start_month,
        date_trunc('month', min(date(order_purchase_timestamp))) + interval '3 months' - interval '1 day' end_month
    from 
		orders
    
    union all
    
    select
        p.end_month + interval '1 day',
        p.end_month + interval '3 months'
    from 
		periods p
    where 
		p.end_month < (select max(date(order_purchase_timestamp)) from orders)
),

customer_first_last as (
    select 
        c.customer_unique_id,
        min(date(o.order_purchase_timestamp)) first_order_date,
        max(date(o.order_purchase_timestamp)) last_order_date
    from 
		orders o
    join 
		customers c 
	on 
		o.customer_id = c.customer_id
    group by 
		1
),

period_stats as (
    select
        p.start_month,
        p.end_month,
        -- Пользователи на начало периода (совершили первый заказ до начала периода)
        count(distinct case when cfl.first_order_date < p.start_month then cfl.customer_unique_id end) starting_customers,
        -- Новые пользователи в периоде
        count(distinct case when cfl.first_order_date between p.start_month and p.end_month then cfl.customer_unique_id end) new_customers,
        -- Ушедшие пользователи (последний заказ был более 3 месяцев назад до конца периода)
        count(distinct case when cfl.last_order_date < p.end_month - interval '3 months' 
                            and cfl.first_order_date < p.start_month then cfl.customer_unique_id end) departed_customers
    from 
		periods p
    cross join 
		customer_first_last cfl
    group by 
		1, 2
)

select
    to_char(start_month, 'yyyy-MM') || ' to ' || to_char(end_month, 'YYYY-MM') as period,
    starting_customers,
    new_customers,
    departed_customers,
    starting_customers + new_customers - departed_customers ending_customers,
    case when starting_customers > 0 
         then round((starting_customers - departed_customers) * 100.0 / starting_customers, 1)
         else null 
    end retention_rate
from 
	period_stats
order by 
	start_month