# **Full-Text Search in PostgreSQL: Searching Video Transcriptions**  

## **Overview**  
The following SQL query performs a **full-text search** in a PostgreSQL database to find videos that contain specific keywords within their transcription text.  

```sql
SELECT video_id
FROM transcriptions.videos
WHERE to_tsvector('english', text) @@ to_tsquery('english', 'Kubernetes | container');
```