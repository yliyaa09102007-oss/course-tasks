SELECT
    r.id,
    r.name,
    (MAX(s.birthday)::date - MIN(s.birthday)::date) AS age_diff_days
FROM rooms AS r
JOIN students AS s ON r.id = s.room
GROUP BY r.id, r.name
ORDER BY age_diff_days DESC
LIMIT 5;