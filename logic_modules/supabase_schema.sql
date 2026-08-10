-- ═══════════════════════════════════════════════════════════════
-- Supabase Schema for "Where We're From" Global Bulletin Board
-- Run this SQL in your Supabase SQL editor to set up the table,
-- indexes, and Row Level Security (RLS) policies.
--
-- 1. Go to https://supabase.com → Create new project (free)
-- 2. Open SQL Editor → paste this entire file → Run
-- 3. Copy your Project URL + anon public key into
--    `logic_modules/frontend/pages/global_supporter_map.html`
--    (SUPABASE_URL and SUPABASE_ANON_KEY variables)
-- ═══════════════════════════════════════════════════════════════

-- ─── Table: supporters ───
create table if not exists public.supporters (
  id uuid primary key default gen_random_uuid(),
  name text not null default '',
  city text not null,
  country text not null default '',
  lat double precision,
  lng double precision,
  vibe text not null default 'Global Grid',
  note text not null default '',
  created_at timestamptz not null default now()
);

-- ─── Indexes (for fast sorting + country counting) ───
create index if not exists supporters_created_at_idx on public.supporters (created_at desc);
create index if not exists supporters_country_idx on public.supporters (country);

-- ─── Enable Row Level Security ───
alter table public.supporters enable row level security;

-- ─── Policies ───
-- Anyone can read all supporters (public bulletin board)
create policy "Public read supporters" on public.supporters
  for select
  using (true);

-- Anyone can insert a new supporter pin (open community board)
create policy "Public insert supporters" on public.supporters
  for insert
  with check (true);

-- ─── Optional: seed data from your existing JSON (uncomment to import) ───
-- insert into public.supporters (name, city, country, lat, lng, vibe, note, created_at)
-- values
--   ('Abdul HQ', 'Detroit', 'USA', 42.3314, -83.0458, 'Rooted & Grounded', 'Let''s build a better Michigan!', '2026-08-01T12:00:00Z'),
--   ('Sarah', 'Dearborn', 'USA', 42.3223, -83.1763, 'Study Hall Regular', 'Proud to support Abdul!', '2026-08-02T15:30:00Z'),
--   ('Ahmed', 'London', 'UK', 51.5074, -0.1278, 'Global Grid', 'Supporting from across the pond!', '2026-08-03T09:15:00Z'),
--   ('Maria', 'Austin', 'USA', 30.2672, -97.7431, 'Lab Bench & Code', 'Tech for good!', '2026-08-04T18:45:00Z'),
--   ('Yusuf', 'Dubai', 'UAE', 25.2048, 55.2708, 'Transit Lounge', 'Global support for Michigan!', '2026-08-05T11:20:00Z');

-- ─── Done! ───
-- After running, the bulletin board will:
--   • Permanently store every pinned supporter in the cloud
--   • Instantly sync new pins to all open browser tabs worldwide
--   • Update the live supporter counter in real time