with source as (
    select * from {{ source('raw', 'yellow_taxi_trips') }}
),

converted as (
    select
        VendorID                                                    as vendor_id,
        TO_TIMESTAMP_NTZ(tpep_pickup_datetime  / 1000000)          as pickup_datetime,
        TO_TIMESTAMP_NTZ(tpep_dropoff_datetime / 1000000)          as dropoff_datetime,
        passenger_count,
        trip_distance                                               as trip_distance_miles,
        RatecodeID                                                  as rate_code_id,
        store_and_fwd_flag,
        PULocationID                                                as pickup_location_id,
        DOLocationID                                                as dropoff_location_id,
        payment_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount,
        congestion_surcharge,
        Airport_fee                                                 as airport_fee,
        cbd_congestion_fee,
        _loaded_at
    from source
),

filtered as (
    select *
    from converted
    where
        fare_amount > 0
        and trip_distance_miles between 0.1 and 200
        and passenger_count between 1 and 6
        and dropoff_datetime > pickup_datetime
        and DATEDIFF(minute, pickup_datetime, dropoff_datetime) between 1 and 180
),

enriched as (
    select
        vendor_id,
        pickup_datetime,
        dropoff_datetime,
        passenger_count,
        ROUND(trip_distance_miles * 1.60934, 2)                     as trip_distance_km,
        rate_code_id,
        store_and_fwd_flag,
        pickup_location_id,
        dropoff_location_id,
        payment_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount,
        congestion_surcharge,
        airport_fee,
        cbd_congestion_fee,
        _loaded_at,

        -- Dimensions temporelles
        DATE(pickup_datetime)                                       as trip_date,
        HOUR(pickup_datetime)                                       as pickup_hour,
        DAYOFWEEK(pickup_datetime)                                  as pickup_dow,
        CASE
            WHEN HOUR(pickup_datetime) between 6  and 11 THEN 'morning'
            WHEN HOUR(pickup_datetime) between 12 and 17 THEN 'afternoon'
            WHEN HOUR(pickup_datetime) between 18 and 21 THEN 'evening'
            ELSE 'night'
        END                                                         as time_of_day,

        -- Durée et vitesse
        DATEDIFF(minute, pickup_datetime, dropoff_datetime)         as trip_duration_min,
        ROUND(
            trip_distance_miles
            / NULLIF(DATEDIFF(minute, pickup_datetime, dropoff_datetime), 0)
            * 60 * 1.60934, 2
        )                                                           as avg_speed_kmh,

        -- Catégorie de distance (seuils en km)
        CASE
            WHEN trip_distance_miles * 1.60934 < 1.6  THEN 'short'
            WHEN trip_distance_miles * 1.60934 < 8.0  THEN 'medium'
            WHEN trip_distance_miles * 1.60934 < 24.0 THEN 'long'
            ELSE 'very_long'
        END                                                         as distance_category,

        -- Taux de pourboire
        ROUND(
            tip_amount / NULLIF(fare_amount, 0) * 100, 2
        )                                                           as tip_rate_pct
    from filtered
)

select * from enriched
