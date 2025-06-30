#!/usr/bin/env python3
"""
Flask Dashboard API - Serve Facebook Group Scraper Dashboard data via REST API.

This Flask application provides endpoints for the dashboard frontend and handles
scraper execution requests.

Author: Facebook Group Scraper Project
Date: 2025
"""

import os
import sys
import json
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from dashboard_analytics import DashboardAnalytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask_dashboard.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Global variables for scraper status
scraper_status = {
    'status': 'idle',  # 'idle', 'running', 'completed', 'failed'
    'last_run': None,
    'duration_seconds': 0,
    'posts_scraped': 0,
    'comments_scraped': 0,
    'start_time': None
}

# Initialize analytics
analytics = DashboardAnalytics()

def run_scraper(prime_bank_posts=20, other_banks_posts=15):
    """Run the complete scraper pipeline in a separate thread."""
    global scraper_status
    
    try:
        logger.info("=" * 80)
        logger.info(f"🚀 STARTING SCRAPER PIPELINE")
        logger.info(f"Prime Bank posts: {prime_bank_posts}")
        logger.info(f"Other Banks posts: {other_banks_posts}")
        logger.info("=" * 80)
        scraper_status['status'] = 'running'
        scraper_status['start_time'] = datetime.now()
        
        # Change to backend directory
        backend_dir = Path(__file__).parent
        os.chdir(str(backend_dir))
        
        # Run the complete pipeline with post count parameters and stream output
        process = subprocess.Popen([
            sys.executable, 'complete_pipeline.py',
            '--prime-bank-posts', str(prime_bank_posts),
            '--other-banks-posts', str(other_banks_posts)
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
        
        # Stream output in real-time
        output_lines = []
        logger.info("=" * 80)
        logger.info("SCRAPER OUTPUT - REAL-TIME DEBUG:")
        logger.info("=" * 80)
        
        for line in process.stdout:
            line = line.rstrip()
            if line:  # Only print non-empty lines
                logger.info(f"[SCRAPER] {line}")
                output_lines.append(line)
        
        # Wait for process to complete
        return_code = process.wait()
        
        # Create a result object similar to subprocess.run
        class ProcessResult:
            def __init__(self, returncode, stdout):
                self.returncode = returncode
                self.stdout = stdout
        
        result = ProcessResult(return_code, '\n'.join(output_lines))
        
        end_time = datetime.now()
        duration = (end_time - scraper_status['start_time']).total_seconds()
        
        if result.returncode == 0:
            logger.info("=" * 80)
            logger.info("✅ SCRAPER PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            scraper_status['status'] = 'completed'
            scraper_status['last_run'] = end_time.isoformat()
            scraper_status['duration_seconds'] = round(duration)
            
            # Try to extract post/comment counts from output
            try:
                for line in output_lines:
                    if 'posts scraped' in line.lower():
                        # Extract number from line like "Successfully scraped 24 posts"
                        import re
                        numbers = re.findall(r'\d+', line)
                        if numbers:
                            scraper_status['posts_scraped'] = int(numbers[0])
                    elif 'comments scraped' in line.lower():
                        numbers = re.findall(r'\d+', line)
                        if numbers:
                            scraper_status['comments_scraped'] = int(numbers[0])
            except Exception as e:
                logger.warning(f"Could not extract scraper stats: {e}")
                
        else:
            logger.error("=" * 80)
            logger.error("❌ SCRAPER PIPELINE FAILED")
            logger.error(f"Return code: {result.returncode}")
            logger.error("=" * 80)
            scraper_status['status'] = 'failed'
            scraper_status['last_run'] = end_time.isoformat()
            scraper_status['duration_seconds'] = round(duration)
            
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR RUNNING SCRAPER PIPELINE: {e}")
        logger.error("=" * 80)
        scraper_status['status'] = 'failed'
        scraper_status['last_run'] = datetime.now().isoformat()
        if scraper_status['start_time']:
            duration = (datetime.now() - scraper_status['start_time']).total_seconds()
            scraper_status['duration_seconds'] = round(duration)

@app.route('/')
def index():
    """Health check endpoint."""
    return jsonify({
        'message': 'Facebook Group Scraper Dashboard API',
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/dashboard', methods=['POST'])
def get_dashboard_data():
    """
    Main dashboard endpoint.
    Endpoint: /api/dashboard
    Method: POST
    Input: {"content": "give_full_data"}
    Output: Complete dashboard JSON
    """
    try:
        request_data = request.get_json()
        if not request_data or request_data.get('content') != 'give_full_data':
            return jsonify({'error': 'Invalid request. Expected {"content": "give_full_data"}'}), 400
        
        logger.info("Generating dashboard data...")
        
        # Get complete dashboard data
        dashboard_data = analytics.get_complete_dashboard_data()
        
        # Update scraping status
        dashboard_data['scraping_status'] = scraper_status.copy()
        # Remove internal fields
        if 'start_time' in dashboard_data['scraping_status']:
            del dashboard_data['scraping_status']['start_time']
        
        logger.info("Dashboard data generated successfully")
        return jsonify(dashboard_data)
        
    except Exception as e:
        logger.error(f"Error generating dashboard data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/reanalyze', methods=['POST'])
def reanalyze():
    """
    Run scraper endpoint.
    Endpoint: /api/reanalyze
    Method: POST
    Input: {"content": "reanalyze", "prime_bank_posts": 50, "other_banks_posts": 30}
    Output: {"scraping_status": "running", "configuration": {...}}
    """
    try:
        request_data = request.get_json()
        if not request_data or request_data.get('content') != 'reanalyze':
            return jsonify({'error': 'Invalid request. Expected {"content": "reanalyze"}'}), 400
        
        if scraper_status['status'] == 'running':
            return jsonify({'error': 'Scraper is already running'}), 400
        
        # Get post count parameters (with defaults)
        prime_bank_posts = request_data.get('prime_bank_posts', 20)
        other_banks_posts = request_data.get('other_banks_posts', 15)
        
        # Validate post counts
        try:
            prime_bank_posts = int(prime_bank_posts)
            other_banks_posts = int(other_banks_posts)
            
            if prime_bank_posts < 1 or prime_bank_posts > 200:
                return jsonify({'error': 'prime_bank_posts must be between 1 and 200'}), 400
            if other_banks_posts < 1 or other_banks_posts > 200:
                return jsonify({'error': 'other_banks_posts must be between 1 and 200'}), 400
                
        except (ValueError, TypeError):
            return jsonify({'error': 'prime_bank_posts and other_banks_posts must be integers'}), 400
        
        logger.info(f"Starting scraper pipeline with {prime_bank_posts} Prime Bank posts and {other_banks_posts} other bank posts...")
        
        # Start scraper in background thread with parameters
        scraper_thread = threading.Thread(target=run_scraper, args=(prime_bank_posts, other_banks_posts))
        scraper_thread.daemon = True
        scraper_thread.start()
        
        return jsonify({
            'scraping_status': 'running',
            'configuration': {
                'prime_bank_posts': prime_bank_posts,
                'other_banks_posts': other_banks_posts
            }
        })
        
    except Exception as e:
        logger.error(f"Error starting scraper: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/full_data', methods=['POST'])
def get_full_data():
    """
    Full data view endpoint (legacy support).
    Endpoint: /api/full_data
    Method: POST
    Input: {"content": "give_full_data"}
    Output: Posts and Comments data
    """
    try:
        request_data = request.get_json()
        if not request_data or request_data.get('content') != 'give_full_data':
            return jsonify({'error': 'Invalid request. Expected {"content": "give_full_data"}'}), 400
        
        # Get CSV data
        posts_csv_file = analytics.csv_dir / "prime_bank_facebook_posts_data.csv"
        comments_csv_file = analytics.csv_dir / "prime_bank_comments_scraped.csv"
        
        logger.info(f"Looking for posts CSV at: {posts_csv_file}")
        logger.info(f"Looking for comments CSV at: {comments_csv_file}")
        logger.info(f"Posts CSV exists: {posts_csv_file.exists()}")
        logger.info(f"Comments CSV exists: {comments_csv_file.exists()}")
        
        posts_data = []
        comments_data = []
        
        # Load posts data
        if posts_csv_file.exists():
            import csv
            with open(posts_csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                row_count_posts = 0
                for row in reader:
                    row_count_posts += 1
                    # Debug: Check the entire row we're reading for the first few posts
                    if row_count_posts <= 3:
                        logger.info(f"Reading post row {row_count_posts}: {row}")
                    
                    post_data = {
                        'date': '',  # No timestamp field in posts CSV
                        'whole_row':row,  # Include the whole row for debugging
                        'reaction_count': int(row.get('reaction_count', 0)),
                        'comment_count': int(row.get('comments_count', 0)),
                        'share_count': int(row.get('share_count', 0)),
                        'text': row.get('text', ''),
                        'sentiment': row.get('sentiment', ''),
                        'emotion': row.get('emotion', ''),
                        'category': row.get('category', ''),
                        'Viral_score': float(row.get('virality_score', 0) or 0),  # Fixed: use correct column name
                        'post_routing_id': row.get('post_routing_id', ''),
                        'post_url': row.get('post_url', '')
                    }
                    posts_data.append(post_data)
        
        # Load comments data
        if comments_csv_file.exists():
            logger.info("Loading comments from CSV...")
            import csv
            try:
                with open(comments_csv_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    row_count = 0
                    for row in reader:
                        row_count += 1
                        
                        # Debug: Check the entire row we're reading for the first few comments
                        if row_count <= 3:
                            logger.info(f"Reading comment row {row_count}: {row}")
                        
                        # Calculate virality score for comments: reaction + comment*2
                        likes_count = int(row.get('likes_count', 0) or 0)
                        comments_count = int(row.get('comments_count', 0) or 0)
                        virality_score = likes_count + (comments_count * 2)
                        
                        # Debug: Log the calculated virality score
                        if row_count <= 3:
                            logger.info(f"Comment row {row_count} - Calculated virality_score: {virality_score}")
                        
                        comment_data = {
                            'whole_row':row,  # Include the whole row for debugging
                            'post_routing_id': row.get('post_routing_id', ''),
                            'comment_text': row.get('comment_text', ''),
                            'comment_author': row.get('author_name', ''),
                            'comment_time': row.get('timestamp', ''),
                            'comment_likes': likes_count,
                            'comment_replies': comments_count,
                            'comment_url': row.get('comment_url', ''),
                            'post_url': row.get('post_url', ''),
                            'comment_id': row.get('comment_id', ''),
                            'virality_score': virality_score
                        }
                        comments_data.append(comment_data)
                    logger.info(f"Processed {row_count} comment rows")
            except Exception as e:
                logger.error(f"Error reading comments CSV: {e}")
        else:
            logger.warning("Comments CSV file not found")
        
        logger.info(f"Loaded {len(posts_data)} posts and {len(comments_data)} comments")
        
        return jsonify({
            'Posts': posts_data,
            'Comments': comments_data,
            'Summary': {
                'total_posts': len(posts_data),
                'total_comments': len(comments_data),
                'posts_csv_exists': posts_csv_file.exists(),
                'comments_csv_exists': comments_csv_file.exists()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting full data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/status', methods=['GET'])
def get_scraper_status():
    """Get current scraper status."""
    status = scraper_status.copy()
    if 'start_time' in status:
        del status['start_time']
    return jsonify(status)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Set up the environment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask Dashboard API on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=debug)
