import unittest
import os
import json
import shutil
from datetime import datetime, timedelta
from app import create_app
from app.utils.logger import ActivityLogger
from app.utils.log_manager import LogManager
from config import TestingConfig

class TestLogging(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create test log directory
        self.test_log_dir = 'test_logs'
        if not os.path.exists(self.test_log_dir):
            os.makedirs(self.test_log_dir)
        
        # Initialize logger and log manager
        self.activity_logger = ActivityLogger('test_module')
        self.log_manager = LogManager(self.app)

    def tearDown(self):
        # Clean up test logs
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        self.app_context.pop()

    def test_activity_logging(self):
        """Test basic activity logging"""
        test_user_id = 1
        test_action = 'test_action'
        test_details = {'key': 'value'}
        
        self.activity_logger.log_activity(test_user_id, test_action, test_details)
        
        # Verify log file exists and contains the logged activity
        log_path = os.path.join(TestingConfig.LOG_DIR, TestingConfig.LOG_FILENAME)
        self.assertTrue(os.path.exists(log_path))
        
        with open(log_path, 'r') as f:
            log_content = f.read()
            self.assertIn(str(test_user_id), log_content)
            self.assertIn(test_action, log_content)
            self.assertIn('value', log_content)

    def test_error_logging(self):
        """Test error logging functionality"""
        test_user_id = 1
        test_error = 'test_error'
        test_details = {'error_key': 'error_value'}
        
        self.activity_logger.log_error(test_user_id, test_error, test_details)
        
        # Verify error log file exists and contains the error
        error_log_path = os.path.join(TestingConfig.LOG_DIR, TestingConfig.ERROR_LOG_FILENAME)
        self.assertTrue(os.path.exists(error_log_path))
        
        with open(error_log_path, 'r') as f:
            log_content = f.read()
            self.assertIn(str(test_user_id), log_content)
            self.assertIn(test_error, log_content)
            self.assertIn('error_value', log_content)

    def test_log_rotation(self):
        """Test log rotation functionality"""
        # Create a large log file
        log_path = os.path.join(self.test_log_dir, 'test.log')
        large_content = 'x' * (TestingConfig.LOG_MAX_BYTES + 1000)
        
        with open(log_path, 'w') as f:
            f.write(large_content)
        
        # Trigger rotation
        self.log_manager.archive_old_logs(days=0)
        
        # Verify rotation occurred
        self.assertTrue(os.path.exists(log_path + '.1'))

    def test_log_analysis(self):
        """Test log analysis functionality"""
        # Create test logs
        log_path = os.path.join(self.test_log_dir, 'analysis_test.log')
        test_logs = [
            '2024-01-01 10:00:00 INFO user_id=1 action=login\n',
            '2024-01-01 10:01:00 ERROR user_id=1 error=test_error\n',
            '2024-01-01 10:02:00 WARNING user_id=2 warning=test_warning\n'
        ]
        
        with open(log_path, 'w') as f:
            f.writelines(test_logs)
        
        # Analyze logs
        analysis = self.log_manager.analyze_logs('analysis_test.log')
        
        # Verify analysis results
        self.assertEqual(analysis['error_count'], 1)
        self.assertEqual(analysis['warning_count'], 1)
        self.assertEqual(len(analysis['user_activity']), 2)

    def test_security_logging(self):
        """Test security event logging"""
        test_user_id = 1
        test_action = 'failed_login'
        test_details = {'ip': '127.0.0.1', 'reason': 'invalid_password'}
        
        self.activity_logger.log_activity(
            test_user_id,
            test_action,
            test_details,
            level='WARNING'
        )
        
        # Verify security log exists and contains the event
        security_log_path = os.path.join(TestingConfig.LOG_DIR, TestingConfig.SECURITY_LOG_FILENAME)
        self.assertTrue(os.path.exists(security_log_path))
        
        with open(security_log_path, 'r') as f:
            log_content = f.read()
            self.assertIn(str(test_user_id), log_content)
            self.assertIn(test_action, log_content)
            self.assertIn('invalid_password', log_content)

    def test_log_cleanup(self):
        """Test log cleanup functionality"""
        # Create old archive files
        archive_dir = os.path.join(self.test_log_dir, 'archived')
        os.makedirs(archive_dir)
        
        old_date = (datetime.now() - timedelta(days=200)).strftime('%Y%m%d')
        old_archive = os.path.join(archive_dir, f'test_log_{old_date}.gz')
        
        with open(old_archive, 'w') as f:
            f.write('old log content')
        
        # Run cleanup
        self.log_manager.cleanup_old_archives(months=1)
        
        # Verify old archive was removed
        self.assertFalse(os.path.exists(old_archive))

    def test_daily_report_generation(self):
        """Test daily report generation"""
        # Create test logs for the day
        log_path = os.path.join(self.test_log_dir, 'daily_test.log')
        test_logs = [
            f'{datetime.now().strftime("%Y-%m-%d")} 10:00:00 INFO user_id=1 action=login\n',
            f'{datetime.now().strftime("%Y-%m-%d")} 10:01:00 ERROR user_id=1 error=test_error\n',
            f'{datetime.now().strftime("%Y-%m-%d")} 10:02:00 WARNING user_id=2 warning=test_warning\n'
        ]
        
        with open(log_path, 'w') as f:
            f.writelines(test_logs)
        
        # Generate report
        report = self.log_manager.generate_daily_report()
        
        # Verify report contents
        self.assertIsNotNone(report)
        self.assertIn('summary', report)
        self.assertIn('total_errors', report['summary'])
        self.assertIn('active_users', report['summary'])

    def test_log_search(self):
        """Test log searching functionality"""
        # Create test logs with searchable content
        log_path = os.path.join(self.test_log_dir, 'search_test.log')
        test_logs = [
            '2024-01-01 10:00:00 INFO user_id=1 action=search_term_test\n',
            '2024-01-01 10:01:00 INFO user_id=2 action=other_action\n',
            '2024-01-01 10:02:00 INFO user_id=1 action=search_term_test\n'
        ]
        
        with open(log_path, 'w') as f:
            f.writelines(test_logs)
        
        # Search logs
        matches = []
        with open(log_path, 'r') as f:
            for line in f:
                if 'search_term_test' in line:
                    matches.append(line)
        
        # Verify search results
        self.assertEqual(len(matches), 2)
        for match in matches:
            self.assertIn('search_term_test', match)

if __name__ == '__main__':
    unittest.main()
