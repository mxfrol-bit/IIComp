-- 008_storage_bucket.sql
-- Публичный storage-бакет 'generations' для фото товаров, кадров и видео.
-- Код создаёт его сам (db.ensure_storage_bucket при старте). Этот SQL —
-- ручной запасной вариант для Supabase SQL Editor.
--
-- Это корень бага «Не получилось сделать видео» и «товар игнорируется»:
-- видео/фото генерируются на fal, но upload в Storage падает с
-- 400 Bucket not found, кредит возвращается, результат теряется.

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
    'generations',
    'generations',
    true,
    209715200,  -- 200 MB (Wan 10-15s mp4 бывает крупным)
    array['image/jpeg','image/png','image/webp','video/mp4']
)
on conflict (id) do update
    set public = true,
        file_size_limit = excluded.file_size_limit,
        allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "public read generations" on storage.objects;
create policy "public read generations"
    on storage.objects for select
    using (bucket_id = 'generations');
