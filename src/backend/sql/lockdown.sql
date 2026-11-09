-- Locks the tables so that only the backend (service_role key) can use them.
--
-- With row level security enabled and no policies, Supabase's public anon key can no
-- longer read or write anything, including the password hashes in `accounts`.
-- The service_role key bypasses RLS, so the FastAPI backend keeps working.
--
-- WARNING: the released Android app (version 4) talks to Supabase directly with the anon
-- key. Running this script breaks that app. Run it once the web app has replaced it.

ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE elements ENABLE ROW LEVEL SECURITY;
ALTER TABLE elements_to_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE compounds ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
