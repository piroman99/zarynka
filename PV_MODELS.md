# PlusVibe API — что живо (проверено живыми запросами)

Дата проверки: 2026-10-17 · баланс: 304.07 ₽

Метод: `GET /api/media-catalog` (171 медиа-модель) + `POST /api/media/price` по каждой с дефолтными параметрами; чат-модели — `POST /v1/chat/completions` с max_tokens=1.

Итог: медиа — **161 из 171 принимаются** (остальные 10 — «временно недоступна» либо требуют входной файл); чат — **56 из 59 живы**.


## Мёртвые / недоступные медиа-модели

| kind | model | почему |
|---|---|---|
| video | `MiniMax-H3-Context-IR` | MiniMax H3 Context IR — временно недоступна. |
| video | `MiniMax-H3-Regeneration` | MiniMax H3 Regeneration — временно недоступна. |
| image | `grok-imagine-2.0-ext` | Grok Imagine 2.0 — редактирование области изображения. Временно недоступна. |
| video | `happyhorse-1.1` | HappyHorse 1.1 — временно недоступна. |
| 3d | `hunyuan3d-2` | Canvas GPU-runtime generation временно недоступна: для этой версии модели не подтверждён ж |
| 3d | `hunyuan3d-2mv` | Canvas GPU-runtime generation временно недоступна: для этой версии модели не подтверждён ж |
| image | `midjourney` | Midjourney — временно недоступна. |
| video | `seedance-2.0-face` | Seedance 2.0 Face — временно недоступна. |
| video | `wan2.7-r2v` | Wan 2.7 Reference-to-Video (Alibaba) — видео по референсу: изображение и/или видео (с виде |
| video | `wan2.7-videoedit` | Wan 2.7 Video Edit — временно недоступна. |

## Живые, но требуют входной файл (иначе 422)

| model | нужен вход |
|---|---|
| `elevenlabs-dubbing` | audio_url/video_url |
| `elevenlabs-voice-changer` | audio |
| `forced-alignment` | audio_url |
| `hailuo-2-3` | image_url (I2V) |
| `ideogram-character` | image_url (create) |
| `nemotron-3-diarization` | audio_url |
| `nemotron-asr-multilingual` | audio_url |
| `p-video-edit` | video_url |
| `qwen3-asr-1.7b` | audio_url |
| `speech-to-text` | audio_url |
| `topaz-denoise` | image_url |
| `topaz-sharpen` | image_url |
| `topaz-upscale-generative` | image_url |
| `universal-2` | audio_url |
| `vidu-q4` | image_url |
| `voxtral-small-24b-2507` | audio_url |
| `whisper-large-v3` | audio_url |
| `whisper-large-v3-turbo` | audio_url |

## image — живые (45)

| model | от, ₽ | unit | цена | aliases |
|---|---|---|---|---|
| `topaz-upscale-generative` (нужен image_url) | — | за изображение | unavailable |  |
| `topaz-sharpen` (нужен image_url) | — | за изображение | unavailable |  |
| `topaz-denoise` (нужен image_url) | — | за изображение | unavailable |  |
| `recraft` | 0.31 | за изображение | estimate |  |
| `z-image` | 0.50 | за изображение | estimate |  |
| `z-image-turbo` | 1.26 | за изображение | exact |  |
| `nano-banana` | 1.58 | за изображение | exact | gemini-2.5-flash-image |
| `seedream-5-0-flash` | 1.86 | за изображение | exact |  |
| `nano-banana-2` | 1.89 | за изображение | exact |  |
| `krea-2` | 1.89 | за изображение | exact |  |
| `grok-imagine` | 2.02 | за изображение | exact |  |
| `ideogram-v3` | 2.37 | за изображение | estimate |  |
| `gpt-image-1-5` | 2.51 | за изображение | exact | gpt-image-1.5 |
| `imagen4` | 2.51 | за изображение | estimate |  |
| `qwen-image` | 2.51 | за изображение | estimate |  |
| `qwen-image-2-1` | 2.51 | за изображение | exact |  |
| `qwen3-image` | 2.59 | за изображение | exact | qwen-image-3.0 |
| `gpt-image-2` | 2.70 | за изображение | exact |  |
| `nano-banana-2.1` | 2.71 | за изображение | exact |  |
| `grok-imagine-image-2-0` | 2.71 | за изображение | exact |  |
| `wan-2-7-image` | 3.02 | за изображение | exact |  |
| `flux-kontext` | 3.14 | за изображение | estimate |  |
| `flux-2` | 3.38 | за изображение | exact |  |
| `krea-3` | 3.39 | за изображение | exact |  |
| `seedream-5-0-pro` | 3.68 | за изображение | exact |  |
| `seedream-5` | 3.72 | за изображение | exact |  |
| `grok-imagine-image-2.0` | 4.02 | за изображение | exact |  |
| `nano-banana-pro` | 4.06 | за изображение | exact |  |
| `gpt-image-2-5` | 4.07 | за изображение | exact |  |
| `seedream` | 4.09 | за изображение | exact |  |
| `seedream-4-5` | 4.09 | за изображение | estimate |  |
| `qwen3-pro` | 4.33 | за изображение | estimate |  |
| `recraft-v4-1` | 4.74 | за изображение | exact |  |
| `flux-3-image` | 4.83 | за изображение | exact |  |
| `grok-imagine-image-quality` | 5.03 | за изображение | exact |  |
| `flux-1.1-pro` | 5.03 | за изображение | exact |  |
| `flux-fill` | 5.03 | за изображение | exact |  |
| `topaz-upscale` | 6.29 | за изображение | estimate |  |
| `wan2.7-image-pro` | 6.84 | за изображение | exact |  |
| `flux-2-max` | 7.59 | за изображение | exact |  |
| `ideogram-v4` | 8.13 | за изображение | exact |  |
| `ideogram-4-5` | 8.13 | за изображение | exact |  |
| `ideogram-4-5-precise-edit` | 8.13 | за изображение | exact |  |
| `ideogram-character` (нужен image_url (create)) | 11.31 | за изображение | estimate |  |
| `seedream-layer` | 23.69 | за изображение | exact |  |

## video — живые (63)

| model | от, ₽ | unit | цена | aliases |
|---|---|---|---|---|
| `vidu-q2` | 1.26 | за секунду | exact |  |
| `MiniMax-Hailuo-02` | 1.31 | за секунду | exact |  |
| `suno-music-video` | 1.35 | за ролик | exact |  |
| `grok-imagine-video` | 1.62 | за секунду | exact |  |
| `pixverse-v6` | 2.71 | за секунду | exact |  |
| `wan-3-0` | 3.14 | за секунду | exact |  |
| `minimax-h3-max-turbo` | 3.14 | за секунду | exact |  |
| `p-video-edit` (нужен video_url) | 3.38 | за секунду | exact |  |
| `wan-animate` | 3.77 | за секунду | estimate |  |
| `gemini-omni-flash-1-1-flow` | 3.77 | за секунду | exact |  |
| `vidu-q3` | 4.02 | за секунду | exact |  |
| `seedance-2-0-mini` | 4.06 | за секунду | exact |  |
| `p-video-2` | 4.07 | за ролик | exact |  |
| `wan3.0-video` | 4.31 | за секунду | exact |  |
| `vidu-q4` (нужен image_url) | 4.87 | за секунду | exact |  |
| `kling-ai-avatar` | 5.03 | за секунду | estimate |  |
| `volcengine-lipsync` | 5.03 | за секунду | estimate |  |
| `topaz-video-upscale` | 5.03 | за секунду | estimate |  |
| `minimax-h3` | 5.42 | за секунду | exact |  |
| `minimax-h3-max` | 6.03 | за секунду | exact |  |
| `p-video-2-pro` | 6.77 | за ролик | exact |  |
| `kling-motion-control` | 6.91 | за секунду | estimate |  |
| `wan-3-0-prime` | 6.96 | за секунду | exact |  |
| `flux-3` | 7.54 | за секунду | exact |  |
| `runway-gen4` | 7.54 | за ролик | estimate |  |
| `skyreels-v4-fast` | 8.04 | за секунду | exact |  |
| `seedance-2.0` | 8.30 | за секунду | exact |  |
| `kling-video-o1` | 8.45 | за секунду | exact |  |
| `veo-3.1` | 8.80 | за ролик | exact |  |
| `kling-v3-omni` | 9.48 | за секунду | exact |  |
| `grok-imagine-extend` | 9.75 | за ролик | exact |  |
| `kling-v3.0` | 10.00 | за секунду | exact |  |
| `seedance-2.0-fast-face` | 10.06 | за секунду | exact |  |
| `minimax-h3-max-lipsync` | 10.06 | за секунду | exact |  |
| `lipsync-2-pro` | 10.50 | за секунду | exact |  |
| `wan-2-7` | 10.83 | за секунду | exact |  |
| `skyreels-v4-std` | 11.06 | за секунду | exact |  |
| `kling-v3-turbo` | 11.31 | за секунду | estimate |  |
| `seedance-2.5` | 11.51 | за секунду | exact |  |
| `grok-imagine-upscale` | 12.57 | за апскейл | estimate |  |
| `heygen-avatar-4` | 12.57 | за секунду | exact |  |
| `wan-speech-to-video` | 12.57 | за секунду | exact |  |
| `omnihuman-v2` | 13.20 | за секунду | exact |  |
| `happyhorse` | 14.14 | за секунду | estimate |  |
| `sync-3-avatar` | 16.76 | за секунду | exact |  |
| `sync-3` | 16.80 | за секунду | exact |  |
| `omnihuman-1-5` | 16.97 | за секунду | estimate |  |
| `p-video-avatar` | 17.57 | за секунду | exact |  |
| `hailuo-2-3` (нужен image_url (I2V)) | 18.86 | за ролик | exact |  |
| `veed-fabric-1.0` | 18.86 | за секунду | exact |  |
| `omnihuman-v1.5` | 20.11 | за секунду | exact |  |
| `luma-ray-3-2` | 20.31 | за ролик | exact |  |
| `react-1` | 21.00 | за секунду | exact |  |
| `ltx-2.5-audio-to-video` | 21.37 | за секунду | exact |  |
| `wan-2-2` | 25.14 | за ролик | estimate |  |
| `pika` | 25.14 | за ролик | exact |  |
| `kling-v2-5-turbo` | 26.40 | за ролик | estimate |  |
| `kling-v2.6` | 37.23 | за ролик | exact |  |
| `wan-2-5` | 37.71 | за ролик | estimate |  |
| `gemini-omni-video` | 42.65 | за ролик | exact |  |
| `gemini-omni-flash-1-1` | 42.65 | за ролик | exact |  |
| `wan-2-6` | 44.00 | за ролик | estimate |  |
| `runway-gen-4-5` | 81.24 | за ролик | exact |  |

## music — живые (11)

| model | от, ₽ | unit | цена | aliases |
|---|---|---|---|---|
| `acestep-v15-xl-sft` | 0.14 | за секунду | exact |  |
| `suno-replace-section` | 4.51 | за трек | exact |  |
| `suno-cover-generate` | 7.54 | за трек | exact |  |
| `lyria-3-5` | 8.13 | за трек | exact |  |
| `suno` | 10.82 | за трек | exact |  |
| `suno-mashup` | 10.82 | за трек | exact |  |
| `suno-add-instrumental` | 10.82 | за трек | exact |  |
| `suno-add-vocals` | 10.82 | за трек | exact |  |
| `suno-cover-audio` | 10.82 | за трек | exact |  |
| `suno-extend-audio` | 10.82 | за трек | exact |  |
| `elevenlabs-music` | 40.62 | за трек | exact |  |

## audio — живые (37)

| model | от, ₽ | unit | цена | aliases |
|---|---|---|---|---|
| `mimo-v2-5-tts` | 0.01 | за 1000 символов | exact |  |
| `mimo-v2-5-tts-voiceclone` | 0.01 | за 1000 символов | exact |  |
| `mimo-v2-5-tts-voicedesign` | 0.01 | за 1000 символов | exact |  |
| `whisper-large-v3-turbo` (нужен audio_url) | 0.02 | за минуту | exact |  |
| `nemotron-asr-multilingual` (нужен audio_url) | 0.02 | за минуту | exact |  |
| `qwen3-asr-1.7b` (нужен audio_url) | 0.06 | за минуту | exact |  |
| `whisper-large-v3` (нужен audio_url) | 0.06 | за минуту | exact |  |
| `gpt-4o-mini-tts` | 0.07 | за 1000 символов | exact |  |
| `nemotron-3-diarization` (нужен audio_url) | 0.08 | за минуту | exact |  |
| `chatterbox-turbo` | 0.13 | за 1000 символов | exact |  |
| `suno-persona` | 0.25 | за файл | exact |  |
| `suno-midi` | 0.25 | за файл | exact |  |
| `universal-2` (нужен audio_url) | 0.35 | за минуту | exact |  |
| `suno-style-boost` | 0.36 | за файл | exact |  |
| `voxtral-small-24b-2507` (нужен audio_url) | 0.42 | за минуту | exact |  |
| `suno-timestamped-lyrics` | 0.45 | за файл | exact |  |
| `speech-to-text` (нужен audio_url) | 1.00 | за минуту | exact |  |
| `elevenlabs-sound-effects-v2` | 1.36 | за файл | exact |  |
| `gemini-3.8-flash-tts` | 1.70 | за 1000 символов | exact |  |
| `gemini-3.8-flash-tts-lite` | 1.70 | за 1000 символов | exact |  |
| `suno-lyrics` | 1.89 | за файл | estimate |  |
| `grok-tts` | 2.04 | за 1000 символов | exact |  |
| `qwen3-tts` | 2.71 | за 1000 символов | exact |  |
| `voice-clone-tts` | 2.71 | за 1000 символов | exact |  |
| `chatterbox-tts` | 3.00 | за 1000 символов | exact |  |
| `kokoro-tts` | 3.00 | за 1000 символов | exact |  |
| `inworld-realtime-tts-1-5-mini` | 3.51 | за 1000 символов | exact |  |
| `elevenlabs-dubbing` (нужен audio_url/video_url) | 4.97 | за секунду | exact |  |
| `gemini-tts` | 5.30 | за 1000 символов | estimate | gemini-3.1-flash-tts |
| `tts` | 7.00 | за озвучку | exact |  |
| `inworld-realtime-tts-1-5-max` | 7.03 | за 1000 символов | exact |  |
| `elevenlabs-v4-tts` | 10.84 | за 1000 символов | exact |  |
| `suno-stem` | 12.57 | за файл | exact |  |
| `elevenlabs-dialogue` | 12.62 | за 1000 символов | exact |  |
| `forced-alignment` (нужен audio_url) | 14.08 | за 1000 символов | exact |  |
| `suno-sfx` | 15.71 | за файл | exact |  |
| `elevenlabs-voice-changer` (нужен audio) | 21.00 | за 1000 символов | exact |  |

## 3d — живые (5)

| model | от, ₽ | unit | цена | aliases |
|---|---|---|---|---|
| `trellis` | 2.51 | за модель | exact |  |
| `hunyuan3d` | 20.11 | за модель | exact |  |
| `tripo` | 37.71 | за модель | exact |  |
| `rodin` | 50.29 | за модель | exact |  |
| `meshy` | 100.57 | за модель | exact |  |

## Чат-модели

Живы (56):

- `anthropic/claude-opus-4.8` — cost=0.00197462
- `anthropic/claude-opus-5` — cost=0.010209
- `claude-opus-4.6` — cost=0.01797882
- `claude-opus-4.7` — cost=0.02633212
- `anthropic/claude-sonnet-4.6` — cost=0.000986
- `anthropic/claude-sonnet-5` — cost=0.001128
- `claude-sonnet-5.5` — cost=0.000884
- `claude-haiku-5.5` — cost=0.000043
- `claude-fable-5-1` — cost=0.008021
- `openai/gpt-5.6-luna` — cost=0.00003008
- `openai/gpt-5.6-terra` — cost=0.00024511
- `openai/gpt-5.6-sol` — cost=0.000543
- `gpt-6-astra` — cost=0.00422655
- `gpt-6-luna` — cost=0.00014635
- `gpt-6-sol` — cost=0.000462
- `gpt-6.1-sol` — cost=0.00024991
- `claude-opus-5.5` — cost=0.00171
- `deepseek/deepseek-v4-flash-0731` — cost=0.00014334
- `deepseek-v4.1-flash` — cost=0.00010306
- `deepseek/deepseek-v4-pro-0813` — cost=0.00117504
- `google/gemini-3.1-pro-preview` — cost=0.00076319
- `google/gemini-3.5-flash` — cost=0.00058132
- `google/gemini-3.8-flash` — cost=0.00525251
- `qwen/qwen3.7-plus` — cost=0.00041104
- `qwen3.8-flash` — cost=0.00003366
- `qwen3.8-omni-flash` — cost=0.00013271
- `hy4-preview` — cost=0.00051373
- `qwen/qwen3.8-max` — cost=0.00064416
- `moonshotai/kimi-k2.7-code` — cost=0.007641
- `nemotron-3.5-lightning` — cost=0.00016715
- `llama-4-maverick` — cost=0.00050994
- `openai/gpt-oss-120b` — cost=0.00136103
- `qwen3.8-27b` — cost=0.00070628
- `moonshotai/kimi-k2.6` — cost=0.00201128
- `gemma-4` — cost=0.00079514
- `glm-5.1` — cost=0.00258291
- `z-ai/glm-5.2` — cost=0.00033608
- `z-ai/glm-5.3` — cost=0.00697188
- `z-ai/glm-5.3-flash` — cost=0.00029164
- `glm-5.3-flashx` — cost=0.00122906
- `qwen3.6-35b` — cost=0.00021424
- `perplexity/sonar` — cost=0.00146342
- `perplexity/sonar-pro` — cost=0.0206976
- `grok-4.3` — cost=0.00068642
- `x-ai/grok-4.6` — cost=0.00057083
- `grok-4.7` — cost=0.01008523
- `google/gemini-3.1-flash-lite` — cost=0.0016889
- `minimax/minimax-m3` — cost=0.00282679
- `minimax/minimax-m2.7` — cost=0.00039176
- `minimax/minimax-m2.5` — cost=0.0011847
- `xiaomi/mimo-v2.5-pro` — cost=0.00111104
- `xiaomi/mimo-v2.5` — cost=0.00054218
- `mimo-v2.6-pro` — cost=0.00422323
- `mimo-v2.6-flash` — cost=0.00363012
- `moonshotai/kimi-k3` — cost=0.006786
- `deepseek-v4-flash-0731:free` — cost={'completion_tokens': 64, 'prompt_tokens': 84, 'total_tokens': 148}

Не отвечают (3):

- `nemotron-3-super-120b-a12b` — PlusVibe HTTP 429 POST /v1/chat/completions: {"error":{"message":"Все провайдеры этой модели временно недоступны. Повтор
- `perplexity/sonar-reasoning-pro` — PlusVibe HTTP 502 POST /v1/chat/completions: {"error":{"message":"Поставщик вернул ответ без текста: модель потратила ве
- `x-ai/grok-build-0.1` — The read operation timed out

## Ловушки в написании имён

- Дефис и точка — РАЗНЫЕ модели: `grok-imagine-image-2-0` (2.71 ₽) и `grok-imagine-image-2.0` (4.02 ₽); `seedance-2-0-mini` и `seedance-2.0`; `wan-2-7` и `wan2.7-r2v`; `kling-v3.0` и `kling-v3-turbo`.
- Часть моделей требует явный пин провайдера: `ideogram-v3` без пина → 503 `requires_provider_pin`; работают `ideogram-v3:pixel` (4.74 ₽) и `ideogram-v3:rep` (7.54 ₽).
- Пин через суффикс работает и у других: `seedream-5-0-pro:white`, `seedance-2.0-fast-face:white`, `grok-imagine-image-2.0:white`, `suno:white`, `nano-banana-2:white`, `gemini-3.8-flash-tts:flow` — все принялись. Но `flux-2:white` → 503 `unsupported_route` (у flux-2 пина нет, звать просто `flux-2`).
- Алиасы: `gpt-image-1.5` = `gpt-image-1-5`; `gemini-2.5-flash-image` = `nano-banana`; `qwen-image-3.0` = `qwen3-image`; `gemini-3.1-flash-tts` = `gemini-tts`. Устаревший `gemini-3.1-flash-image` (sunset 2026-10-31) → переходить на `gemini-2.5-flash-image`.
- Ошибки распознавания: `unknown_model` — имени нет вообще; `incompatible_params` (503) — модель есть, но маршрут/провайдер выключен; `unsupported_route` (503) — такого пина нет; 422 — не хватает входного файла.

---

# Разбор двух конкретных моделей (2026-10-17)

Всё проверено живыми запросами; повтор: `python3 pv_check_models.py <model> [<model>…]`
(< 0.1 ₽ на модель, печатает чек-лист: текст / stream / stream+tools / картинка / max_tokens).

## `qwen3.8-omni-flash` — работает, но есть две ловушки

✅ работает: текст, стриминг (SSE), tools (и в стриме), картинка — **но по https-ссылке**.

1. **Картинка не принимется base64 / data-URI.** `{"type":"image_url","image_url":{"url":"data:image/png;base64,…"}}` →
   HTTP 400 `Некорректный запрос: проверьте параметры и формат запроса`. Загрузка в `POST /v1/files` тоже не помогает
   (id файла в chat не подставляется — ответ не содержит url). Работает только публичный **https URL**:
   проверил на `raw.githubusercontent.com` — модель реально видит картинку («Бабушка.»).
   Нерабочая ссылка даёт 400 `Не удалось получить изображение по ссылке: …` (отличается от 400 про формат).
2. **`max_tokens` не ограничивает reasoning.** С `max_tokens=1` ушло 61 completion-токенов (205 знаков reasoning),
   `finish=length`, а текст всё равно пришёл. Лечится **`reasoning_effort: "none"`** (или `enable_thinking: false` /
   `thinking: {"type":"disabled"}`): 3 токена вместо 61, цена 0.000019 ₽ вместо 0.000191 ₽ (в 10 раз), ответ 1.5 с вместо 2.4 с.
3. `max_completion_tokens` тоже игнорируется. Метaданные врут про модальности (`text,image,video`) — видео не проверял.

## `xiaomi/mimo-v2.5` — маршрут сломан/непредсказуем, не рекомендуется

1. **Скрытая преамбула ~1129 токенов на КАЖДЫЙ запрос** (в `usage.prompt_tokens`, cached ~1110). Даже на «ping» —
   платишь за 1.1k промпта (~0.0009 ₽/вызов). У `mimo-v2.5-pro` тот же запрос — 147 токенов.
2. **Постоянные «заготовки» в ответах** на китайском/английском вместо работы: «**I am MiMo-V2.5.** 无法在当前接口中调用工具。»,
   «底层已就绪，指令完全生效» — независимо от промпта, температуры и tools.
3. **Игнорирует `max_tokens` и `reasoning_effort`** целиком: `max_tokens=1` → 57 токенов ответа;
   один раз на `max_tokens=1` вернул 2240 токенов (1290 знаков, 0.0169 ₽).
4. **tools нестабильны**: то `finish_reason=tool_calls`, то обычный текст «нет доступа к файлу»; в стриме
   `tool_calls` то есть, то нет. Словом, для агента негодна.
5. Метаданные модели врёт: `architecture.input_modalities = ["text"]`, при этом картинку по URL принял (и ответила
   «MiMo-V2.5» вместо описания).
6. Один из 3 вызовов подряд один раз отдал 503 «Все провайдеры этой модели временно недоступны».

**Замена:** `xiaomi/mimo-v2.5-pro` — преамбулы нет (147), стрим и stream+tools работают, картинку читает верно
(«Бабушка.»), но дороже (0.0012–0.014 ₽/вызов) и `max_tokens` тоже не соблюдает.

## Общая ловушка: `max_tokens` не режет reasoning

Проверено на `qwen3.8-omni-flash`, `xiaomi/mimo-v2.5`, `xiaomi/mimo-v2.5-pro`, `mimo-v2.6-flash`, `qwen3.8-flash`(нет)
— у рассуждающих маршрутов лимит не применяется к reasoning-токам. Если нужен жёсткий контроль цены/длины:
выключать thinking (`reasoning_effort: "none"`) или считать бюджет самому, а не надеяться на `max_tokens`.
