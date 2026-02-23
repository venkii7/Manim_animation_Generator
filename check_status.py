#!/usr/bin/env python3
"""Check backend status and test results"""

import requests
import os
import json

print('🔍 BACKEND STATUS CHECK')
print('='*70)

# Check API
try:
    response = requests.get('http://localhost:8000/health', timeout=2)
    print('✓ API Server: Running on http://localhost:8000')
    print(f'✓ Health Check: {response.json()["status"]}')
except:
    print('❌ API Server: Not responding')
    exit(1)

# Check sessions
sessions_dir = 'storage/sessions'
if os.path.exists(sessions_dir):
    sessions = [d for d in os.listdir(sessions_dir) if os.path.isdir(os.path.join(sessions_dir, d))]
    print(f'✓ Total Sessions Created: {len(sessions)}')
    
    # Analyze completions
    completed = 0
    with_plan = 0
    with_code = 0
    with_video = 0
    
    for s in sessions:
        session_path = os.path.join(sessions_dir, s)
        if os.path.exists(os.path.join(session_path, 'plan.json')):
            with_plan += 1
        if os.path.exists(os.path.join(session_path, 'code.json')):
            with_code += 1
        if os.path.exists(os.path.join(session_path, 'output/animation.mp4')):
            with_video += 1
            completed += 1
    
    print(f'\n📊 Completion Stats:')
    print(f'   Plans Generated: {with_plan}/{len(sessions)}')
    print(f'   Code Generated: {with_code}/{len(sessions)}')
    print(f'   Videos Rendered: {with_video}/{len(sessions)}')
    
    # Show recent sessions
    recent = sorted(sessions, key=lambda x: os.path.getmtime(os.path.join(sessions_dir, x)), reverse=True)[:5]
    print(f'\n📁 Recent 5 Sessions:')
    for idx, s in enumerate(recent, 1):
        session_path = os.path.join(sessions_dir, s)
        
        # Read metadata
        metadata_file = os.path.join(session_path, 'metadata.json')
        if os.path.exists(metadata_file):
            with open(metadata_file) as f:
                metadata = json.load(f)
                desc = metadata.get('user_input', 'N/A')[:40]
                stage = metadata.get('stage', 'unknown')
        else:
            desc = 'N/A'
            stage = 'unknown'
        
        has_plan = os.path.exists(os.path.join(session_path, 'plan.json'))
        has_code = os.path.exists(os.path.join(session_path, 'code.json'))
        has_video = os.path.exists(os.path.join(session_path, 'output/animation.mp4'))
        
        status_parts = []
        if has_plan: status_parts.append('Plan✓')
        if has_code: status_parts.append('Code✓')
        if has_video: status_parts.append('Video✓')
        
        status_str = ' → '.join(status_parts) if status_parts else 'Empty'
        print(f'\n   {idx}. {desc}...')
        print(f'      ID: {s}')
        print(f'      Stage: {stage}')
        print(f'      Status: {status_str}')

print('\n' + '='*70)
print('✅ Backend is operational!')
