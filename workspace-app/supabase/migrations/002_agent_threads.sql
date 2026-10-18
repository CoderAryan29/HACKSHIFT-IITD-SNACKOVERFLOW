CREATE TABLE IF NOT EXISTS threads (
    thread_id TEXT PRIMARY KEY,
    user_uid TEXT NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    title TEXT,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_threads_user_last_message
    ON threads (user_uid, last_message_at DESC);
