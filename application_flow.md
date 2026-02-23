┌─────────────────────────────────────────────────────────────────────┐
│                    USER JOURNEY & DATA FLOW                         │
└─────────────────────────────────────────────────────────────────────┘

STAGE 0: USER INPUT
├─ User enters idea: "matrix multiplication visualization"
├─ Frontend sends POST /api/v1/animations
└─ Backend creates session, returns session_id
     │
     ▼
STAGE 1: PLANNING (Gemini Flash 2.5)
├─ Backend → Gemini API: Generate structured JSON plan
│  ├─ System instruction: "You are a Manim planner"
│  ├─ Response schema: AnimationPlan (objects[], timeline[])
│  └─ Returns: JSON with positions, colors, animations
├─ Backend saves plan.json to session folder
├─ Backend updates session status: "plan_ready"
└─ Frontend polls status, shows plan in JSON editor
     │
     ▼
STAGE 2: PLAN REVIEW & EDITING
├─ User reviews plan (Monaco JSON editor)
├─ Option A: Edit plan directly (modify JSON)
│  └─ Frontend sends PUT /api/v1/animations/{id}/plan
├─ Option B: Request regeneration with feedback
│  ├─ User adds text: "make circles bigger, use blue color"
│  ├─ Frontend sends POST /api/v1/animations/{id}/regenerate
│  └─ Backend → Gemini: Multi-turn chat with feedback
└─ Once satisfied, user clicks "Approve Plan"
     │
     ▼
STAGE 3: CODE GENERATION (Gemini Flash 2.5)
├─ Backend → Gemini API: Generate Manim Python code
│  ├─ Input: Approved plan (JSON)
│  ├─ System instruction: "Generate executable Manim code"
│  ├─ Response schema: ManimCode (code, imports, scene_name)
│  └─ Returns: Complete Python file
├─ Backend validates code (AST syntax check)
├─ Backend saves code.py to session folder
├─ Frontend shows code with syntax highlighting
└─ User can preview code or click "Render Video"
     │
     ▼
STAGE 4: CODE EXECUTION & RENDERING
├─ Backend runs: manim render -qh --format mp4 code.py SceneName
├─ Subprocess executes in isolated temp directory
├─ Manim generates video file (output/SceneName.mp4)
├─ Frontend polls status, shows progress bar
├─ Backend extracts video from Manim output directory
└─ Backend moves video to storage
     │
     ▼
STAGE 5: VIDEO STORAGE & HISTORY
├─ Backend generates thumbnail (ffmpeg screenshot at 2s)
├─ Backend saves to database:
│  ├─ animations table: (id, user_id, title, file_path, s3_key, 
│  │                      duration, resolution, tags, created_at)
│  └─ Links to session_id for traceability
├─ If using S3: Upload video + thumbnail
│  └─ storage/animations/{user_id}/{year}/{month}/{id}.mp4
├─ Generate presigned URL (1-hour expiry)
└─ Return video URL to frontend
     │
     ▼
STAGE 6: VIDEO DISPLAY
├─ Frontend shows video player with controls
├─ Download button (presigned URL)
├─ "Create Another" button (restart flow)
└─ "Add to Library" (already saved automatically)
     │
     ▼
STAGE 7: ANIMATION LIBRARY (History)
├─ User navigates to "My Animations" page
├─ Frontend sends GET /api/v1/animations
│  └─ Query params: page, limit, tags, search, sort
├─ Backend queries database, returns list with thumbnails
├─ Frontend displays grid view with:
│  ├─ Thumbnail previews
│  ├─ Duration, title, tags
│  ├─ Checkboxes for multi-select
│  └─ Actions: Download, Delete, Edit metadata
└─ User can select multiple animations for stitching
     │
     ▼
STAGE 8: MULTI-ANIMATION STITCHING
├─ User selects 2+ animations (checkboxes)
├─ Clicks "Stitch Selected"
├─ Frontend shows StitchComposer modal:
│  ├─ Drag-drop to reorder animations
│  ├─ Set transitions: none / fade / crossfade
│  ├─ Set transition durations
│  ├─ Title for stitched video
│  └─ Preview timeline (total duration)
├─ User clicks "Create Stitched Video"
├─ Frontend sends POST /api/v1/stitches
│  └─ Body: {animation_ids[], transitions[], title}
└─ Backend queues Celery task
     │
     ▼
STAGE 9: BACKGROUND STITCHING (Async Task)
├─ Celery worker picks up stitch job
├─ Fetches video files from storage
├─ Runs FFmpeg concat:
│  ├─ No transitions: concat demuxer (fast, no re-encoding)
│  └─ With transitions: filter complex (slower, re-encodes)
├─ Worker updates progress in Redis:
│  ├─ 10%: "Fetching videos..."
│  ├─ 30%: "Preparing stitch..."
│  ├─ 50%: "Stitching videos..."
│  ├─ 80%: "Uploading result..."
│  └─ 100%: "Completed!"
├─ Generates thumbnail for stitched video
├─ Saves to database (stitched_videos table)
└─ Updates status: "completed"
     │
     ▼
STAGE 10: STITCH COMPLETION
├─ Frontend polls GET /api/v1/stitches/{id} every 2s
│  └─ Or uses WebSocket for real-time updates
├─ Backend returns progress_percent + current_step
├─ When complete, returns video_url
├─ Frontend shows success message
├─ Displays video player with stitched result
└─ Download button available