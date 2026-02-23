#!/usr/bin/env python3
"""Test code generation for vector projection"""

import requests
import time

API_URL = 'http://localhost:8000'
session_id = '5b1a2b50-5d55-47e8-a70c-9d7072232b5d'

print('🚀 Generating code for vector projection...\n')

# Trigger code generation
response = requests.post(f'{API_URL}/api/v1/animations/{session_id}/generate-code')
if response.status_code != 200:
    print(f'❌ Failed: {response.text}')
    exit(1)

print('⏳ Waiting for code generation...\n')

# Wait for completion
for i in range(60):
    time.sleep(2)
    response = requests.get(f'{API_URL}/api/v1/animations/{session_id}/status')
    status = response.json()
    
    if status['stage'] == 'code_ready':
        print('✅ Code generated!\n')
        
        # Get the code
        response = requests.get(f'{API_URL}/api/v1/animations/{session_id}/code')
        code_data = response.json()
        
        print('='*70)
        print('GENERATED MANIM CODE')
        print('='*70)
        print(f'Scene Class: {code_data["scene_class_name"]}')
        print(f'Total Lines: {len(code_data["code"].splitlines())}')
        print(f'\nCode Preview (first 40 lines):')
        print('-'*70)
        lines = code_data['code'].splitlines()
        for i, line in enumerate(lines[:40], 1):
            print(f'{i:3d} | {line}')
        if len(lines) > 40:
            print(f'... ({len(lines) - 40} more lines)')
        
        print(f'\n✅ Full code saved to:')
        print(f'   storage/sessions/{session_id}/animation.py')
        break
    
    if status['stage'] == 'failed':
        print(f'❌ Failed: {status.get("error")}')
        break
    
    if i % 5 == 0:
        print(f'  [{status["progress"]:.0f}%] {status["message"]}')
