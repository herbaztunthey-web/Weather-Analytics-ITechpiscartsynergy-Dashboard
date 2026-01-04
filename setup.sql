SELECT 
    city, 
    temperature,
    CASE 
        WHEN temperature > 30 THEN '🔥 HEATWAVE ALERT'
        WHEN temperature BETWEEN 20 AND 30 THEN '✅ PLEASANT'
        WHEN temperature < 20 THEN '❄️ CHILLY'
        ELSE 'UNKNOWN'
    END AS weather_category
FROM weather;