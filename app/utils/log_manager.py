import os
import json
import gzip
import shutil
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import re
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional
from config import Config

class LogManager:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.setup_log_directories()
        self.setup_log_handlers()

    def setup_log_directories(self):
        """Create necessary log directories if they don't exist."""
        directories = [
            Config.LOG_DIR,
            os.path.join(Config.LOG_DIR, 'archived'),
            os.path.join(Config.LOG_DIR, 'analysis')
        ]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def setup_log_handlers(self):
        """Set up handlers for different types of logs."""
        handlers = {
            'general': self._create_handler(Config.LOG_PATH, Config.LOG_FORMAT),
            'error': self._create_handler(Config.ERROR_LOG_PATH, Config.LOG_FORMAT, level=logging.ERROR),
            'security': self._create_handler(Config.SECURITY_LOG_PATH, Config.SECURITY_LOG_FORMAT),
            'performance': self._create_handler(Config.PERFORMANCE_LOG_PATH, Config.PERFORMANCE_LOG_FORMAT)
        }
        
        for name, handler in handlers.items():
            self.app.logger.addHandler(handler)

    def _create_handler(self, filename: str, format_str: str, level=logging.INFO) -> RotatingFileHandler:
        """Create a rotating file handler with the specified configuration."""
        handler = RotatingFileHandler(
            filename,
            maxBytes=Config.LOG_MAX_BYTES,
            backupCount=Config.LOG_BACKUP_COUNT
        )
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(format_str, Config.LOG_DATE_FORMAT))
        return handler

    def archive_old_logs(self, days: int = 30):
        """Archive logs older than specified days."""
        archive_dir = os.path.join(Config.LOG_DIR, 'archived')
        current_time = datetime.now()
        
        for log_file in os.listdir(Config.LOG_DIR):
            if not log_file.endswith('.log'):
                continue
                
            log_path = os.path.join(Config.LOG_DIR, log_file)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(log_path))
            
            if current_time - file_mtime > timedelta(days=days):
                archive_name = f"{log_file}_{file_mtime.strftime('%Y%m%d')}.gz"
                archive_path = os.path.join(archive_dir, archive_name)
                
                with open(log_path, 'rb') as f_in:
                    with gzip.open(archive_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Clear the original log file
                open(log_path, 'w').close()

    def analyze_logs(self, log_file: str, start_date: Optional[datetime] = None, 
                    end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze logs within the specified date range."""
        log_path = os.path.join(Config.LOG_DIR, log_file)
        if not os.path.exists(log_path):
            return {}

        analysis = {
            'error_count': 0,
            'warning_count': 0,
            'user_activity': defaultdict(int),
            'ip_addresses': Counter(),
            'endpoints': Counter(),
            'error_types': Counter(),
            'hourly_activity': defaultdict(int)
        }

        date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
        
        with open(log_path, 'r') as f:
            for line in f:
                # Parse log date
                date_match = date_pattern.search(line)
                if not date_match:
                    continue
                    
                log_date = datetime.strptime(date_match.group(1), '%Y-%m-%d %H:%M:%S')
                
                # Check if log is within date range
                if start_date and log_date < start_date:
                    continue
                if end_date and log_date > end_date:
                    continue

                # Update analysis
                if 'ERROR' in line:
                    analysis['error_count'] += 1
                elif 'WARNING' in line:
                    analysis['warning_count'] += 1

                # Extract user ID if present
                user_match = re.search(r'user_id=(\d+)', line)
                if user_match:
                    analysis['user_activity'][user_match.group(1)] += 1

                # Extract IP address if present
                ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if ip_match:
                    analysis['ip_addresses'][ip_match.group(1)] += 1

                # Extract endpoint if present
                endpoint_match = re.search(r'(GET|POST|PUT|DELETE) (/[^\s]*)', line)
                if endpoint_match:
                    analysis['endpoints'][endpoint_match.group(2)] += 1

                # Update hourly activity
                hour = log_date.strftime('%H:00')
                analysis['hourly_activity'][hour] += 1

        return analysis

    def get_recent_errors(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get errors from the last specified hours."""
        errors = []
        start_time = datetime.now() - timedelta(hours=hours)
        
        with open(Config.ERROR_LOG_PATH, 'r') as f:
            for line in f:
                try:
                    timestamp_str = line[:19]  # Extract timestamp
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    if timestamp >= start_time:
                        errors.append({
                            'timestamp': timestamp_str,
                            'message': line[20:].strip(),
                            'level': 'ERROR'
                        })
                except Exception:
                    continue
                    
        return errors

    def get_security_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get security-related events from the last specified days."""
        events = []
        start_time = datetime.now() - timedelta(days=days)
        
        with open(Config.SECURITY_LOG_PATH, 'r') as f:
            for line in f:
                try:
                    timestamp_str = line[:19]
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    if timestamp >= start_time:
                        events.append({
                            'timestamp': timestamp_str,
                            'event': line[20:].strip()
                        })
                except Exception:
                    continue
                    
        return events

    def export_analysis(self, analysis: Dict[str, Any], filename: str):
        """Export log analysis to a JSON file."""
        export_path = os.path.join(Config.LOG_DIR, 'analysis', filename)
        
        # Convert defaultdict and Counter objects to regular dictionaries
        serializable_analysis = {}
        for key, value in analysis.items():
            if isinstance(value, (Counter, defaultdict)):
                serializable_analysis[key] = dict(value)
            else:
                serializable_analysis[key] = value
        
        with open(export_path, 'w') as f:
            json.dump(serializable_analysis, f, indent=2)

    def cleanup_old_archives(self, months: int = 6):
        """Remove archived logs older than specified months."""
        archive_dir = os.path.join(Config.LOG_DIR, 'archived')
        current_time = datetime.now()
        
        for archived_file in os.listdir(archive_dir):
            if not archived_file.endswith('.gz'):
                continue
                
            file_path = os.path.join(archive_dir, archived_file)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if current_time - file_mtime > timedelta(days=30*months):
                os.remove(file_path)

    def generate_daily_report(self):
        """Generate a daily summary report of log activities."""
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        # Analyze different log files
        general_analysis = self.analyze_logs('stewardwell.log', start_date, end_date)
        error_analysis = self.analyze_logs('error.log', start_date, end_date)
        security_analysis = self.analyze_logs('security.log', start_date, end_date)
        
        report = {
            'date': yesterday.strftime('%Y-%m-%d'),
            'general': general_analysis,
            'errors': error_analysis,
            'security': security_analysis,
            'summary': {
                'total_errors': error_analysis.get('error_count', 0),
                'total_warnings': general_analysis.get('warning_count', 0),
                'active_users': len(general_analysis.get('user_activity', {})),
                'unique_ips': len(general_analysis.get('ip_addresses', {}))
            }
        }
        
        # Export report
        report_filename = f"daily_report_{yesterday.strftime('%Y%m%d')}.json"
        self.export_analysis(report, report_filename)
        return report
