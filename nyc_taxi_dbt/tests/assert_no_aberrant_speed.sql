-- Vérifie qu'aucun trajet n'a une vitesse moyenne supérieure à 150 km/h.
-- Un taxi new-yorkais ne peut pas rouler à plus de 150 km/h en conditions normales.
-- Ce test retourne les lignes qui violent la règle (0 ligne = succès).

select
    pickup_datetime,
    dropoff_datetime,
    trip_distance_km,
    trip_duration_min,
    avg_speed_kmh
from {{ ref('stg_clean_trips') }}
where avg_speed_kmh > 150
