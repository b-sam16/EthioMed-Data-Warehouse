WITH raw_data AS (
    SELECT
        channel_title,
        channel_username,
        message_date,
        message,
        media_path,
        emoji_used,
        youtube_links
    FROM {{ source('ethio_med_data_warehouse', 'telegram_messages') }}  -- Reference the source
)

SELECT
    channel_title,
    channel_username,
    message_date,
    LENGTH(message) AS message_length,  -- New field: message length
    emoji_used,
    youtube_links
FROM raw_data
WHERE LENGTH(message) > 50  -- Filter: only messages longer than 50 characters
