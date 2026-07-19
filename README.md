My first project :v

# Habit RPG 

A habit tracker that turns your daily grind into an RPG. Do your habits, earn HP/EXP/Gold/Kupon, level up. Skip them, take the hit. Built with Streamlit on the frontend and Supabase (Postgres + Auth) on the backend, so multiple people can use it and everyone's data stays separate.

## What it does

- Daily missions, split by category (Faith, Physical, Skill & Knowledge, Evaluation) and reordered depending on your shift (Pagi/Malam) and current level.
- Weekly missions and obligations, with bonuses for finishing and penalties for slacking.
- A level system (Pecundang → Polos → Pejuang → Pendekar → Jamal) based on total HP + EXP.
- Achievements that unlock automatically (streaks, levels, total habits done).
- A reward shop — spend your kupon on real rewards you set for yourself.
- Charts and a 12-week heatmap so you can actually see your consistency instead of just guessing.
- Daily/weekly resets that run on Jakarta time (WIB), and catch up automatically if you didn't open the app for a few days.
- Import/export your data.
- Login/register with email + password (Supabase Auth), and everyone's data is locked to their own account at the database level — not just in the app code.

## Stack

- Python + [Streamlit](https://streamlit.io/)
- [Supabase](https://supabase.com/) for the database and auth
- [Plotly](https://plotly.com/python/) for the charts
- Pandas

## Files

```
.
├── app.py              # the whole UI: login page, tabs, everything you see
├── core.py             # game logic + talking to Supabase
└── requirements.txt
```

Kept it to two main files on purpose — no need to over-engineer this.

## Getting it running

### 1. Clone it and install stuff

```bash
git clone https://github.com/jamalsatria13-svg/habit-rpg-v2.git
cd habit-rpg-v2
pip install -r requirements.txt
```

### 2. Set up Supabase

Spin up a project at [supabase.com](https://supabase.com/), then run this in the SQL editor:

```sql
create table habit_state (
  id bigint generated always as identity primary key,
  user_id uuid not null unique references auth.users(id) on delete cascade,
  data jsonb not null,
  updated_at timestamptz not null default now()
);

alter table habit_state enable row level security;

create policy "Users can view own habit_state"
  on habit_state for select using (auth.uid() = user_id);

create policy "Users can insert own habit_state"
  on habit_state for insert with check (auth.uid() = user_id);

create policy "Users can update own habit_state"
  on habit_state for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "Users can delete own habit_state"
  on habit_state for delete using (auth.uid() = user_id);
```

Then go to **Authentication → Providers** and make sure Email is turned on. If you don't want people to verify their email before using the app, turn off "Confirm email" there too.

### 3. Add your secrets

Create `.streamlit/secrets.toml` — and make sure it's in your `.gitignore`, don't commit this file:

```toml
SUPABASE_URL = "https://xxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```

Use the **anon/public key** here, not the `service_role` key. The service_role key skips RLS entirely, so if it ever leaked (say, an old commit in a public repo), anyone could read or wipe everyone's data.

### 4. Run it

```bash
streamlit run app.py
```

## Deploying to Streamlit Cloud

1. Push this repo to GitHub — public is fine, your users' data isn't protected by the repo being private, it's protected by RLS + auth.
2. Create a new app on [share.streamlit.io](https://share.streamlit.io/) pointing at this repo.
3. In **App settings → Secrets**, paste in the same `SUPABASE_URL` / `SUPABASE_KEY` as above.

## A word on security

The repo and the app can both be public — that's fine. What actually keeps one person's data away from another is the `auth.uid() = user_id` policy in Postgres, not the app hiding anything. So don't skip the RLS setup above, and don't ever commit `secrets.toml` or a `service_role` key, even in an old branch or commit. If one ever slips in, rotate the key right away from Supabase → Settings → API.


===== please give a stars and thank you =====


## License

Not decided yet — add one if you want (MIT is the easy default).
