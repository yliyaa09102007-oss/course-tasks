SELECT
    r.id,
    r.name,
    AVG(AGE(CURRENT_DATE, s.birthday)) AS avg_age
FROM rooms AS r
JOIN students AS s ON r.id = s.room
GROUP BY r.id, r.name
ORDER BY avg_age ASC
LIMIT 5;