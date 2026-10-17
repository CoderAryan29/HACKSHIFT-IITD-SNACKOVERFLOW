-- KisanSetu: Initial database migration

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS districts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    state TEXT NOT NULL,
    UNIQUE (name, state)
);

CREATE TABLE IF NOT EXISTS mandis (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    district_id BIGINT REFERENCES districts(id),
    state TEXT NOT NULL,
    UNIQUE (name, district_id)
);

CREATE TABLE IF NOT EXISTS mandi_prices (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    price_date DATE NOT NULL,
    mandi_id BIGINT NOT NULL REFERENCES mandis(id),
    commodity TEXT NOT NULL,
    variety TEXT NOT NULL DEFAULT 'General',
    min_price NUMERIC(12, 2) NOT NULL CHECK (min_price >= 0),
    max_price NUMERIC(12, 2) NOT NULL CHECK (max_price >= min_price),
    modal_price NUMERIC(12, 2) NOT NULL CHECK (modal_price >= 0),
    arrivals_qtl NUMERIC(14, 2) CHECK (arrivals_qtl >= 0),
    UNIQUE (price_date, mandi_id, commodity, variety)
);

CREATE TABLE IF NOT EXISTS price_forecasts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mandi_id BIGINT NOT NULL REFERENCES mandis(id),
    commodity TEXT NOT NULL,
    issued_on DATE NOT NULL,
    target_date DATE NOT NULL,
    horizon_days INTEGER NOT NULL CHECK (horizon_days > 0),
    p10 NUMERIC(12, 2),
    p50 NUMERIC(12, 2),
    p90 NUMERIC(12, 2),
    model_version TEXT NOT NULL,
    CHECK (
        p10 IS NULL OR p50 IS NULL OR p90 IS NULL
        OR (p10 <= p50 AND p50 <= p90)
    )
);

CREATE TABLE IF NOT EXISTS price_model_metrics (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    model_version TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC(14, 6) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    uid TEXT PRIMARY KEY,
    role TEXT NOT NULL CHECK (role IN ('farmer', 'buyer', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS farms (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_uid TEXT NOT NULL REFERENCES users(uid),
    name TEXT NOT NULL,
    district_id BIGINT REFERENCES districts(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS listings (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    farmer_uid TEXT NOT NULL REFERENCES users(uid),
    farm_id BIGINT REFERENCES farms(id),
    commodity TEXT NOT NULL,
    variety TEXT,
    quantity_qtl NUMERIC(14, 2) NOT NULL CHECK (quantity_qtl > 0),
    asking_price NUMERIC(12, 2) CHECK (asking_price >= 0),
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bids (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    listing_id BIGINT NOT NULL REFERENCES listings(id),
    buyer_uid TEXT NOT NULL REFERENCES users(uid),
    price_per_qtl NUMERIC(12, 2) NOT NULL CHECK (price_per_qtl > 0),
    quantity_qtl NUMERIC(14, 2) NOT NULL CHECK (quantity_qtl > 0),
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS deals (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    listing_id BIGINT NOT NULL REFERENCES listings(id),
    bid_id BIGINT REFERENCES bids(id),
    farmer_uid TEXT NOT NULL REFERENCES users(uid),
    buyer_uid TEXT NOT NULL REFERENCES users(uid),
    quantity_qtl NUMERIC(14, 2) NOT NULL CHECK (quantity_qtl > 0),
    agreed_price_per_qtl NUMERIC(12, 2) NOT NULL
        CHECK (agreed_price_per_qtl > 0),
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS doc_chunks (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mandi_prices_lookup
    ON mandi_prices (commodity, mandi_id, price_date DESC);

CREATE INDEX IF NOT EXISTS idx_price_forecasts_lookup
    ON price_forecasts (commodity, mandi_id, target_date);

CREATE INDEX IF NOT EXISTS idx_listings_status
    ON listings (status);

CREATE INDEX IF NOT EXISTS idx_doc_chunks_embedding
    ON doc_chunks USING hnsw (embedding vector_cosine_ops);