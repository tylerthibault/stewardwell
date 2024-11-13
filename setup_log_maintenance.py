import os
import sys
import platform
from datetime import datetime
import subprocess
import click

WINDOWS_TASK_XML = '''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>StewardWell Log Maintenance Tasks</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{start_time}</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>Password</LogonType>
      <RunLevel>Highest</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>{script_path} {command}</Arguments>
      <WorkingDirectory>{working_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
'''

CRON_TEMPLATE = '''# StewardWell Log Maintenance Tasks
0 0 * * * cd {working_dir} && {python_path} {script_path} archive-logs
0 1 * * * cd {working_dir} && {python_path} {script_path} generate-report
0 2 * * 0 cd {working_dir} && {python_path} {script_path} cleanup
'''

def is_windows():
    return platform.system().lower() == 'windows'

def setup_windows_task(task_name, command, start_time):
    """Set up a Windows Scheduled Task"""
    python_path = sys.executable
    script_path = os.path.join(os.getcwd(), 'manage_logs.py')
    working_dir = os.getcwd()
    
    # Create task XML
    xml_content = WINDOWS_TASK_XML.format(
        start_time=start_time.strftime('%Y-%m-%dT%H:%M:%S'),
        python_path=python_path,
        script_path=script_path,
        working_dir=working_dir,
        command=command
    )
    
    # Save XML to temporary file
    xml_path = os.path.join(working_dir, f'{task_name}.xml')
    with open(xml_path, 'w') as f:
        f.write(xml_content)
    
    # Create task using schtasks
    try:
        subprocess.run([
            'schtasks', '/create', '/tn', f'StewardWell\\{task_name}',
            '/xml', xml_path, '/f'
        ], check=True)
        click.echo(f"Successfully created task: {task_name}")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error creating task {task_name}: {e}")
    finally:
        os.remove(xml_path)

def setup_cron_jobs():
    """Set up cron jobs for log maintenance"""
    python_path = sys.executable
    script_path = os.path.join(os.getcwd(), 'manage_logs.py')
    working_dir = os.getcwd()
    
    cron_content = CRON_TEMPLATE.format(
        working_dir=working_dir,
        python_path=python_path,
        script_path=script_path
    )
    
    # Write to temporary file
    temp_cron = '/tmp/stewardwell_cron'
    with open(temp_cron, 'w') as f:
        f.write(cron_content)
    
    # Install cron jobs
    try:
        subprocess.run(['crontab', temp_cron], check=True)
        click.echo("Successfully installed cron jobs")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error installing cron jobs: {e}")
    finally:
        os.remove(temp_cron)

@click.command()
def setup():
    """Set up automated log maintenance tasks"""
    if is_windows():
        click.echo("Setting up Windows Scheduled Tasks...")
        
        # Set up daily log archiving
        setup_windows_task(
            'LogArchive',
            'archive-logs',
            datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        )
        
        # Set up daily report generation
        setup_windows_task(
            'DailyReport',
            'generate-report',
            datetime.now().replace(hour=1, minute=0, second=0, microsecond=0)
        )
        
        # Set up weekly cleanup
        setup_windows_task(
            'LogCleanup',
            'cleanup',
            datetime.now().replace(hour=2, minute=0, second=0, microsecond=0)
        )
        
        click.echo("\nTasks have been created. You can view them in Task Scheduler under the StewardWell folder.")
    else:
        click.echo("Setting up cron jobs...")
        setup_cron_jobs()
        click.echo("\nCron jobs have been installed. You can view them with 'crontab -l'")
    
    click.echo("\nLog maintenance tasks have been scheduled:")
    click.echo("1. Daily log archiving (midnight)")
    click.echo("2. Daily report generation (1 AM)")
    click.echo("3. Weekly cleanup (2 AM on Sundays)")

if __name__ == '__main__':
    setup()
