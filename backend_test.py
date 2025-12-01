#!/usr/bin/env python3
"""
İnşaat Yapı Denetim Yönetim Sistemi - Backend API Test Suite
Test user: test@batlama.com / test123
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class ConstructionInspectionAPITester:
    def __init__(self, base_url="https://batlama-template.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_info = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test credentials
        self.test_email = "test@batlama.com"
        self.test_password = "test123"

    def log_test(self, name, success, details="", error_msg=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")
        if error_msg:
            print(f"    Error: {error_msg}")

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            return success, response.status_code, response_data

        except requests.exceptions.RequestException as e:
            return False, 0, {"error": str(e)}

    def test_login(self):
        """Test login functionality"""
        print("\n🔐 Testing Authentication...")
        
        success, status_code, response = self.make_request(
            'POST', 
            'auth/login',
            {"email": self.test_email, "password": self.test_password},
            200
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_info = response.get('user', {})
            self.log_test(
                "Login with test@batlama.com", 
                True, 
                f"User role: {self.user_info.get('role', 'unknown')}"
            )
            return True
        else:
            self.log_test(
                "Login with test@batlama.com", 
                False, 
                f"Status: {status_code}",
                response.get('detail', 'Login failed')
            )
            return False

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        print("\n📊 Testing Dashboard...")
        
        success, status_code, response = self.make_request('GET', 'dashboard/stats')
        
        if success:
            stats = response
            self.log_test(
                "Dashboard stats", 
                True, 
                f"Stats loaded: {list(stats.keys()) if isinstance(stats, dict) else 'Data received'}"
            )
        else:
            # Dashboard stats might not exist, try activities instead
            success2, status_code2, response2 = self.make_request('GET', 'activities')
            self.log_test(
                "Dashboard/Activities", 
                success2, 
                f"Activities count: {len(response2) if isinstance(response2, list) else 'Data received'}",
                response2.get('detail', '') if not success2 else ""
            )

    def test_constructions(self):
        """Test constructions (İnşaat Listesi) endpoints"""
        print("\n🏗️ Testing Constructions...")
        
        # Get constructions
        success, status_code, response = self.make_request('GET', 'constructions')
        self.log_test(
            "Get constructions list", 
            success, 
            f"Found {len(response) if isinstance(response, list) else 0} constructions",
            response.get('detail', '') if not success else ""
        )
        
        # Search constructions
        success, status_code, response = self.make_request('GET', 'constructions/search?q=test')
        self.log_test(
            "Search constructions", 
            success, 
            f"Search results: {len(response) if isinstance(response, list) else 0}",
            response.get('detail', '') if not success else ""
        )

    def test_inspections(self):
        """Test site inspections (Saha Denetimi) endpoints"""
        print("\n🔍 Testing Site Inspections...")
        
        # Get inspections
        success, status_code, response = self.make_request('GET', 'inspections')
        self.log_test(
            "Get inspections list", 
            success, 
            f"Found {len(response) if isinstance(response, list) else 0} inspections",
            response.get('detail', '') if not success else ""
        )
        
        # Create test inspection
        test_inspection = {
            "denetimTarihi": "2025-01-15",
            "kontrolEdilenBolum": "Temel Kontrolü",
            "insaatIsmi": "Test İnşaat",
            "yibfNo": "TEST-001",
            "ilce": "Test İlçe"
        }
        
        success, status_code, response = self.make_request(
            'POST', 
            'inspections', 
            test_inspection,
            200
        )
        
        inspection_id = None
        if success and isinstance(response, dict) and 'id' in response:
            inspection_id = response['id']
            
        self.log_test(
            "Create inspection", 
            success, 
            f"Created inspection ID: {inspection_id}" if inspection_id else "Creation attempted",
            response.get('detail', '') if not success else ""
        )
        
        return inspection_id

    def test_payments(self):
        """Test progress payments (Hakediş) endpoints"""
        print("\n💰 Testing Progress Payments...")
        
        # Get payments
        success, status_code, response = self.make_request('GET', 'payments')
        self.log_test(
            "Get payments list", 
            success, 
            f"Found {len(response) if isinstance(response, list) else 0} payments",
            response.get('detail', '') if not success else ""
        )
        
        # Create test payment
        test_payment = {
            "insaatIsmi": "Test İnşaat",
            "yibfNo": "TEST-001",
            "hakedisNo": "H-001",
            "hakedisTipi": "Ara Hakediş",
            "hakedisDurumu": "Hazırlanacak",
            "eksik": "Eksik Yok"
        }
        
        success, status_code, response = self.make_request(
            'POST', 
            'payments', 
            test_payment,
            200
        )
        
        payment_id = None
        if success and isinstance(response, dict) and 'id' in response:
            payment_id = response['id']
            
        self.log_test(
            "Create payment", 
            success, 
            f"Created payment ID: {payment_id}" if payment_id else "Creation attempted",
            response.get('detail', '') if not success else ""
        )
        
        return payment_id

    def test_licenses(self):
        """Test licenses (Ruhsat & Proje Takip) endpoints"""
        print("\n📋 Testing Licenses...")
        
        # Get licenses
        success, status_code, response = self.make_request('GET', 'licenses')
        self.log_test(
            "Get licenses list", 
            success, 
            f"Found {len(response) if isinstance(response, list) else 0} licenses",
            response.get('detail', '') if not success else ""
        )
        
        # Create test license
        test_license = {
            "insaatIsmi": "Test İnşaat",
            "yibfNo": "TEST-001",
            "yapiSahibiTapu": True,
            "yapiMuteahhitiSozlesme": True,
            "belediyeRuhsat": False
        }
        
        success, status_code, response = self.make_request(
            'POST', 
            'licenses', 
            test_license,
            200
        )
        
        license_id = None
        if success and isinstance(response, dict) and 'id' in response:
            license_id = response['id']
            
        self.log_test(
            "Create license", 
            success, 
            f"Created license ID: {license_id}" if license_id else "Creation attempted",
            response.get('detail', '') if not success else ""
        )
        
        return license_id

    def test_workplans(self):
        """Test work plans (İş Planı Takvimi) endpoints"""
        print("\n📅 Testing Work Plans...")
        
        # Get work plans
        success, status_code, response = self.make_request('GET', 'workplans')
        self.log_test(
            "Get work plans list", 
            success, 
            f"Found {len(response) if isinstance(response, list) else 0} work plans",
            response.get('detail', '') if not success else ""
        )

    def test_users_management(self):
        """Test user management (admin/superadmin only)"""
        print("\n👥 Testing User Management...")
        
        if not self.user_info or self.user_info.get('role') not in ['super_admin', 'admin']:
            self.log_test(
                "User management access", 
                False, 
                f"User role: {self.user_info.get('role', 'unknown')}", 
                "Insufficient permissions for user management"
            )
            return
        
        # Get users list
        success, status_code, response = self.make_request('GET', 'users')
        self.log_test(
            "Get users list", 
            success, 
            f"Found {len(response) if isinstance(response, list) else 0} users",
            response.get('detail', '') if not success else ""
        )

    def test_companies(self):
        """Test companies (Firma Yönetimi) endpoints"""
        print("\n🏢 Testing Companies...")
        
        # Get companies
        success, status_code, response = self.make_request('GET', 'companies')
        self.log_test(
            "Get companies list", 
            success, 
            f"Found {len(response) if isinstance(response, list) else 0} companies",
            response.get('detail', '') if not success else ""
        )

    def test_activities(self):
        """Test activity logs"""
        print("\n📝 Testing Activity Logs...")
        
        success, status_code, response = self.make_request('GET', 'activities')
        self.log_test(
            "Get activity logs", 
            success, 
            f"Found {len(response) if isinstance(response, list) else 0} activities",
            response.get('detail', '') if not success else ""
        )

    def cleanup_test_data(self, inspection_id=None, payment_id=None, license_id=None):
        """Clean up test data (if user has permissions)"""
        print("\n🧹 Cleaning up test data...")
        
        if not self.user_info or self.user_info.get('role') not in ['super_admin', 'admin']:
            self.log_test("Cleanup", False, "", "Insufficient permissions for cleanup")
            return
        
        # Clean up inspection
        if inspection_id:
            success, status_code, response = self.make_request('DELETE', f'inspections/{inspection_id}')
            self.log_test(
                "Cleanup inspection", 
                success, 
                f"Deleted inspection {inspection_id}" if success else "Cleanup attempted",
                response.get('detail', '') if not success else ""
            )
        
        # Clean up payment
        if payment_id:
            success, status_code, response = self.make_request('DELETE', f'payments/{payment_id}')
            self.log_test(
                "Cleanup payment", 
                success, 
                f"Deleted payment {payment_id}" if success else "Cleanup attempted",
                response.get('detail', '') if not success else ""
            )
        
        # Clean up license
        if license_id:
            success, status_code, response = self.make_request('DELETE', f'licenses/{license_id}')
            self.log_test(
                "Cleanup license", 
                success, 
                f"Deleted license {license_id}" if success else "Cleanup attempted",
                response.get('detail', '') if not success else ""
            )

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting İnşaat Yapı Denetim Yönetim Sistemi API Tests")
        print(f"🌐 Backend URL: {self.base_url}")
        print(f"👤 Test User: {self.test_email}")
        print("=" * 60)
        
        # Authentication is required for all other tests
        if not self.test_login():
            print("\n❌ Login failed - cannot continue with other tests")
            return False
        
        # Test all modules
        self.test_dashboard_stats()
        self.test_constructions()
        
        # Test CRUD operations and collect IDs for cleanup
        inspection_id = self.test_inspections()
        payment_id = self.test_payments()
        license_id = self.test_licenses()
        
        # Test other modules
        self.test_workplans()
        self.test_users_management()
        self.test_companies()
        self.test_activities()
        
        # Cleanup test data
        self.cleanup_test_data(inspection_id, payment_id, license_id)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Show failed tests
        failed_tests = [t for t in self.test_results if not t['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  - {test['test_name']}: {test['error']}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = ConstructionInspectionAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results = {
        "summary": {
            "total_tests": tester.tests_run,
            "passed_tests": tester.tests_passed,
            "failed_tests": tester.tests_run - tester.tests_passed,
            "success_rate": (tester.tests_passed/tester.tests_run*100) if tester.tests_run > 0 else 0,
            "test_timestamp": datetime.now().isoformat(),
            "backend_url": tester.base_url,
            "test_user": tester.test_email
        },
        "detailed_results": tester.test_results,
        "user_info": tester.user_info
    }
    
    with open('/app/backend_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())