import click
import json
from datetime import datetime, timedelta
from app import create_app
from app.utils.log_manager import LogManager
from config import Config

app = create_app()
log_manager = LogManager(app)

@click.group()
def cli():
    """StewardWell Log Management CLI"""
    pass

@cli.command()
@click.option('--days', default=30, help='Archive logs older than specified days')
def archive_logs(days):
    """Archive old log files"""
    click.echo(f"Archiving logs older than {days} days...")
    log_manager.archive_old_logs(days)
    click.echo("Log archiving completed!")

@cli.command()
@click.option('--log-file', default='stewardwell.log', help='Log file to analyze')
@click.option('--days', default=7, help='Analyze logs from the last N days')
@click.option('--output', default='log_analysis.json', help='Output file name')
def analyze(log_file, days, output):
    """Analyze logs and generate report"""
    click.echo(f"Analyzing {log_file} for the last {days} days...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    analysis = log_manager.analyze_logs(log_file, start_date, end_date)
    log_manager.export_analysis(analysis, output)
    
    click.echo(f"Analysis completed! Results saved to logs/analysis/{output}")
    
    # Display summary
    click.echo("\nSummary:")
    click.echo(f"Total Errors: {analysis.get('error_count', 0)}")
    click.echo(f"Total Warnings: {analysis.get('warning_count', 0)}")
    click.echo(f"Active Users: {len(analysis.get('user_activity', {}))}")
    click.echo(f"Unique IP Addresses: {len(analysis.get('ip_addresses', {}))}")

@cli.command()
@click.option('--hours', default=24, help='Show errors from the last N hours')
def show_errors(hours):
    """Display recent errors"""
    click.echo(f"Showing errors from the last {hours} hours:")
    errors = log_manager.get_recent_errors(hours)
    
    if not errors:
        click.echo("No errors found.")
        return
    
    for error in errors:
        click.echo(f"\n[{error['timestamp']}] {error['message']}")

@cli.command()
@click.option('--days', default=7, help='Show security events from the last N days')
def security_report(days):
    """Display security-related events"""
    click.echo(f"Showing security events from the last {days} days:")
    events = log_manager.get_security_events(days)
    
    if not events:
        click.echo("No security events found.")
        return
    
    for event in events:
        click.echo(f"\n[{event['timestamp']}] {event['event']}")

@cli.command()
def generate_report():
    """Generate daily summary report"""
    click.echo("Generating daily report...")
    report = log_manager.generate_daily_report()
    
    click.echo("\nDaily Report Summary:")
    click.echo(f"Date: {report['date']}")
    click.echo(f"Total Errors: {report['summary']['total_errors']}")
    click.echo(f"Total Warnings: {report['summary']['total_warnings']}")
    click.echo(f"Active Users: {report['summary']['active_users']}")
    click.echo(f"Unique IPs: {report['summary']['unique_ips']}")

@cli.command()
@click.option('--months', default=6, help='Remove archives older than N months')
def cleanup(months):
    """Clean up old archived logs"""
    click.echo(f"Cleaning up archives older than {months} months...")
    log_manager.cleanup_old_archives(months)
    click.echo("Cleanup completed!")

@cli.command()
def status():
    """Show logging system status"""
    click.echo("Checking logging system status...")
    
    # Check log directories
    log_dir = Config.LOG_DIR
    archive_dir = f"{log_dir}/archived"
    analysis_dir = f"{log_dir}/analysis"
    
    click.echo("\nDirectory Status:")
    click.echo(f"Log Directory: {'✓' if os.path.exists(log_dir) else '✗'}")
    click.echo(f"Archive Directory: {'✓' if os.path.exists(archive_dir) else '✗'}")
    click.echo(f"Analysis Directory: {'✓' if os.path.exists(analysis_dir) else '✗'}")
    
    # Check log files
    click.echo("\nLog Files:")
    log_files = {
        'Main Log': Config.LOG_PATH,
        'Error Log': Config.ERROR_LOG_PATH,
        'Security Log': Config.SECURITY_LOG_PATH,
        'Performance Log': Config.PERFORMANCE_LOG_PATH
    }
    
    for name, path in log_files.items():
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        click.echo(f"{name}: {'✓' if exists else '✗'} ({size/1024:.2f} KB)")

@cli.command()
@click.argument('query')
@click.option('--log-file', default='stewardwell.log', help='Log file to search')
def search(query, log_file):
    """Search logs for specific terms"""
    click.echo(f"Searching for '{query}' in {log_file}...")
    
    log_path = os.path.join(Config.LOG_DIR, log_file)
    if not os.path.exists(log_path):
        click.echo(f"Error: Log file {log_file} not found!")
        return
    
    with open(log_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if query.lower() in line.lower():
                click.echo(f"\nLine {line_num}:")
                click.echo(line.strip())

if __name__ == '__main__':
    cli()
