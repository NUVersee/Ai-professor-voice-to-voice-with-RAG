create table if not exists public.ai_professor_logs (
  id bigserial primary key,
  created_at timestamptz not null default now(),

  session_id text,
  endpoint text not null,

  user_question text not null,
  user_transcription text,
  model_answer text not null,

  retrieved_ids jsonb,
  latency_sec double precision
);

create index if not exists ai_professor_logs_created_at_idx
  on public.ai_professor_logs (created_at desc);

create index if not exists ai_professor_logs_endpoint_idx
  on public.ai_professor_logs (endpoint);

