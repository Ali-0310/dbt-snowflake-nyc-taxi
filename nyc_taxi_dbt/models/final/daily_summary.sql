with trips as (
    select * from {{ ref('stg_clean_trips') }}
)

select
    trip_date,
    COUNT(*)                                    as total_trips,
    ROUND(SUM(trip_distance_km), 2)             as total_distance_km,
    ROUND(AVG(trip_distance_km), 2)             as avg_distance_km,
    ROUND(SUM(total_amount), 2)                 as total_revenue,
    ROUND(AVG(total_amount), 2)                 as avg_revenue,
    ROUND(AVG(trip_duration_min), 2)            as avg_duration_min,
    ROUND(AVG(avg_speed_kmh), 2)                as avg_speed_kmh,
    ROUND(AVG(tip_rate_pct), 2)                 as avg_tip_rate_pct,
    SUM(passenger_count)                        as total_passengers,
    ROUND(AVG(passenger_count), 2)              as avg_passengers
from trips
group by trip_date
order by trip_date
