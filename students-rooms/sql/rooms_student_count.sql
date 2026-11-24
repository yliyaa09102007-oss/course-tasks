SELECT
    r.id,
    r.name,
    COUNT(s.id) AS student_count
FROM rooms AS r
LEFT JOIN students AS s ON r.id = s.room
GROUP BY r.id, r.name
ORDER BY r.id;