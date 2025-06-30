"""
Reporting Agent for Multi-Market Correlation Engine

This agent handles automated report generation, alerts, and notifications.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

from .base_agent import BaseAgent, Task, TaskPriority, AgentStatus


class ReportingAgent(BaseAgent):
    """
    Agent responsible for generating reports and sending notifications.
    
    Features:
    - Automated report generation
    - Email notifications
    - Alert management
    - Performance dashboards
    - Export capabilities
    """
    
    def __init__(self, agent_id: str = "reporting-agent-001", 
                 name: str = "Reporting Agent", 
                 config: Optional[Dict] = None):
        """
        Initialize the reporting agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            config: Configuration dictionary
        """
        default_config = {
            'enable_email_reports': False,  # Disabled by default
            'email_config': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'use_tls': True
            },
            'report_recipients': [],
            'report_frequency': 'daily',  # daily, weekly, monthly
            'alert_thresholds': {
                'high_correlation': 0.8,
                'high_volatility': 0.1,
                'system_error': True
            },
            'report_formats': ['html', 'pdf'],
            'report_directory': 'data/reports',
            'enable_slack_notifications': False,
            'slack_webhook_url': ''
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(agent_id, name, default_config)
        
        # Reporting state
        self.report_history = []
        self.alert_history = []
        self.notification_queue = []
        
        # Create report directory
        os.makedirs(self.config['report_directory'], exist_ok=True)
        
        self.logger.info("Reporting Agent initialized")
    
    def execute_task(self, task: Task) -> Any:
        """Execute a reporting task"""
        task_type = task.data.get('type', 'unknown')
        
        try:
            if task_type == 'generate_report':
                return self._generate_report(task.data)
            elif task_type == 'send_alert':
                return self._send_alert(task.data)
            elif task_type == 'send_notification':
                return self._send_notification(task.data)
            elif task_type == 'export_data':
                return self._export_data(task.data)
            elif task_type == 'cleanup_reports':
                return self._cleanup_old_reports(task.data)
            elif task_type == 'system_status_report':
                return self._generate_system_status_report(task.data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Reporting task execution failed: {e}")
            raise
    
    def _generate_report(self, task_data: Dict) -> Dict[str, Any]:
        """Generate a comprehensive report"""
        report_type = task_data.get('report_type', 'daily_summary')
        symbols = task_data.get('symbols', ['AAPL', 'MSFT', 'GOOGL'])
        include_charts = task_data.get('include_charts', True)
        
        self.logger.info(f"Generating {report_type} report for {len(symbols)} symbols")
        
        try:
            # Get analysis results from analysis agent
            analysis_data = self._get_analysis_data(symbols)
            
            # Generate report content
            report_content = self._create_report_content(
                report_type, symbols, analysis_data, include_charts
            )
            
            # Save report
            report_filename = self._save_report(report_type, report_content)
            
            # Send report if configured
            if self.config['enable_email_reports'] and self.config['report_recipients']:
                self._email_report(report_filename, report_type)
            
            report_info = {
                'report_type': report_type,
                'symbols': symbols,
                'generated_at': datetime.now().isoformat(),
                'filename': report_filename,
                'size_kb': os.path.getsize(report_filename) / 1024 if os.path.exists(report_filename) else 0
            }
            
            # Store in history
            self.report_history.append(report_info)
            
            return report_info
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise
    
    def _get_analysis_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get analysis data from other agents"""
        from .base_agent import agent_registry
        
        # Try to get analysis agent
        analysis_agent = agent_registry.get_agent('analysis-agent-001')
        data_agent = agent_registry.get_agent('data-collector-001')
        
        analysis_data = {
            'correlations': {},
            'volatility': {},
            'network_metrics': {},
            'alerts': [],
            'data_quality': {}
        }
        
        if analysis_agent:
            # Get latest analysis results
            analysis_status = analysis_agent.get_analysis_status()
            if hasattr(analysis_agent, 'analysis_results'):
                analysis_data.update(analysis_agent.analysis_results)
            
            # Get alerts
            if hasattr(analysis_agent, 'alerts'):
                analysis_data['alerts'] = analysis_agent.alerts[-20:]  # Last 20 alerts
        
        if data_agent:
            # Get data collection status
            collection_status = data_agent.get_collection_status()
            analysis_data['data_quality'] = collection_status.get('quality_scores', {})
        
        return analysis_data
    
    def _create_report_content(self, report_type: str, symbols: List[str], 
                             analysis_data: Dict[str, Any], include_charts: bool) -> str:
        """Create HTML report content"""
        
        # Start HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Multi-Market Correlation Engine - {report_type.replace('_', ' ').title()}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #2E86C1; color: white; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }}
                .alert {{ background-color: #f8d7da; color: #721c24; padding: 10px; margin: 5px 0; border-radius: 5px; }}
                .success {{ background-color: #d4edda; color: #155724; padding: 10px; margin: 5px 0; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .chart {{ text-align: center; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Multi-Market Correlation Engine</h1>
                <h2>{report_type.replace('_', ' ').title()}</h2>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        """
        
        # Executive Summary
        html_content += self._create_executive_summary(symbols, analysis_data)
        
        # Market Overview
        html_content += self._create_market_overview(symbols, analysis_data)
        
        # Correlation Analysis
        html_content += self._create_correlation_section(analysis_data)
        
        # Volatility Analysis
        html_content += self._create_volatility_section(analysis_data)
        
        # Alerts and Notifications
        html_content += self._create_alerts_section(analysis_data)
        
        # System Health
        html_content += self._create_system_health_section()
        
        # Charts (if enabled)
        if include_charts:
            html_content += self._create_charts_section(symbols, analysis_data)
        
        # Footer
        html_content += """
            <div class="section">
                <h3>Report Information</h3>
                <p><strong>Generated by:</strong> Multi-Market Correlation Engine Reporting Agent</p>
                <p><strong>Report ID:</strong> """ + f"RPT_{int(time.time())}" + """</p>
                <p><strong>Data Sources:</strong> Yahoo Finance</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _create_executive_summary(self, symbols: List[str], analysis_data: Dict[str, Any]) -> str:
        """Create executive summary section"""
        correlation_data = analysis_data.get('correlation', {})
        volatility_data = analysis_data.get('volatility', {})
        alerts = analysis_data.get('alerts', [])
        
        # Calculate summary metrics
        total_pairs = len(symbols) * (len(symbols) - 1) // 2
        significant_pairs = len(correlation_data.get('significant_pairs', []))
        high_vol_assets = len([
            s for s, data in volatility_data.get('volatility_analysis', {}).items()
            if data.get('current_volatility', 0) > 0.05
        ])
        recent_alerts = len([a for a in alerts if 
                           datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(days=1)])
        
        return f"""
        <div class="section">
            <h3>Executive Summary</h3>
            <div class="metric">
                <strong>Assets Analyzed:</strong> {len(symbols)}
            </div>
            <div class="metric">
                <strong>Correlation Pairs:</strong> {significant_pairs}/{total_pairs}
            </div>
            <div class="metric">
                <strong>High Volatility Assets:</strong> {high_vol_assets}
            </div>
            <div class="metric">
                <strong>Recent Alerts:</strong> {recent_alerts}
            </div>
        </div>
        """
    
    def _create_market_overview(self, symbols: List[str], analysis_data: Dict[str, Any]) -> str:
        """Create market overview section"""
        data_quality = analysis_data.get('data_quality', {})
        
        html = """
        <div class="section">
            <h3>Market Overview</h3>
            <table>
                <tr><th>Symbol</th><th>Data Quality</th><th>Status</th></tr>
        """
        
        for symbol in symbols:
            quality = data_quality.get(symbol, 0)
            status = "Good" if quality > 0.8 else "Fair" if quality > 0.5 else "Poor"
            html += f"""
                <tr>
                    <td>{symbol}</td>
                    <td>{quality:.2f}</td>
                    <td>{status}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
        
        return html
    
    def _create_correlation_section(self, analysis_data: Dict[str, Any]) -> str:
        """Create correlation analysis section"""
        correlation_data = analysis_data.get('correlation', {})
        significant_pairs = correlation_data.get('significant_pairs', [])
        
        html = """
        <div class="section">
            <h3>Correlation Analysis</h3>
        """
        
        if significant_pairs:
            html += """
            <h4>Significant Correlations</h4>
            <table>
                <tr><th>Asset Pair</th><th>Correlation</th><th>Strength</th></tr>
            """
            
            for pair in significant_pairs[:10]:  # Top 10
                html += f"""
                <tr>
                    <td>{pair['pair']}</td>
                    <td>{pair['correlation']:.3f}</td>
                    <td>{pair['strength']}</td>
                </tr>
                """
            
            html += "</table>"
        else:
            html += "<p>No significant correlations detected.</p>"
        
        html += "</div>"
        return html
    
    def _create_volatility_section(self, analysis_data: Dict[str, Any]) -> str:
        """Create volatility analysis section"""
        volatility_data = analysis_data.get('volatility', {})
        vol_analysis = volatility_data.get('volatility_analysis', {})
        
        html = """
        <div class="section">
            <h3>Volatility Analysis</h3>
        """
        
        if vol_analysis:
            html += """
            <table>
                <tr><th>Symbol</th><th>Current Volatility</th><th>Forecast</th></tr>
            """
            
            for symbol, data in vol_analysis.items():
                current_vol = data.get('current_volatility', 0)
                forecasts = data.get('forecasts', [])
                next_forecast = forecasts[0] if forecasts else 0
                
                html += f"""
                <tr>
                    <td>{symbol}</td>
                    <td>{current_vol:.3f}</td>
                    <td>{next_forecast:.3f}</td>
                </tr>
                """
            
            html += "</table>"
        else:
            html += "<p>No volatility analysis data available.</p>"
        
        html += "</div>"
        return html
    
    def _create_alerts_section(self, analysis_data: Dict[str, Any]) -> str:
        """Create alerts section"""
        alerts = analysis_data.get('alerts', [])
        recent_alerts = [a for a in alerts if 
                        datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(days=7)]
        
        html = """
        <div class="section">
            <h3>Recent Alerts (Last 7 Days)</h3>
        """
        
        if recent_alerts:
            for alert in recent_alerts[-10:]:  # Last 10 alerts
                severity_class = "alert" if alert.get('severity') in ['high', 'critical'] else "success"
                html += f"""
                <div class="{severity_class}">
                    <strong>{alert.get('type', 'Unknown').replace('_', ' ').title()}:</strong>
                    {alert.get('message', 'No message')}
                    <br><small>{alert.get('timestamp', '')}</small>
                </div>
                """
        else:
            html += '<div class="success">No recent alerts - system operating normally.</div>'
        
        html += "</div>"
        return html
    
    def _create_system_health_section(self) -> str:
        """Create system health section"""
        from .base_agent import agent_registry
        
        health_status = agent_registry.health_check_all()
        
        html = """
        <div class="section">
            <h3>System Health</h3>
            <table>
                <tr><th>Agent</th><th>Status</th><th>Last Activity</th></tr>
        """
        
        for agent_id, health in health_status.items():
            status = "Healthy" if health.get('healthy', False) else "Unhealthy"
            last_activity = health.get('last_activity', 'Unknown')
            
            html += f"""
            <tr>
                <td>{agent_id}</td>
                <td>{status}</td>
                <td>{last_activity}</td>
            </tr>
            """
        
        html += """
            </table>
        </div>
        """
        
        return html
    
    def _create_charts_section(self, symbols: List[str], analysis_data: Dict[str, Any]) -> str:
        """Create charts section"""
        html = """
        <div class="section">
            <h3>Charts and Visualizations</h3>
        """
        
        # Create a simple correlation heatmap
        try:
            correlation_matrix = analysis_data.get('correlation', {}).get('correlation_matrix', {})
            
            if correlation_matrix:
                # Create a simple text-based representation
                html += """
                <div class="chart">
                    <h4>Correlation Matrix</h4>
                    <p><em>Note: Interactive charts available in the advanced dashboard</em></p>
                </div>
                """
            else:
                html += "<p>No chart data available.</p>"
        
        except Exception as e:
            html += f"<p>Error generating charts: {e}</p>"
        
        html += "</div>"
        return html
    
    def _save_report(self, report_type: str, content: str) -> str:
        """Save report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(
            self.config['report_directory'],
            f"{report_type}_{timestamp}.html"
        )
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Report saved: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
            raise
    
    def _email_report(self, report_filename: str, report_type: str):
        """Send report via email"""
        if not self.config['enable_email_reports']:
            return
        
        email_config = self.config['email_config']
        recipients = self.config['report_recipients']
        
        if not recipients or not email_config.get('username'):
            self.logger.warning("Email configuration incomplete, skipping email")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"Market Correlation Report - {report_type.replace('_', ' ').title()}"
            
            # Email body
            body = f"""
            Dear Team,
            
            Please find attached the latest market correlation analysis report.
            
            Report Type: {report_type.replace('_', ' ').title()}
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            This is an automated report from the Multi-Market Correlation Engine.
            
            Best regards,
            Correlation Engine Reporting System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach report file
            with open(report_filename, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(report_filename)}'
                )
                msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            if email_config.get('use_tls', True):
                server.starttls()
            
            server.login(email_config['username'], email_config['password'])
            server.sendmail(email_config['username'], recipients, msg.as_string())
            server.quit()
            
            self.logger.info(f"Report emailed to {len(recipients)} recipients")
            
        except Exception as e:
            self.logger.error(f"Failed to send email report: {e}")
    
    def _send_alert(self, task_data: Dict) -> Dict[str, Any]:
        """Send an alert notification"""
        alert_type = task_data.get('alert_type', 'general')
        message = task_data.get('message', 'Alert notification')
        severity = task_data.get('severity', 'medium')
        
        alert_info = {
            'alert_id': f"ALT_{int(time.time())}",
            'alert_type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store alert
        self.alert_history.append(alert_info)
        
        # Send notifications based on severity
        if severity in ['high', 'critical']:
            if self.config['enable_email_reports']:
                self._send_alert_email(alert_info)
            
            if self.config['enable_slack_notifications']:
                self._send_slack_notification(alert_info)
        
        self.logger.warning(f"Alert sent: {alert_type} - {message}")
        
        return alert_info
    
    def _send_alert_email(self, alert_info: Dict[str, Any]):
        """Send alert via email"""
        # Similar to report email but for alerts
        # Implementation would be similar to _email_report
        pass
    
    def _send_slack_notification(self, alert_info: Dict[str, Any]):
        """Send notification to Slack"""
        # Implementation for Slack webhook
        pass
    
    def _send_notification(self, task_data: Dict) -> Dict[str, Any]:
        """Send a general notification"""
        notification_type = task_data.get('type', 'info')
        message = task_data.get('message', 'Notification')
        
        notification_info = {
            'notification_id': f"NOT_{int(time.time())}",
            'type': notification_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.notification_queue.append(notification_info)
        
        self.logger.info(f"Notification sent: {notification_type} - {message}")
        
        return notification_info
    
    def _export_data(self, task_data: Dict) -> Dict[str, Any]:
        """Export data in various formats"""
        export_type = task_data.get('export_type', 'csv')
        data_source = task_data.get('data_source', 'analysis_results')
        
        # Get data to export
        export_data = self._get_export_data(data_source)
        
        # Export based on format
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(
            self.config['report_directory'],
            f"export_{data_source}_{timestamp}.{export_type}"
        )
        
        if export_type == 'csv':
            # Convert to CSV
            if isinstance(export_data, dict):
                df = pd.DataFrame([export_data])
            else:
                df = pd.DataFrame(export_data)
            df.to_csv(filename, index=False)
        
        elif export_type == 'json':
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        
        return {
            'filename': filename,
            'export_type': export_type,
            'data_source': data_source,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_export_data(self, data_source: str) -> Any:
        """Get data for export"""
        if data_source == 'reports':
            return self.report_history
        elif data_source == 'alerts':
            return self.alert_history
        elif data_source == 'notifications':
            return self.notification_queue
        else:
            return {}
    
    def _cleanup_old_reports(self, task_data: Dict) -> Dict[str, Any]:
        """Clean up old report files"""
        retention_days = task_data.get('retention_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        cleaned_files = 0
        report_dir = self.config['report_directory']
        
        try:
            for filename in os.listdir(report_dir):
                filepath = os.path.join(report_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_date:
                        os.remove(filepath)
                        cleaned_files += 1
            
            self.logger.info(f"Cleaned up {cleaned_files} old report files")
            
            return {
                'cleaned_files': cleaned_files,
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup reports: {e}")
            raise
    
    def _generate_system_status_report(self, task_data: Dict) -> Dict[str, Any]:
        """Generate a system status report"""
        from .base_agent import agent_registry
        
        # Get system status from all agents
        system_status = agent_registry.get_status_all()
        health_status = agent_registry.health_check_all()
        
        report_data = {
            'report_type': 'system_status',
            'generated_at': datetime.now().isoformat(),
            'system_overview': {
                'total_agents': len(system_status),
                'healthy_agents': sum(1 for h in health_status.values() if h.get('healthy', False)),
                'total_tasks_completed': sum(s.get('metrics', {}).get('tasks_completed', 0) for s in system_status.values()),
                'total_errors': sum(s.get('metrics', {}).get('error_count', 0) for s in system_status.values())
            },
            'agent_details': system_status,
            'health_details': health_status
        }
        
        # Save as JSON report
        filename = self._save_report('system_status', json.dumps(report_data, indent=2))
        
        return {
            'filename': filename,
            'report_data': report_data
        }
    
    def get_reporting_status(self) -> Dict[str, Any]:
        """Get detailed reporting status"""
        return {
            'total_reports': len(self.report_history),
            'total_alerts': len(self.alert_history),
            'pending_notifications': len(self.notification_queue),
            'recent_reports': self.report_history[-5:],
            'recent_alerts': self.alert_history[-5:],
            'email_enabled': self.config['enable_email_reports'],
            'slack_enabled': self.config['enable_slack_notifications']
        }
    
    def force_report_generation(self, report_type: str = 'daily_summary', 
                               symbols: Optional[List[str]] = None) -> str:
        """Force immediate report generation"""
        symbols = symbols or ['AAPL', 'MSFT', 'GOOGL']
        
        task = self.create_task(
            f"Manual {report_type} Report",
            {
                'type': 'generate_report',
                'report_type': report_type,
                'symbols': symbols,
                'include_charts': True
            },
            priority=TaskPriority.HIGH
        )
        
        return task.id


if __name__ == "__main__":
    # Test the reporting agent
    agent = ReportingAgent()
    
    # Start the agent
    agent.start()
    
    # Force a report generation
    task_id = agent.force_report_generation('test_report', ['AAPL', 'MSFT'])
    print(f"Started report generation task: {task_id}")
    
    # Wait for task completion
    time.sleep(10)
    
    # Check status
    status = agent.get_reporting_status()
    print("Reporting Status:")
    print(f"Total reports: {status['total_reports']}")
    print(f"Total alerts: {status['total_alerts']}")
    
    # Stop the agent
    agent.stop()