GET_VIDEOS_BY_KEYWORD = """
    SELECT video_id
    FROM transcriptions.videos
    WHERE to_tsvector('english', text) @@ to_tsquery('english', '{keywords}');
"""
