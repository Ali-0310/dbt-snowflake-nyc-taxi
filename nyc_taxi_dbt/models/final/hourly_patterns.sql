with trips as (
    select * from {{ ref('stg_clean_trips') }}
)

select
    pickup_hour,
    time_of_day,
    pickup_dow,
    COUNT(*)                                    as total_trips,
    ROUND(AVG(trip_distance_km), 2)             as avg_distance_km,
    ROUND(AVG(trip_duration_min), 2)            as avg_duration_min,
    ROUND(AVG(avg_speed_kmh), 2)                as avg_speed_kmh,
    ROUND(AVG(fare_amount), 2)                  as avg_fare_amount,
    ROUND(AVG(tip_rate_pct), 2)                 as avg_tip_rate_pct,
    ROUND(AVG(passenger_count), 2)              as avg_passengers,
    ROUND(SUM(total_amount), 2)                 as total_revenue
from trips
group by pickup_hour, time_of_day, pickup_dow
order by pickup_dow, pickup_hour
