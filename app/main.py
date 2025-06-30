from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
import os

from flasgger import Swagger

app = Flask(__name__)
Swagger(app)


# Sample data (replace with your actual data source)
data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dashboard_data.json')
with open(data_path, 'r', encoding='utf-8') as f:
    DASHBOARD_DATA = json.load(f)

# Helper function to get current timestamp
def get_current_timestamp():
    return datetime.now().isoformat()

# Error handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested resource was not found on this server.',
        'timestamp': get_current_timestamp()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An internal server error occurred.',
        'timestamp': get_current_timestamp()
    }), 500

# Root endpoint - Health check
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'API is running',
        'timestamp': get_current_timestamp(),
        'version': '1.0.0'
    })

# Get all dashboard data
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get complete dashboard data"""
    try:
        response_data = DASHBOARD_DATA.copy()
        response_data['last_updated'] = get_current_timestamp()
        return jsonify({
            'success': True,
            'data': response_data,
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

# Action Items Endpoints
@app.route('/api/action-items', methods=['GET'])
def get_action_items():
    """Get all action items with optional filtering"""
    try:
        # Query parameters for filtering
        category = request.args.get('category')
        sentiment = request.args.get('sentiment')
        limit = request.args.get('limit', type=int)
        
        action_items = DASHBOARD_DATA['action_items']
        
        # Apply filters
        if category:
            action_items = [item for item in action_items if item.get('category', '').lower() == category.lower()]
        
        if sentiment:
            action_items = [item for item in action_items if item.get('sentiment', '').lower() == sentiment.lower()]
        
        # Apply limit
        if limit:
            action_items = action_items[:limit]
        
        return jsonify({
            'success': True,
            'data': action_items,
            'count': len(action_items),
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

@app.route('/api/action-items/<post_id>', methods=['GET'])
def get_action_item_by_id(post_id):
    """Get specific action item by post ID"""
    try:
        action_item = next((item for item in DASHBOARD_DATA['action_items'] if item['post_id'] == post_id), None)
        
        if not action_item:
            return jsonify({
                'success': False,
                'error': 'Action item not found',
                'timestamp': get_current_timestamp()
            }), 404
        
        return jsonify({
            'success': True,
            'data': action_item,
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

# AI Overview Endpoints
@app.route('/api/ai-overview', methods=['GET'])
def get_ai_overview():
    """Get complete AI overview"""
    try:
        return jsonify({
            'success': True,
            'data': DASHBOARD_DATA['ai_overview'],
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

@app.route('/api/ai-overview/complaints', methods=['GET'])
def get_complaints_analysis():
    """Get complaints analysis"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'complaints': DASHBOARD_DATA['ai_overview']['complaints']
            },
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

@app.route('/api/ai-overview/inquiries', methods=['GET'])
def get_inquiries_analysis():
    """Get inquiries analysis"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'inquiry': DASHBOARD_DATA['ai_overview']['inquiry']
            },
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

@app.route('/api/ai-overview/praise', methods=['GET'])
def get_praise_analysis():
    """Get praise analysis"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'praise': DASHBOARD_DATA['ai_overview']['praise']
            },
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

@app.route('/api/ai-overview/suggestions', methods=['GET'])
def get_suggestions_analysis():
    """Get AI suggestions"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'suggestions': DASHBOARD_DATA['ai_overview']['suggestions']
            },
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

# Bank Mentions Endpoints
@app.route('/api/bank-mentions', methods=['GET'])
def get_bank_mentions():
    """Get bank mentions data"""
    try:
        return jsonify({
            'success': True,
            'data': DASHBOARD_DATA['bank_mentions'],
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

# KPI Endpoints
@app.route('/api/kpi', methods=['GET'])
def get_kpi():
    """Get KPI metrics"""
    try:
        return jsonify({
            'success': True,
            'data': DASHBOARD_DATA['kpi'],
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

# Geolocation Endpoints
@app.route('/api/geolocation', methods=['GET'])
def get_geolocation_data():
    """Get post geolocation distribution"""
    try:
        return jsonify({
            'success': True,
            'data': DASHBOARD_DATA['post_geolocation'],
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

# Scraping Status Endpoints
@app.route('/api/scraping-status', methods=['GET'])
def get_scraping_status():
    """Get scraping status information"""
    try:
        return jsonify({
            'success': True,
            'data': DASHBOARD_DATA['scraping_status'],
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

# Sentiment Analysis Endpoints
@app.route('/api/sentiment-analysis', methods=['GET'])
def get_sentiment_analysis():
    """Get complete sentiment analysis"""
    try:
        return jsonify({
            'success': True,
            'data': DASHBOARD_DATA['sentiment_analysis'],
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

@app.route('/api/sentiment-analysis/emotions', methods=['GET'])
def get_emotion_distribution():
    """Get emotion distribution"""
    try:
        return jsonify({
            'success': True,
            'data': DASHBOARD_DATA['sentiment_analysis']['emotion_distribution'],
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

@app.route('/api/sentiment-analysis/categories', methods=['GET'])
def get_post_categories():
    """Get post categories distribution"""
    try:
        return jsonify({
            'success': True,
            'data': DASHBOARD_DATA['sentiment_analysis']['post_categories'],
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

@app.route('/api/sentiment-analysis/sentiments', methods=['GET'])
def get_sentiment_distribution():
    """Get sentiment distribution"""
    try:
        return jsonify({
            'success': True,
            'data': DASHBOARD_DATA['sentiment_analysis']['sentiment_distribution'],
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

@app.route('/api/sentiment-analysis/top-posts', methods=['GET'])
def get_top_posts():
    """Get top posts with optional limit"""
    try:
        limit = request.args.get('limit', default=10, type=int)
        top_posts = DASHBOARD_DATA['sentiment_analysis'].get('top_posts', [])
        
        if limit:
            top_posts = top_posts[:limit]
        
        return jsonify({
            'success': True,
            'data': top_posts,
            'count': len(top_posts),
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

# Statistics and Summary Endpoints
@app.route('/api/summary', methods=['GET'])
def get_dashboard_summary():
    """Get dashboard summary statistics"""
    try:
        summary = {
            'total_action_items': len(DASHBOARD_DATA['action_items']),
            'total_bank_mentions': DASHBOARD_DATA['bank_mentions']['total_bank_mentions'],
            'prime_bank_mentions': DASHBOARD_DATA['bank_mentions']['prime_bank'],
            'sentiment_score': DASHBOARD_DATA['kpi']['bank_sentiment_score'],
            'posts_scraped': DASHBOARD_DATA['scraping_status']['posts_scraped'],
            'scraping_status': DASHBOARD_DATA['scraping_status']['status'],
            'top_emotion': max(DASHBOARD_DATA['sentiment_analysis']['emotion_distribution'].items(), key=lambda x: int(x[1].replace('%', ''))),
            'dominant_sentiment': max(DASHBOARD_DATA['sentiment_analysis']['sentiment_distribution'].items(), key=lambda x: int(x[1].replace('%', '')))
        }
        
        return jsonify({
            'success': True,
            'data': summary,
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

# Search endpoint
@app.route('/api/search', methods=['GET'])
def search_posts():
    """Search through action items"""
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required',
                'timestamp': get_current_timestamp()
            }), 400
        
        results = []
        for item in DASHBOARD_DATA['action_items']:
            if (query in item.get('text', '').lower() or 
                query in item.get('keywords', '').lower() or
                query in item.get('author_name', '').lower()):
                results.append(item)
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'query': query,
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500
    

##ai_overview_path
ai_overview_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dashboard_ai_overview.json')
with open(ai_overview_path, 'r', encoding='utf-8') as f:
    DASHBOARD_AI_OVERVIEW = json.load(f)

@app.route('/api/dashboard-ai-overview', methods=['GET'])
def get_dashboard_ai_overview():
    """Get dashboard AI overview data"""
    try:
        return jsonify({
            'success': True,
            'data': DASHBOARD_AI_OVERVIEW,
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500


#full data path
full_data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'full_data.json')
with open(full_data_path, 'r', encoding='utf-8') as f:
    FULL_DATA = json.load(f)

@app.route('/api/full-data/<page_no>', methods=['GET'])
def get_full_data(page_no):
    """Get full data from full_data.json with pagination (50 items per page, posts prioritized)"""
    try:
        # Convert page_no to integer and handle invalid input
        try:
            page = int(page_no)
            if page < 1:
                raise ValueError("Page number must be positive")
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': get_current_timestamp()
            }), 400

        items_per_page = 50
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page

        posts = FULL_DATA['Posts']
        comments = FULL_DATA['Comments']
        posts_len = len(posts)
        comments_len = len(comments)

        # Get posts for this page
        posts_slice = posts[start_idx:end_idx] if start_idx < posts_len else []
        num_posts = len(posts_slice)

        # If not enough posts, fill with comments
        if num_posts < items_per_page:
            # Calculate how many more items needed
            remaining = items_per_page - num_posts
            # Comments start index: if posts are exhausted, comments should start at (start_idx - posts_len)
            comments_start = max(0, start_idx - posts_len)
            comments_end = comments_start + remaining
            comments_slice = comments[comments_start:comments_end] if comments_start < comments_len else []
        else:
            comments_slice = []

        # If posts are exhausted for this page, fill with comments only
        if num_posts == 0:
            comments_start = start_idx - posts_len
            comments_end = comments_start + items_per_page
            comments_slice = comments[comments_start:comments_end] if comments_start < comments_len else []

        # Combine for response
        combined_items = posts_slice + comments_slice

        # Calculate total pages based on total items (posts + comments)
        total_items = posts_len + comments_len
        total_pages = (total_items + items_per_page - 1) // items_per_page

        data_to_send = {
            'items': combined_items,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'number_of_pages': total_pages,
                'items_per_page': items_per_page,
                'total_posts': posts_len,
                'total_comments': comments_len
            }
        }

        return jsonify({
            'success': True,
            'data': data_to_send,
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

@app.route('/api/full-data/posts/<page_no>', methods=['GET'])
def get_full_posts(page_no):
    """Get paginated posts from full_data.json (50 per page)"""
    try:
        try:
            page = int(page_no)
            if page < 1:
                raise ValueError("Page number must be positive")
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': get_current_timestamp()
            }), 400

        items_per_page = 25
        posts = FULL_DATA['Posts']
        posts_len = len(posts)
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        posts_slice = posts[start_idx:end_idx] if start_idx < posts_len else []
        total_pages = (posts_len + items_per_page - 1) // items_per_page

        data_to_send = {
            'items': posts_slice,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'number_of_pages': total_pages,
                'items_per_page': items_per_page,
                'total_posts': posts_len
            }
        }
        return jsonify({
            'success': True,
            'data': data_to_send,
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

@app.route('/api/full-data/comments/<page_no>', methods=['GET'])
def get_full_comments(page_no):
    """Get paginated comments from full_data.json (50 per page)"""
    try:
        try:
            page = int(page_no)
            if page < 1:
                raise ValueError("Page number must be positive")
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': get_current_timestamp()
            }), 400

        items_per_page = 25
        comments = FULL_DATA['Comments']
        comments_len = len(comments)
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        comments_slice = comments[start_idx:end_idx] if start_idx < comments_len else []
        total_pages = (comments_len + items_per_page - 1) // items_per_page

        data_to_send = {
            'items': comments_slice,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'number_of_pages': total_pages,
                'items_per_page': items_per_page,
                'total_comments': comments_len
            }
        }
        return jsonify({
            'success': True,
            'data': data_to_send,
            'timestamp': get_current_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)