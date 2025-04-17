select
	count(c.customer_unique_id),
	date(o.order_purchase_timestamp) date_day
from
	orders o
join
	customers c
on
	o.customer_id = c.customer_id
group by
	2
order by
	2