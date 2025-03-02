CREATE SCHEMA IF NOT EXISTS transcriptions;

CREATE TABLE IF NOT EXISTS transcriptions.videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(255) UNIQUE NOT NULL,
    text TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fts_transcript
ON transcriptions.videos USING GIN (to_tsvector('english', text));
