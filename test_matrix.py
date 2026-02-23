#!/usr/bin/env python3
"""Test matrix multiplication animation"""

import requests
import json
import time

API_URL = 'http://localhost:8000'

# Create animation with matrix multiplication
print('🚀 Testing Matrix Multiplication Animation\n')
print('='*60)

payload = {
    'description': 'Explain matrix multiplication visually with two 2x2 matrices'
}

response = requests.post(f'{API_URL}/api/v1/animations', json=payload)
session_id = response.json()['session_id']
print(f'✓ Session created: {session_id}\n')

# Wait for plan completion
print('⏳ Step 1: Planning...\n')
plan_ready = False
for i in range(60):  # Wait up to 2 minutes
    time.sleep(2)
    response = requests.get(f'{API_URL}/api/v1/animations/{session_id}/status')
    status = response.json()
    
    print(f'📋 [{status["progress"]:3.0f}%] {status["stage"].upper()}: {status["message"]}')
    
    if status['stage'] == 'plan_ready':
        plan_ready = True
        print('\n✓ Plan ready!')
        
        # Get and display plan
        response = requests.get(f'{API_URL}/api/v1/animations/{session_id}/plan')
        plan = response.json()
        print(f'   Title: {plan["scene_title"]}')
        print(f'   Duration: {plan["duration"]}s')
        print(f'   Objects: {len(plan["objects"])}')
        print(f'   Timeline Events: {len(plan["timeline"])}')
        print(f'\n📝 Visual Description:')
        print(f'   {plan.get("visual_description", "N/A")[:200]}...')
        break
    
    if status['stage'] == 'failed':
        print(f'\n❌ Failed: {status.get("error")}')
        exit(1)

if not plan_ready:
    print('\n⏰ Timeout waiting for plan')
    exit(1)

# Trigger code generation
print('\n⏳ Step 2: Generating Code...\n')
response = requests.post(f'{API_URL}/api/v1/animations/{session_id}/generate-code')
if response.status_code != 200:
    print(f'❌ Failed to start code generation: {response.text}')
    exit(1)

# Wait for code completion
for i in range(30):
    time.sleep(2)
    response = requests.get(f'{API_URL}/api/v1/animations/{session_id}/status')
    status = response.json()
    
    print(f'💻 [{status["progress"]:3.0f}%] {status["stage"].upper()}: {status["message"]}')
    
    if status['stage'] == 'code_ready':
        print('\n✓ Code ready!')
        
        # Get and display code
        response = requests.get(f'{API_URL}/api/v1/animations/{session_id}/code')
        code_data = response.json()
        print(f'   Scene: {code_data["scene_class_name"]}')
        print(f'   Lines: {len(code_data["code"].splitlines())}')
        break
    
    if status['stage'] == 'failed':
        print(f'\n❌ Failed: {status.get("error")}')
        exit(1)

# Trigger video rendering
print('\n⏳ Step 3: Rendering Video...\n')
response = requests.post(f'{API_URL}/api/v1/animations/{session_id}/render')
if response.status_code != 200:
    print(f'❌ Failed to start rendering: {response.text}')
    exit(1)

# Wait for rendering completion
for i in range(60):
    time.sleep(3)
    response = requests.get(f'{API_URL}/api/v1/animations/{session_id}/status')
    status = response.json()
    
    print(f'🎬 [{status["progress"]:3.0f}%] {status["stage"].upper()}: {status["message"]}')
    
    if status['stage'] == 'completed':
        print(f'\n✅ SUCCESS! Video ready!')
        print(f'   Video URL: {API_URL}{status["video_url"]}')
        print(f'\n🎉 Matrix multiplication animation complete!')
        break
    
    if status['stage'] == 'failed':
        print(f'\n❌ Failed: {status.get("error")}')
        exit(1)
