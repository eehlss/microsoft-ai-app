import pandas as pd
import plotly
import json
from datetime import datetime
import io

def export_to_csv(parameters, assessment, pathologist_notes=None):
    """Export analysis results to CSV format"""
    try:
        # Create a DataFrame with the parameters
        df = pd.DataFrame([parameters])
        
        # Add assessment and notes if available
        if assessment:
            df['system_assessment'] = assessment.get('system_assessment', '')
        if pathologist_notes:
            df['pathologist_notes'] = pathologist_notes
            
        # Add timestamp
        df['analysis_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()
    except Exception as e:
        raise Exception(f"Error exporting to CSV: {str(e)}")

def export_to_json(parameters, assessment, charts=None, pathologist_notes=None):
    """Export analysis results to JSON format"""
    try:
        export_data = {
            'parameters': parameters,
            'assessment': assessment,
            'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if pathologist_notes:
            export_data['pathologist_notes'] = pathologist_notes
            
        if charts:
            export_data['charts'] = {
                name: plotly.io.to_json(fig) for name, fig in charts.items()
            }
            
        return json.dumps(export_data, indent=2)
    except Exception as e:
        raise Exception(f"Error exporting to JSON: {str(e)}")

def get_html_template():
    """Return HTML template for report"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hemoglobinopathy Analysis Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { text-align: center; margin-bottom: 30px; }
            .section { margin-bottom: 20px; }
            .parameter-table { width: 100%; border-collapse: collapse; }
            .parameter-table th, .parameter-table td { 
                border: 1px solid #ddd; 
                padding: 8px; 
                text-align: left; 
            }
            .parameter-table th { background-color: #f5f5f5; }
            .chart-container { margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Hemoglobinopathy Analysis Report</h1>
            <p>{date}</p>
        </div>
        {content}
    </body>
    </html>
    """

def export_to_html(parameters, assessment, charts=None, pathologist_notes=None):
    """Export analysis results to HTML format"""
    try:
        # Create parameters table HTML
        params_html = "<div class='section'><h2>Blood Test Parameters</h2>"
        params_html += "<table class='parameter-table'><tr><th>Parameter</th><th>Value</th></tr>"
        for param, value in parameters.items():
            params_html += f"<tr><td>{param}</td><td>{value}</td></tr>"
        params_html += "</table></div>"
        
        # Add assessment
        assessment_html = "<div class='section'><h2>System Assessment</h2>"
        assessment_html += f"<p>{assessment.get('system_assessment', '')}</p></div>"
        
        # Add pathologist notes if available
        notes_html = ""
        if pathologist_notes:
            notes_html = "<div class='section'><h2>Pathologist Notes</h2>"
            notes_html += f"<p>{pathologist_notes}</p></div>"
        
        # Add charts if available
        charts_html = ""
        if charts:
            charts_html = "<div class='section'><h2>Visualizations</h2>"
            for name, fig in charts.items():
                charts_html += f"<div class='chart-container'>{plotly.io.to_html(fig)}</div>"
            charts_html += "</div>"
        
        # Combine all sections
        content = params_html + assessment_html + notes_html + charts_html
        
        # Insert into template
        template = get_html_template()
        html_report = template.format(
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            content=content
        )
        
        return html_report
    except Exception as e:
        raise Exception(f"Error exporting to HTML: {str(e)}")
