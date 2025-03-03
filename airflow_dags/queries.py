GET_VIDEOS_BY_KEYWORD = """
    SELECT video_id
    FROM transcriptions.videos
    WHERE to_tsvector('english', text) @@ to_tsquery('english', '{keywords}');
"""

GET_VIDEOS_EXISTENCE = """
WITH video_ids AS (
    SELECT unnest(ARRAY[{video_ids}]) as video_id
)
SELECT v_list.video_id
FROM video_ids v_list
LEFT JOIN transcriptions.videos v_database
ON v_list.video_id = v_database.video_id
WHERE v_database.video_id IS NULL;
"""
