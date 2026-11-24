SELECT
    r.id,
    r.name
FROM rooms AS r
JOIN students AS s ON r.id = s.room
GROUP BY r.id, r.name
HAVING COUNT(DISTINCT s.sex) > 1
ORDER BY r.id;