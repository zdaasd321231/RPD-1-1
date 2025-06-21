import requests
import sys
import time
from datetime import datetime

class RDPStealthAPITester:
    def __init__(self, base_url="https://b1191014-47f2-402f-837b-c274a506cf7a.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.headers = {'Content-Type': 'application/json'}

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        
        if self.token:
            self.headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=self.headers, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers, params=params)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health check endpoint"""
        return self.run_test(
            "API Health Check",
            "GET",
            "",
            200
        )

    def test_login(self, username, password, totp_code=None):
        """Test login and get token"""
        data = {"username": username, "password": password}
        if totp_code:
            data["totp_code"] = totp_code
            
        success, response = self.run_test(
            "Login",
            "POST",
            "auth/login",
            200,
            data=data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        return self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )

    def test_list_files(self):
        """Test file listing endpoint"""
        return self.run_test(
            "List Files",
            "GET",
            "files/list",
            200
        )

    def test_rdp_connections(self):
        """Test RDP connections listing"""
        return self.run_test(
            "List RDP Connections",
            "GET",
            "rdp/connections",
            200
        )

    def test_create_rdp_connection(self):
        """Test creating an RDP connection"""
        data = {
            "host": "192.168.1.100",
            "port": 3389,
            "username": "test_user",
            "password": "test_password",
            "name": f"Test Connection {datetime.now().strftime('%H:%M:%S')}",
            "description": "Test connection created by automated test"
        }
        
        return self.run_test(
            "Create RDP Connection",
            "POST",
            "rdp/connections",
            200,
            data=data
        )

    def test_active_sessions(self):
        """Test active sessions endpoint"""
        return self.run_test(
            "Active Sessions",
            "GET",
            "sessions/active",
            200
        )

    def test_logs(self):
        """Test logs endpoint"""
        return self.run_test(
            "Logs",
            "GET",
            "logs",
            200
        )

    def test_settings(self):
        """Test settings endpoint"""
        return self.run_test(
            "Settings",
            "GET",
            "settings",
            200
        )

def main():
    # Setup
    tester = RDPStealthAPITester()
    
    # Test health check
    tester.test_health_check()
    
    # Test login
    if not tester.test_login("admin", "admin123"):
        print("❌ Login failed, stopping tests")
        return 1
    
    # Test authenticated endpoints
    tester.test_dashboard_stats()
    tester.test_list_files()
    tester.test_rdp_connections()
    success, response = tester.test_create_rdp_connection()
    
    if success:
        print("RDP Connection created successfully")
        # Could test more operations with the created connection here
    
    tester.test_active_sessions()
    tester.test_logs()
    tester.test_settings()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())