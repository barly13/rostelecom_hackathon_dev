select
	count(c.customer_unique_id),
	to_char(date(o.order_purchase_timestamp), 'yyyy-MM') month_year
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