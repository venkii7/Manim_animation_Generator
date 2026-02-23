#!/usr/bin/env python3
"""Test vector projection animation"""

import requests
import time

API_URL = 'http://localhost:8000'

print('🚀 Testing: Projection of Vector A on B\n')
print('='*60)

# Create animation
payload = {'description': 'Explain the projection of vector A on vector B visually'}
response = requests.post(f'{API_URL}/api/v1/animations', json=payload)
session_id = response.json()['session_id']
print(f'✓ Session created: {session_id}\n')

print('⏳ Waiting for plan generation...\n')

# Wait for plan
for i in range(60):
    time.sleep(2)
    response = requests.get(f'{API_URL}/api/v1/animations/{session_id}/status')
    status = response.json()
    
    if status['stage'] == 'plan_ready':
        print('✓ Plan ready!\n')
        
        # Get plan
        response = requests.get(f'{API_URL}/api/v1/animations/{session_id}/plan')
        plan = response.json()
        
        print('='*60)
        print('ANIMATION PLAN')
        print('='*60)
        print(f'Title: {plan["scene_title"]}')
        print(f'Duration: {plan["duration"]}s')
        print(f'Objects: {len(plan["objects"])}')
        print(f'Timeline Events: {len(plan["timeline"])}')
        print()
        print('VISUAL DESCRIPTION:')
        print('-'*60)
        print(plan["visual_description"])
        print()
        print('FIRST 5 ANIMATION STEPS:')
        print('-'*60)
        for idx, event in enumerate(plan["timeline"][:5]):
            print(f'{idx+1}. [{event["start_time"]}s] {event["description"]}')
        
        print(f'\n✅ Complete plan saved to:')
        print(f'   storage/sessions/{session_id}/plan.json')
        break
    
    if status['stage'] == 'failed':
        print(f'❌ Failed: {status.get("error")}')
        break
    
    if i % 5 == 0:
        print(f'  [{status["progress"]:.0f}%] {status["message"]}')
