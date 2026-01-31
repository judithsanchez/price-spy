-- Migration to add blocking_type and is_screenshot_faulty to extraction_logs

ALTER TABLE extraction_logs ADD COLUMN blocking_type TEXT;
ALTER TABLE extraction_logs ADD COLUMN is_screenshot_faulty BOOLEAN DEFAULT 0;
