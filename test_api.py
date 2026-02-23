#!/usr/bin/env python3
"""Comprehensive test script for the Manim Animation API"""

import requests
import json
import time

API_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    response = requests.get(f"{API_URL}/health")
    print(f"✓ Health check: {response.json()}")

def wait_for_stage(session_id, target_stages, timeout=60):
    """Poll status until reaching target stage or failure"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(2)
        response = requests.get(f"{API_URL}/api/v1/animations/{session_id}/status")
        status = response.json()
        
        print(f"  Stage: {status['stage']} | Progress: {status['progress']}% | {status['message']}")
        
        if status['stage'] in target_stages:
            return status
        
        if status['stage'] == 'failed':
            print(f"\n❌ Failed: {status.get('error', 'Unknown error')}")
            return None
    
    print(f"\n⏰ Timeout waiting for stage")
    return None

def test_full_workflow():
    """Test complete workflow: planning → code generation → video rendering"""
    
    # Step 1: Create animation and wait for plan
    print("\n📝 Step 1: Creating animation and generating plan...")
    payload = {
        "description": "Create a simple animation showing a blue circle transforming into a red square"
    }
    
    response = requests.post(f"{API_URL}/api/v1/animations", json=payload)
    data = response.json()
    session_id = data["session_id"]
    print(f"✓ Session created: {session_id}")
    
    print("\n⏳ Waiting for plan generation...")
    status = wait_for_stage(session_id, ['plan_ready'], timeout=30)
    if not status:
        return None
    
    print("\n✓ Plan ready!")
    
    # Get the plan
    response = requests.get(f"{API_URL}/api/v1/animations/{session_id}/plan")
    plan = response.json()
    print(f"\n📋 Generated Plan:")
    print(json.dumps(plan, indent=2)[:500] + "..." if len(json.dumps(plan)) > 500 else json.dumps(plan, indent=2))
    
    # Step 2: Generate code
    print("\n\n💻 Step 2: Generating Manim code...")
    response = requests.post(f"{API_URL}/api/v1/animations/{session_id}/generate-code")
    if response.status_code != 200:
        print(f"❌ Failed to start code generation: {response.text}")
        return None
    
    print("\n⏳ Waiting for code generation...")
    status = wait_for_stage(session_id, ['code_ready'], timeout=30)
    if not status:
        return None
    
    print("\n✓ Code ready!")
    
    # Get the code
    response = requests.get(f"{API_URL}/api/v1/animations/{session_id}/code")
    code_data = response.json()
    print(f"\n📄 Generated Code Preview:")
    print(f"Scene Class: {code_data.get('scene_class_name', 'N/A')}")
    code_preview = code_data.get('code', '')[:300]
    print(f"Code (first 300 chars):\n{code_preview}...")
    
    # Step 3: Render video
    print("\n\n🎬 Step 3: Rendering video with Manim...")
    response = requests.post(f"{API_URL}/api/v1/animations/{session_id}/render")
    if response.status_code != 200:
        print(f"❌ Failed to start rendering: {response.text}")
        return None
    
    print("\n⏳ Waiting for video rendering (this may take a while)...")
    status = wait_for_stage(session_id, ['completed'], timeout=120)
    if not status:
        return None
    
    print("\n✓ Video rendered successfully!")
    
    # Get video URL
    if status.get('video_url'):
        print(f"\n🎥 Video URL: {status['video_url']}")
    
    return session_id

if __name__ == "__main__":
    print("🚀 Testing Complete Manim Animation API Workflow")
    print("="*60)
    print("This will test: Planning → Code Generation → Video Rendering\n")
    
    # Test health
    test_health()
    
    # Test full workflow
    session_id = test_full_workflow()
    
    if session_id:
        print(f"\n\n✅ ALL TESTS PASSED!")
        print(f"   Session ID: {session_id}")
        print(f"\n💡 API Endpoints tested:")
        print(f"   ✓ POST /api/v1/animations (create session)")
        print(f"   ✓ GET  /api/v1/animations/{session_id}/status (polling)")
        print(f"   ✓ GET  /api/v1/animations/{session_id}/plan (view plan)")
        print(f"   ✓ POST /api/v1/animations/{session_id}/generate-code (code gen)")
        print(f"   ✓ GET  /api/v1/animations/{session_id}/code (view code)")
        print(f"   ✓ POST /api/v1/animations/{session_id}/render (video render)")
        print(f"\n🎉 Full workflow completed successfully!")
    else:
        print("\n\n❌ TEST FAILED - Check errors above")
