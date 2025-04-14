with grouped_payments as (
	select
		order_id,
		sum(payment_value) monetary_value
	from
		order_payments
	group by
		1
),

max_date as (
	select 
		date(max(order_purchase_timestamp)) + interval '1 day' analysis_date
	from
		orders
),

customer_metrics as (
	select
		c.customer_unique_id,
		max(order_purchase_timestamp) last_purchase_date,
		count(distinct o.order_id) total_orders_count,
		sum(monetary_value) monetary_value,
		count(distinct case when order_status = 'delivered' then o.order_id end) delivered_orders_count
	from
		grouped_payments gp
	join
		orders o on o.order_id = gp.order_id
	join
		customers c on c.customer_id = o.customer_id
	group by
		1
),

rfm_data as (
	select
		cm.*,
		date((select analysis_date from max_date)) - date(cm.last_purchase_date) recency_days,
		cm.monetary_value / nullif(cm.total_orders_count, 0) avg_order_value,
		round(cm.delivered_orders_count * 100 / nullif(cm.total_orders_count, 0), 2) delivered_rate_percentage
	from
		customer_metrics cm
),

rfm_scores as (
    select 
        customer_unique_id,
        last_purchase_date,
        recency_days,
        total_orders_count,
        monetary_value,
        avg_order_value,
        delivered_rate_percentage,
        case 
            when recency_days <= (select percentile_cont(0.33) within group (order by recency_days) from rfm_data) then 1
            when recency_days <= (select percentile_cont(0.66) within group (order by recency_days) from rfm_data) then 2
            else 3
        end r_score,
        
        case 
            when total_orders_count >= 5 then 1
            when total_orders_count >= 2 then 2 
            else 3                              
        end f_score,
        
        case 
            when monetary_value >= (select percentile_cont(0.66) within group (order by monetary_value) from rfm_data) then 1
            when monetary_value >= (select percentile_cont(0.33) within group (order by monetary_value) from rfm_data) then 2
            else 3
        end m_score
    from
        rfm_data
),

rfm_analysis as (
	select 
	    customer_unique_id,
	    last_purchase_date,
	    recency_days,
	    total_orders_count,
	    monetary_value,
	    avg_order_value,
	    delivered_rate_percentage,
		concat(r_score, f_score, m_score) rfm_cell,
	    case concat(r_score, f_score, m_score)
	        when '111' then 'Недавние, частые, высокий чек'
	        when '121' then 'Недавние, не очень часто, высокий чек'
	        when '131' then 'Недавние, редкие, высокий чек'
	        when '112' then 'Недавние, частые, средний чек'
	        when '122' then 'Недавние, не очень часто, средний чек'
	        when '132' then 'Недавние, редкие, средний чек'
	        when '113' then 'Недавние, частые, низкий чек'
	        when '123' then 'Недавние, не очень часто, низкий чек'
	        when '133' then 'Недавние, редкие, низкий чек'
	        when '211' then 'Средней давности, частые, высокий чек'
	        when '221' then 'Средней давности, не очень часто, высокий чек'
	        when '231' then 'Средней давности, редкие, высокий чек'
	        when '212' then 'Средней давности, частые, средний чек'
	        when '222' then 'Средней давности, не очень часто, средний чек'
	        when '232' then 'Средней давности, редкие, средний чек'
	        when '213' then 'Средней давности, частые, низкий чек'
	        when '223' then 'Средней давности, не очень часто, низкий чек'
	        when '233' then 'Средней давности, редкие, низкий чек'
	        when '311' then 'Давние, частые, высокий чек'
	        when '321' then 'Давние, не очень часто, высокий чек'
	        when '331' then 'Давние, редкие, высокий чек'
	        when '312' then 'Давние, частые, средний чек'
	        when '322' then 'Давние, не очень часто, средний чек'
	        when '332' then 'Давние, редкие, средний чек'
	        when '313' then 'Давние, частые, низкий чек'
	        when '323' then 'Давние, не очень часто, низкий чек'
	        when '333' then 'Давние, редкие, низкий чек'
	        else 'Не определено'
	    end rfm_segment_description
	from
	    rfm_scores
	order by
	    rfm_cell
)

-- select
-- 	*
-- from
-- 	rfm_analysis
-- order by
-- 	recency_days

select
	rfm_cell,
	rfm_segment_description,
	count(customer_unique_id)
from
	rfm_analysis
group by
	1, 2
order by
	1


