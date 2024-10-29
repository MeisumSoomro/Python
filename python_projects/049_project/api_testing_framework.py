import requests
import json
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import yaml
import jsonschema
from concurrent.futures import ThreadPoolExecutor
import time
import csv
from jinja2 import Template

class TestStatus:
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"

class APITest:
    def __init__(self, name: str, endpoint: str, method: str = "GET"):
        self.name = name
        self.endpoint = endpoint
        self.method = method.upper()
        self.headers: Dict = {}
        self.params: Dict = {}
        self.body: Optional[Dict] = None
        self.expected_status: int = 200
        self.expected_schema: Optional[Dict] = None
        self.expected_contains: List[str] = []
        self.setup_scripts: List[str] = []
        self.cleanup_scripts: List[str] = []
        self.timeout: int = 30
        self.retry_count: int = 0
        self.dependencies: List[str] = []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "endpoint": self.endpoint,
            "method": self.method,
            "headers": self.headers,
            "params": self.params,
            "body": self.body,
            "expected_status": self.expected_status,
            "expected_schema": self.expected_schema,
            "expected_contains": self.expected_contains,
            "setup_scripts": self.setup_scripts,
            "cleanup_scripts": self.cleanup_scripts,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "dependencies": self.dependencies
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'APITest':
        test = cls(data["name"], data["endpoint"], data["method"])
        test.headers = data.get("headers", {})
        test.params = data.get("params", {})
        test.body = data.get("body")
        test.expected_status = data.get("expected_status", 200)
        test.expected_schema = data.get("expected_schema")
        test.expected_contains = data.get("expected_contains", [])
        test.setup_scripts = data.get("setup_scripts", [])
        test.cleanup_scripts = data.get("cleanup_scripts", [])
        test.timeout = data.get("timeout", 30)
        test.retry_count = data.get("retry_count", 0)
        test.dependencies = data.get("dependencies", [])
        return test

class TestResult:
    def __init__(self, test: APITest):
        self.test = test
        self.status = TestStatus.SKIPPED
        self.response: Optional[requests.Response] = None
        self.error_message: str = ""
        self.duration: float = 0.0
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        return {
            "test_name": self.test.name,
            "status": self.status,
            "response_status": self.response.status_code if self.response else None,
            "error_message": self.error_message,
            "duration": self.duration,
            "timestamp": self.timestamp
        }

class APITestRunner:
    def __init__(self):
        self.tests: Dict[str, APITest] = {}
        self.results: List[TestResult] = []
        self.config_file = Path("test_config.yaml")
        self.log_file = Path("test_execution.log")
        self.report_dir = Path("test_reports")
        self.setup_logging()
        self.load_config()
        self.report_dir.mkdir(exist_ok=True)

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def load_config(self):
        """Load test configuration from YAML file"""
        if not self.config_file.exists():
            return

        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
                for test_data in config.get("tests", []):
                    test = APITest.from_dict(test_data)
                    self.tests[test.name] = test
        except Exception as e:
            logging.error(f"Error loading config: {e}")

    def save_config(self):
        """Save test configuration to YAML file"""
        config = {
            "tests": [test.to_dict() for test in self.tests.values()]
        }
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

    def add_test(self, test: APITest) -> bool:
        """Add a new test case"""
        if test.name in self.tests:
            logging.error(f"Test {test.name} already exists")
            return False

        self.tests[test.name] = test
        self.save_config()
        logging.info(f"Added test: {test.name}")
        return True

    def remove_test(self, test_name: str) -> bool:
        """Remove a test case"""
        if test_name not in self.tests:
            logging.error(f"Test {test_name} not found")
            return False

        del self.tests[test_name]
        self.save_config()
        logging.info(f"Removed test: {test_name}")
        return True

    def run_test(self, test: APITest) -> TestResult:
        """Run a single test case"""
        result = TestResult(test)
        start_time = time.time()

        try:
            # Run setup scripts
            for script in test.setup_scripts:
                exec(script)

            # Make the API request
            response = requests.request(
                method=test.method,
                url=test.endpoint,
                headers=test.headers,
                params=test.params,
                json=test.body,
                timeout=test.timeout
            )
            result.response = response

            # Validate status code
            if response.status_code != test.expected_status:
                result.status = TestStatus.FAILED
                result.error_message = f"Expected status {test.expected_status}, got {response.status_code}"
                return result

            # Validate response schema
            if test.expected_schema:
                try:
                    jsonschema.validate(response.json(), test.expected_schema)
                except jsonschema.exceptions.ValidationError as e:
                    result.status = TestStatus.FAILED
                    result.error_message = f"Schema validation failed: {str(e)}"
                    return result

            # Validate response content
            response_text = response.text.lower()
            for expected_text in test.expected_contains:
                if expected_text.lower() not in response_text:
                    result.status = TestStatus.FAILED
                    result.error_message = f"Response does not contain: {expected_text}"
                    return result

            result.status = TestStatus.PASSED

        except Exception as e:
            result.status = TestStatus.ERROR
            result.error_message = str(e)

        finally:
            # Run cleanup scripts
            for script in test.cleanup_scripts:
                try:
                    exec(script)
                except Exception as e:
                    logging.error(f"Cleanup script error: {e}")

            result.duration = time.time() - start_time

        return result

    def run_all_tests(self, parallel: bool = False) -> List[TestResult]:
        """Run all test cases"""
        self.results = []
        tests_to_run = list(self.tests.values())

        if parallel:
            with ThreadPoolExecutor() as executor:
                self.results = list(executor.map(self.run_test, tests_to_run))
        else:
            for test in tests_to_run:
                self.results.append(self.run_test(test))

        self.generate_report()
        return self.results

    def generate_report(self):
        """Generate test execution report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate HTML report
        html_report = self.report_dir / f"test_report_{timestamp}.html"
        self._generate_html_report(html_report)
        
        # Generate CSV report
        csv_report = self.report_dir / f"test_report_{timestamp}.csv"
        self._generate_csv_report(csv_report)
        
        logging.info(f"Reports generated: {html_report}, {csv_report}")

    def _generate_html_report(self, output_path: Path):
        """Generate HTML test report"""
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>API Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .PASSED { color: green; }
                .FAILED { color: red; }
                .ERROR { color: orange; }
                .SKIPPED { color: gray; }
            </style>
        </head>
        <body>
            <h1>API Test Report</h1>
            <h3>Generated: {{ timestamp }}</h3>
            
            <h2>Summary</h2>
            <p>Total Tests: {{ total_tests }}</p>
            <p>Passed: {{ passed_tests }}</p>
            <p>Failed: {{ failed_tests }}</p>
            <p>Errors: {{ error_tests }}</p>
            <p>Skipped: {{ skipped_tests }}</p>
            
            <h2>Test Results</h2>
            <table>
                <tr>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Duration (s)</th>
                    <th>Error Message</th>
                </tr>
                {% for result in results %}
                <tr>
                    <td>{{ result.test.name }}</td>
                    <td class="{{ result.status }}">{{ result.status }}</td>
                    <td>{{ "%.2f"|format(result.duration) }}</td>
                    <td>{{ result.error_message }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """

        template = Template(template_str)
        
        context = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r.status == TestStatus.PASSED),
            "failed_tests": sum(1 for r in self.results if r.status == TestStatus.FAILED),
            "error_tests": sum(1 for r in self.results if r.status == TestStatus.ERROR),
            "skipped_tests": sum(1 for r in self.results if r.status == TestStatus.SKIPPED),
            "results": self.results
        }

        with open(output_path, 'w') as f:
            f.write(template.render(context))

    def _generate_csv_report(self, output_path: Path):
        """Generate CSV test report"""
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Test Name', 'Status', 'Duration', 'Error Message', 'Timestamp'])
            for result in self.results:
                writer.writerow([
                    result.test.name,
                    result.status,
                    f"{result.duration:.2f}",
                    result.error_message,
                    result.timestamp
                ])

def main():
    runner = APITestRunner()
    
    while True:
        print("\nAPI Testing Framework")
        print("1. Add Test")
        print("2. Remove Test")
        print("3. List Tests")
        print("4. Run Single Test")
        print("5. Run All Tests")
        print("6. View Test Results")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == "1":
            name = input("Enter test name: ")
            endpoint = input("Enter API endpoint: ")
            method = input("Enter HTTP method (GET/POST/PUT/DELETE): ")
            
            test = APITest(name, endpoint, method)
            
            # Optional parameters
            if input("Add headers? (y/n): ").lower() == 'y':
                headers = {}
                while True:
                    key = input("Enter header key (or press Enter to finish): ")
                    if not key:
                        break
                    value = input("Enter header value: ")
                    headers[key] = value
                test.headers = headers
            
            if input("Add request body? (y/n): ").lower() == 'y':
                try:
                    body = input("Enter JSON body: ")
                    test.body = json.loads(body)
                except json.JSONDecodeError:
                    print("Invalid JSON format!")
                    continue
            
            test.expected_status = int(input("Enter expected status code (default 200): ") or "200")
            
            if runner.add_test(test):
                print("Test added successfully!")
            else:
                print("Failed to add test!")
        
        elif choice == "2":
            name = input("Enter test name to remove: ")
            if runner.remove_test(name):
                print("Test removed successfully!")
            else:
                print("Failed to remove test!")
        
        elif choice == "3":
            if not runner.tests:
                print("No tests found!")
                continue
                
            print("\nAvailable Tests:")
            for name, test in runner.tests.items():
                print(f"\nName: {name}")
                print(f"Endpoint: {test.endpoint}")
                print(f"Method: {test.method}")
                print(f"Expected Status: {test.expected_status}")
                if test.headers:
                    print("Headers:", test.headers)
                if test.body:
                    print("Body:", test.body)
        
        elif choice == "4":
            name = input("Enter test name: ")
            if name not in runner.tests:
                print("Test not found!")
                continue
            
            result = runner.run_test(runner.tests[name])
            print(f"\nTest Status: {result.status}")
            print(f"Duration: {result.duration:.2f} seconds")
            if result.error_message:
                print(f"Error: {result.error_message}")
        
        elif choice == "5":
            parallel = input("Run tests in parallel? (y/n): ").lower() == 'y'
            results = runner.run_all_tests(parallel)
            
            print("\nTest Results:")
            for result in results:
                print(f"\nTest: {result.test.name}")
                print(f"Status: {result.status}")
                print(f"Duration: {result.duration:.2f} seconds")
                if result.error_message:
                    print(f"Error: {result.error_message}")
        
        elif choice == "6":
            if not runner.results:
                print("No test results available!")
                continue
            
            print("\nTest Results Summary:")
            total = len(runner.results)
            passed = sum(1 for r in runner.results if r.status == TestStatus.PASSED)
            failed = sum(1 for r in runner.results if r.status == TestStatus.FAILED)
            errors = sum(1 for r in runner.results if r.status == TestStatus.ERROR)
            skipped = sum(1 for r in runner.results if r.status == TestStatus.SKIPPED)
            
            print(f"Total Tests: {total}")
            print(f"Passed: {passed}")
            print(f"Failed: {failed}")
            print(f"Errors: {errors}")
            print(f"Skipped: {skipped}")
            
            print("\nDetailed Results:")
            for result in runner.results:
                print(f"\nTest: {result.test.name}")
                print(f"Status: {result.status}")
                print(f"Duration: {result.duration:.2f} seconds")
                if result.error_message:
                    print(f"Error: {result.error_message}")
        
        elif choice == "7":
            print("Thank you for using API Testing Framework!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 