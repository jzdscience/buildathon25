#!/usr/bin/env python3
"""
Flask Web Application for Codebase Time Machine
"""

import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_socketio import SocketIO, emit
import sqlite3
import pandas as pd
import numpy as np
from codebase_time_machine import CodebaseTimeMachine
import tempfile
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'codebase_time_machine_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for tracking analysis state
analysis_state = {
    'status': 'idle',
    'progress': 0,
    'message': '',
    'results': None,
    'error': None
}

def make_json_serializable(obj):
    """Convert non-JSON-serializable objects to serializable formats"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, pd.Series):
        return obj.to_list()
    else:
        return obj

class WebCodebaseTimeMachine(CodebaseTimeMachine):
    """Extended version of CodebaseTimeMachine for web interface"""
    
    def __init__(self, socketio_instance=None):
        super().__init__()
        self.socketio = socketio_instance
        self.progress_callback = None
    
    def emit_progress(self, message, progress=None):
        """Emit progress updates to the web interface"""
        if self.socketio:
            data = {'message': message}
            if progress is not None:
                data['progress'] = progress
            self.socketio.emit('progress_update', data)
        print(f"Progress: {message}")
    
    def analyze_repository_web(self, repo_url=None, repo_path=None, full_analysis=False):
        """Web-friendly repository analysis with progress updates"""
        try:
            self.emit_progress("Starting analysis...", 0)
            
            # Load or clone repository
            if repo_url:
                self.emit_progress("Cloning repository...", 10)
                self.clone_repository(repo_url)
            elif repo_path:
                self.repo_path = repo_path
                import git
                self.repo = git.Repo(repo_path)
            else:
                raise ValueError("No repository URL or path provided")
            
            # Analyze commit history
            self.emit_progress("Analyzing commit history...", 30)
            commits = self.analyze_commit_history()
            
            # Extract file changes
            self.emit_progress("Extracting file changes...", 50)
            file_changes = self.extract_file_changes()
            
            # Analyze commit messages
            self.emit_progress("Analyzing commit patterns...", 70)
            commit_analysis = self.analyze_commit_messages()
            
            # Generate visualizations
            self.emit_progress("Generating visualizations...", 85)
            
            # Create unique filenames for this analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ownership_file = f"static/ownership_{timestamp}.html"
            complexity_file = f"static/complexity_{timestamp}.html"
            report_file = f"static/report_{timestamp}.html"
            
            # Ensure static directory exists
            os.makedirs("static", exist_ok=True)
            
            self.visualize_code_ownership(ownership_file)
            
            if full_analysis:
                self.emit_progress("Calculating code metrics...", 90)
                code_metrics = self.calculate_code_metrics()
                # Note: Complexity trends visualization removed
            
            self.generate_report(report_file)
            
            self.emit_progress("Analysis complete!", 100)
            
            # Prepare results and ensure they're JSON serializable
            results = {
                'repository': repo_url or repo_path,
                'timestamp': timestamp,
                'commit_count': len(commits),
                'file_changes_count': len(file_changes),
                'commit_analysis': make_json_serializable(commit_analysis),
                'ownership_chart': ownership_file,
                'complexity_chart': None,  # Complexity trends feature removed
                'report': report_file,
                'full_analysis': full_analysis
            }
            
            return results
            
        except Exception as e:
            self.emit_progress(f"Error: {str(e)}", 0)
            raise e


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/demo')
def demo():
    """Demo page with example repositories"""
    demo_repos = [
        {
            'name': 'Hello World (Simple)',
            'url': 'https://github.com/octocat/Hello-World.git',
            'description': 'A simple repository with basic commits',
            'size': 'Small'
        },
        {
            'name': 'Git Tutorial',
            'url': 'https://github.com/git/git-reference.git',
            'description': 'Git reference documentation',
            'size': 'Medium'
        },
        {
            'name': 'Python Project Example',
            'url': 'https://github.com/psf/requests.git',
            'description': 'Popular Python HTTP library',
            'size': 'Large'
        }
    ]
    return render_template('demo.html', repos=demo_repos)

@app.route('/results')
def results():
    """Results page"""
    if analysis_state['results']:
        return render_template('results.html', results=analysis_state['results'])
    else:
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint to start repository analysis"""
    global analysis_state
    
    if analysis_state['status'] == 'running':
        return jsonify({'error': 'Analysis already in progress'}), 400
    
    data = request.get_json()
    repo_url = data.get('repo_url')
    repo_path = data.get('repo_path')
    full_analysis = data.get('full_analysis', False)
    
    if not repo_url and not repo_path:
        return jsonify({'error': 'Repository URL or path is required'}), 400
    
    # Reset analysis state
    analysis_state.update({
        'status': 'running',
        'progress': 0,
        'message': 'Starting analysis...',
        'results': None,
        'error': None
    })
    
    # Start analysis in background thread
    thread = threading.Thread(
        target=run_analysis,
        args=(repo_url, repo_path, full_analysis)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Analysis started'})

@app.route('/api/query', methods=['POST'])
def api_query():
    """API endpoint for natural language queries"""
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        tm = WebCodebaseTimeMachine()
        response = tm.query_natural_language(query)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def api_status():
    """API endpoint to get current analysis status"""
    return jsonify(analysis_state)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_file(f'static/{filename}')

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print('Client connected')
    emit('status_update', analysis_state)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print('Client disconnected')

def run_analysis(repo_url, repo_path, full_analysis):
    """Run analysis in background thread"""
    global analysis_state
    
    try:
        tm = WebCodebaseTimeMachine(socketio)
        results = tm.analyze_repository_web(
            repo_url=repo_url,
            repo_path=repo_path,
            full_analysis=full_analysis
        )
        
        analysis_state.update({
            'status': 'completed',
            'progress': 100,
            'message': 'Analysis completed successfully!',
            'results': make_json_serializable(results),
            'error': None
        })
        
        socketio.emit('analysis_complete', make_json_serializable(results))
        
    except Exception as e:
        analysis_state.update({
            'status': 'error',
            'progress': 0,
            'message': f'Analysis failed: {str(e)}',
            'results': None,
            'error': str(e)
        })
        
        socketio.emit('analysis_error', {'error': str(e)})

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Get port from environment variable (for Cloud Run) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    print("Starting Codebase Time Machine Web Interface...")
    print(f"Open your browser to: http://localhost:{port}")
    
    # Use debug=False in production
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    socketio.run(app, debug=debug_mode, host='0.0.0.0', port=port)