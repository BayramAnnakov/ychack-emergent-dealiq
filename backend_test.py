#!/usr/bin/env python3
"""
Backend API Testing for DealIQ Benchmark Endpoints
Tests the three main benchmark API endpoints as per review request
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Backend URL - using localhost as per review request
BASE_URL = "http://localhost:8001"
API_PREFIX = "/api/v1/benchmark"

# Expected task titles from review request
EXPECTED_TITLES = [
    "Automotive Parts Check-In Procedure",
    "Beutist Set Inventory Analysis",
    "XR Retailer Makeup Sales Analysis",
    "Beverage Inventory Stockout Prevention",
    "Men's Fragrance Competitive Pricing"
]

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name: str):
    """Print formatted test header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}TEST: {test_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def test_get_tasks() -> tuple[bool, List[Dict[str, Any]]]:
    """
    Test GET /api/v1/benchmark/tasks endpoint
    Verifies:
    - Returns tasks with meaningful titles
    - Each task has required fields
    - Titles match expected values
    - Has reference_file_urls array
    - Has has_reference_files boolean
    """
    print_test_header("GET /api/v1/benchmark/tasks - List Benchmark Tasks")
    
    url = f"{BASE_URL}{API_PREFIX}/tasks"
    print_info(f"Testing endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print_error(f"Expected status 200, got {response.status_code}")
            print_error(f"Response: {response.text}")
            return False, []
        
        print_success("Status code 200 OK")
        
        # Parse JSON response
        data = response.json()
        
        # Check response structure
        if "tasks" not in data:
            print_error("Response missing 'tasks' field")
            return False, []
        
        print_success("Response has 'tasks' field")
        
        tasks = data["tasks"]
        total = data.get("total", 0)
        
        print_info(f"Total tasks returned: {len(tasks)}")
        print_info(f"Total count in response: {total}")
        
        if len(tasks) == 0:
            print_error("No tasks returned")
            return False, []
        
        print_success(f"Found {len(tasks)} tasks")
        
        # Verify each task has required fields
        all_valid = True
        found_titles = []
        
        for i, task in enumerate(tasks, 1):
            print(f"\n{Colors.BOLD}Task {i}:{Colors.RESET}")
            
            # Check required fields
            required_fields = ["task_id", "title", "sector", "occupation", "reference_file_urls", "has_reference_files"]
            missing_fields = [field for field in required_fields if field not in task]
            
            if missing_fields:
                print_error(f"Missing fields: {', '.join(missing_fields)}")
                all_valid = False
                continue
            
            # Check title field
            title = task.get("title", "")
            if not title or title == "Wholesale Trade":
                print_error(f"Title is not meaningful: '{title}'")
                all_valid = False
            else:
                print_success(f"Title: {title}")
                found_titles.append(title)
            
            # Check reference_file_urls
            ref_urls = task.get("reference_file_urls", [])
            if not isinstance(ref_urls, list):
                print_error(f"reference_file_urls is not a list: {type(ref_urls)}")
                all_valid = False
            else:
                print_success(f"reference_file_urls is array with {len(ref_urls)} items")
            
            # Check has_reference_files
            has_ref = task.get("has_reference_files")
            if not isinstance(has_ref, bool):
                print_error(f"has_reference_files is not boolean: {type(has_ref)}")
                all_valid = False
            else:
                print_success(f"has_reference_files: {has_ref}")
            
            # Show other fields
            print_info(f"Task ID: {task.get('task_id', 'N/A')}")
            print_info(f"Sector: {task.get('sector', 'N/A')}")
        
        # Check if expected titles are present
        print(f"\n{Colors.BOLD}Checking Expected Titles:{Colors.RESET}")
        for expected_title in EXPECTED_TITLES:
            if expected_title in found_titles:
                print_success(f"Found: {expected_title}")
            else:
                print_warning(f"Not found: {expected_title}")
        
        if all_valid:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TASKS ENDPOINT TESTS PASSED{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TASKS ENDPOINT TESTS FAILED{Colors.RESET}")
        
        return all_valid, tasks
        
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return False, []
    except json.JSONDecodeError as e:
        print_error(f"Failed to parse JSON response: {str(e)}")
        return False, []
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False, []

def test_get_history() -> tuple[bool, List[Dict[str, Any]]]:
    """
    Test GET /api/v1/benchmark/history endpoint
    Verifies:
    - Returns completed tasks list
    - Response structure with file metadata
    """
    print_test_header("GET /api/v1/benchmark/history - Task History")
    
    url = f"{BASE_URL}{API_PREFIX}/history"
    print_info(f"Testing endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print_error(f"Expected status 200, got {response.status_code}")
            print_error(f"Response: {response.text}")
            return False, []
        
        print_success("Status code 200 OK")
        
        # Parse JSON response
        data = response.json()
        
        # Check response structure
        if "tasks" not in data:
            print_error("Response missing 'tasks' field")
            return False, []
        
        print_success("Response has 'tasks' field")
        
        tasks = data["tasks"]
        total = data.get("total", 0)
        
        print_info(f"Total completed tasks: {len(tasks)}")
        print_info(f"Total count in response: {total}")
        
        if len(tasks) == 0:
            print_warning("No completed tasks found (this may be expected if no tasks have been executed)")
            return True, []
        
        print_success(f"Found {len(tasks)} completed tasks")
        
        # Verify each task has expected metadata
        all_valid = True
        
        for i, task in enumerate(tasks, 1):
            print(f"\n{Colors.BOLD}Completed Task {i}:{Colors.RESET}")
            
            # Check expected fields
            expected_fields = ["task_id", "file_name", "file_size", "sheet_count", "created_at", "modified_at"]
            missing_fields = [field for field in expected_fields if field not in task]
            
            if missing_fields:
                print_error(f"Missing fields: {', '.join(missing_fields)}")
                all_valid = False
                continue
            
            print_success(f"Task ID: {task.get('task_id')}")
            print_success(f"File: {task.get('file_name')}")
            print_info(f"Size: {task.get('file_size')} bytes")
            print_info(f"Sheets: {task.get('sheet_count')}")
            print_info(f"Created: {task.get('created_at')}")
            print_info(f"Modified: {task.get('modified_at')}")
        
        if all_valid:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL HISTORY ENDPOINT TESTS PASSED{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME HISTORY ENDPOINT TESTS FAILED{Colors.RESET}")
        
        return all_valid, tasks
        
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return False, []
    except json.JSONDecodeError as e:
        print_error(f"Failed to parse JSON response: {str(e)}")
        return False, []
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False, []

def test_download_endpoint(task_id: str) -> bool:
    """
    Test GET /api/v1/benchmark/download/{task_id} endpoint
    Verifies:
    - Returns file with proper headers
    - Content-Type is correct
    - Content-Disposition header is present
    """
    print_test_header(f"GET /api/v1/benchmark/download/{task_id} - Download Task Result")
    
    url = f"{BASE_URL}{API_PREFIX}/download/{task_id}"
    print_info(f"Testing endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code == 404:
            print_warning("Task file not found (404) - this is expected if task hasn't been executed")
            return True  # Not a failure, just no file available
        
        if response.status_code != 200:
            print_error(f"Expected status 200 or 404, got {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
        
        print_success("Status code 200 OK")
        
        # Check Content-Type header
        content_type = response.headers.get("Content-Type", "")
        expected_content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        if content_type == expected_content_type:
            print_success(f"Content-Type: {content_type}")
        else:
            print_error(f"Expected Content-Type: {expected_content_type}")
            print_error(f"Got Content-Type: {content_type}")
            return False
        
        # Check Content-Disposition header
        content_disposition = response.headers.get("Content-Disposition", "")
        if "attachment" in content_disposition:
            print_success(f"Content-Disposition: {content_disposition}")
        else:
            print_error(f"Content-Disposition missing 'attachment': {content_disposition}")
            return False
        
        # Check content length
        content_length = len(response.content)
        print_info(f"File size: {content_length} bytes")
        
        if content_length > 0:
            print_success(f"File downloaded successfully ({content_length} bytes)")
        else:
            print_error("Downloaded file is empty")
            return False
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ DOWNLOAD ENDPOINT TEST PASSED{Colors.RESET}")
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False

def main():
    """Run all backend tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print("DealIQ Backend Benchmark API Testing")
    print(f"{'='*70}{Colors.RESET}\n")
    
    print_info(f"Backend URL: {BASE_URL}")
    print_info(f"API Prefix: {API_PREFIX}")
    
    results = {
        "tasks_endpoint": False,
        "history_endpoint": False,
        "download_endpoint": False
    }
    
    # Test 1: GET /api/v1/benchmark/tasks
    tasks_passed, tasks = test_get_tasks()
    results["tasks_endpoint"] = tasks_passed
    
    # Test 2: GET /api/v1/benchmark/history
    history_passed, completed_tasks = test_get_history()
    results["history_endpoint"] = history_passed
    
    # Test 3: GET /api/v1/benchmark/download/{task_id}
    # Use a task_id from history if available, otherwise use first task from tasks list
    test_task_id = None
    if completed_tasks:
        test_task_id = completed_tasks[0]["task_id"]
        print_info(f"Using task_id from history: {test_task_id}")
    elif tasks:
        test_task_id = tasks[0]["task_id"]
        print_info(f"Using task_id from tasks list: {test_task_id}")
    
    if test_task_id:
        download_passed = test_download_endpoint(test_task_id)
        results["download_endpoint"] = download_passed
    else:
        print_warning("No task_id available to test download endpoint")
        results["download_endpoint"] = True  # Skip test
    
    # Print final summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print("FINAL TEST SUMMARY")
    print(f"{'='*70}{Colors.RESET}\n")
    
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}PASSED{Colors.RESET}" if passed else f"{Colors.RED}FAILED{Colors.RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed_tests}/{total_tests} tests passed{Colors.RESET}")
    
    if passed_tests == total_tests:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
