with trips as (
    select * from {{ ref('stg_clean_trips') }}
)

select
    pickup_location_id,
    COUNT(*)                                    as total_trips,
    ROUND(AVG(trip_distance_km), 2)             as avg_distance_km,
    ROUND(AVG(trip_duration_min), 2)            as avg_duration_min,
    ROUND(AVG(avg_speed_kmh), 2)                as avg_speed_kmh,
    ROUND(AVG(fare_amount), 2)                  as avg_fare_amount,
    ROUND(AVG(tip_rate_pct), 2)                 as avg_tip_rate_pct,
    ROUND(SUM(total_amount), 2)                 as total_revenue,
    ROUND(AVG(total_amount), 2)                 as avg_total_amount,
    COUNT(DISTINCT dropoff_location_id)         as unique_destinations
from trips
group by pickup_location_id
order by total_trips desc
