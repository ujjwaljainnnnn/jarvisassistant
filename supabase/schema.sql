-- Jarvis's Supabase schema. Run this once against a fresh Supabase
-- project (SQL Editor -> New query -> paste -> Run) after creating it.
-- See the README's "Supabase setup" section for the full walkthrough.

-- Projects: named workspaces, each scoped to one user.
create table public.projects (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    name text not null,
    created_at timestamptz not null default now(),
    unique (user_id, name)
);

alter table public.projects enable row level security;

create policy "Users manage their own projects"
    on public.projects
    for all
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

-- Notes: the organized output of a voice note-taking session.
create table public.notes (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    project_id uuid references public.projects(id) on delete set null,
    content text not null,
    created_at timestamptz not null default now()
);

alter table public.notes enable row level security;

create policy "Users manage their own notes"
    on public.notes
    for all
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

create index notes_user_project_idx on public.notes (user_id, project_id, created_at desc);

-- Messages: reserved for persisted chat history per project. Jarvis
-- currently keeps conversation memory in memory for the running process
-- only (see engine/tutor.py) -- this table is here for that to build on
-- later without another migration.
create table public.messages (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    project_id uuid references public.projects(id) on delete cascade,
    role text not null check (role in ('user', 'assistant')),
    content text not null,
    created_at timestamptz not null default now()
);

alter table public.messages enable row level security;

create policy "Users manage their own messages"
    on public.messages
    for all
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

create index messages_user_project_idx on public.messages (user_id, project_id, created_at);
