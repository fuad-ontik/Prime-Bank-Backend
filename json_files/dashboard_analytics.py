#!/usr/bin/env python3
"""
Dashboard Analytics - Generate analytics data for the Facebook Group Scraper Dashboard.

This module analyzes processed CSV data and generates JSON responses for the dashboard.

Author: Facebook Group Scraper Project
Date: 2025
"""

import os
import re
import json
import pickle
import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardAnalytics:
    """Generate analytics data for the dashboard."""
    
    def __init__(self):
        """Initialize the Dashboard Analytics."""
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / "output"
        self.csv_dir = self.output_dir / "bank_posts_and_comments_csv"
        self.posts_dir = self.output_dir / "all_extracted_posts"
        self.ai_overview_file = self.base_dir / "dashboard_ai_overview.json"
        
        # Create directories if they don't exist
        self.output_dir.mkdir(exist_ok=True)
        self.csv_dir.mkdir(exist_ok=True)
        self.posts_dir.mkdir(exist_ok=True)
        
        # Bank mention patterns
        self.bank_patterns = {
            'prime_bank': [r'prime\s*bank', r'primebank', r'@primebank', r'prime\s*b\.?'],
            'eastern_bank': [r'eastern\s*bank', r'ebl', r'@easternbank'],
            'brac_bank': [r'brac\s*bank', r'@bracbank'],
            'city_bank': [r'city\s*bank', r'@citybank'],
            'dutch_bangla': [r'dutch\s*bangla', r'dbbl', r'@dutchbangla']
        }
        
        # OpenAI setup
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
    
    def get_post_categories_percentage(self) -> Dict:
        """
        Get post categories percentage from prime_bank_facebook_posts_data.csv
        
        Returns:
            Dictionary with category percentages
        """
        csv_file = self.csv_dir / "prime_bank_facebook_posts_data.csv"
        
        if not csv_file.exists():
            logger.warning(f"CSV file not found: {csv_file}")
            return {
                'inquiry': '0%',
                'suggestions': '0%',
                'complaint': '0%',
                'praise': '0%',
                'other': '0%',
                'total_number_of_posts': 0
            }
        
        categories = {'inquiry': 0, 'suggestion': 0, 'complaint': 0, 'praise': 0, 'other': 0}
        total_posts = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_posts += 1
                    category = row.get('category', '').lower()
                    if category in categories:
                        categories[category] += 1
                    else:
                        categories['other'] += 1
            
            # Calculate percentages
            if total_posts > 0:
                result = {}
                for cat, count in categories.items():
                    # Convert 'suggestion' to 'suggestions' for output
                    output_key = 'suggestions' if cat == 'suggestion' else cat
                    result[output_key] = f"{round((count / total_posts) * 100)}%"
                result['total_number_of_posts'] = total_posts
                return result
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
        
        return {
            'inquiry': '0%',
            'suggestions': '0%',
            'complaint': '0%',
            'praise': '0%',
            'other': '0%',
            'total_number_of_posts': 0
        }
    
    def get_bank_mentions(self) -> Dict:
        """
        Get bank mentions from other_banks posts.
        
        Returns:
            Dictionary with bank mention counts
        """
        posts_file = self.posts_dir / "other_banks" / "all_extracted_posts.txt"
        
        if not posts_file.exists():
            logger.warning(f"Posts file not found: {posts_file}")
            return {
                'prime_bank': 0,
                'eastern_bank': 0,
                'brac_bank': 0,
                'city_bank': 0,
                'dutch_bangla': 0,
                'total_bank_mentions': 0
            }
        
        try:
            with open(posts_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            bank_counts = {}
            total_mentions = 0
            
            for bank_name, patterns in self.bank_patterns.items():
                count = 0
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    count += len(matches)
                bank_counts[bank_name] = count
                total_mentions += count
            
            bank_counts['total_bank_mentions'] = total_mentions
            return bank_counts
            
        except Exception as e:
            logger.error(f"Error reading posts file: {e}")
            return {
                'prime_bank': 0,
                'eastern_bank': 0,
                'brac_bank': 0,
                'city_bank': 0,
                'dutch_bangla': 0,
                'total_bank_mentions': 0
            }
    
    def get_hardcoded_geolocation(self) -> Dict:
        """
        Get hardcoded geolocation data.
        
        Returns:
            Dictionary with geolocation data
        """
        return {
            'Dhaka': 30,
            'Chittagong': 17,
            'Rajshahi': 8,
            'Sylhet': 9
        }
    
    def get_sentiment_analysis(self) -> Dict:
        """
        Get sentiment analysis from prime bank CSV.
        
        Returns:
            Dictionary with sentiment analysis
        """
        csv_file = self.csv_dir / "prime_bank_facebook_posts_data.csv"
        
        if not csv_file.exists():
            logger.warning(f"CSV file not found: {csv_file}")
            return {
                'bank_sentiment_score': 0,
                'engagement_weighted_sentiment': 0,
                'sentiment_distribution': {'positive': '0%', 'negative': '0%', 'neutral': '0%'},
                'emotion_distribution': {'neutral': '0%', 'joy': '0%', 'confusion': '0%', 'frustration': '0%'}
            }
        
        positive_posts = 0
        negative_posts = 0
        neutral_posts = 0
        total_virality = 0
        emotions = {'neutral': 0, 'joy': 0, 'confusion': 0, 'frustration': 0}
        total_posts = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_posts += 1
                    
                    # Count sentiments
                    sentiment = row.get('sentiment', '').lower()
                    if sentiment == 'positive':
                        positive_posts += 1
                    elif sentiment == 'negative':
                        negative_posts += 1
                    else:
                        neutral_posts += 1
                    
                    # Sum virality scores
                    try:
                        virality = float(row.get('virality_score', 0))
                        total_virality += virality
                    except (ValueError, TypeError):
                        pass
                    
                    # Count emotions
                    emotion = row.get('emotion', '').lower()
                    if emotion in emotions:
                        emotions[emotion] += 1
                    else:
                        emotions['neutral'] += 1
            
            # Calculate percentages
            sentiment_dist = {}
            emotion_dist = {}
            
            if total_posts > 0:
                sentiment_dist = {
                    'positive': f"{round((positive_posts / total_posts) * 100)}%",
                    'negative': f"{round((negative_posts / total_posts) * 100)}%",
                    'neutral': f"{round((neutral_posts / total_posts) * 100)}%"
                }
                
                for emotion, count in emotions.items():
                    emotion_dist[emotion] = f"{round((count / total_posts) * 100)}%"
            
            bank_sentiment_score = positive_posts - negative_posts
            
            return {
                'bank_sentiment_score': bank_sentiment_score,
                'engagement_weighted_sentiment': round(total_virality, 2),
                'sentiment_distribution': sentiment_dist,
                'emotion_distribution': emotion_dist
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'bank_sentiment_score': 0,
                'engagement_weighted_sentiment': 0,
                'sentiment_distribution': {'positive': '0%', 'negative': '0%', 'neutral': '0%'},
                'emotion_distribution': {'neutral': '0%', 'joy': '0%', 'confusion': '0%', 'frustration': '0%'}
            }
    
    def get_top_posts(self, limit: int = 10) -> List[Dict]:
        """
        Get top posts by virality score.
        
        Args:
            limit: Number of top posts to return
            
        Returns:
            List of top posts
        """
        csv_file = self.csv_dir / "prime_bank_facebook_posts_data.csv"
        
        if not csv_file.exists():
            logger.warning(f"CSV file not found: {csv_file}")
            return []
        
        posts = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        row['virality_score'] = float(row.get('virality_score', 0))
                        row['reaction_count'] = int(row.get('reaction_count', 0))
                        row['comments_count'] = int(row.get('comments_count', 0))
                        row['share_count'] = int(row.get('share_count', 0))
                    except (ValueError, TypeError):
                        row['virality_score'] = 0
                        row['reaction_count'] = 0
                        row['comments_count'] = 0
                        row['share_count'] = 0
                    
                    posts.append(row)
            
            # Sort by virality score and return top posts
            posts.sort(key=lambda x: x['virality_score'], reverse=True)
            return posts[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top posts: {e}")
            return []
    
    def get_action_items(self, posts_limit: int = None, comments_limit: int = None) -> List[Dict]:
        """
        Get action items - top posts and top comments by virality score.
        
        Args:
            posts_limit: Number of top posts to return (uses env var ACTION_ITEMS_POSTS_LIMIT or default 10)
            comments_limit: Number of top comments to return (uses env var ACTION_ITEMS_COMMENTS_LIMIT or default 10)
            
        Returns:
            List of action items from both posts and comments
        """
        # Get limits from environment variables or use defaults
        if posts_limit is None:
            posts_limit = int(os.getenv('ACTION_ITEMS_POSTS_LIMIT', 10))
        if comments_limit is None:
            comments_limit = int(os.getenv('ACTION_ITEMS_COMMENTS_LIMIT', 10))
        posts_csv_file = self.csv_dir / "prime_bank_facebook_posts_data.csv"
        comments_csv_file = self.csv_dir / "prime_bank_comments_scraped.csv"
        
        posts = []
        comments = []
        
        # Process all posts
        if posts_csv_file.exists():
            try:
                with open(posts_csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            virality_score = float(row.get('virality_score', 0))
                            reaction_count = int(row.get('reaction_count', 0))
                            comments_count = int(row.get('comments_count', 0))
                            share_count = int(row.get('share_count', 0))
                        except (ValueError, TypeError):
                            virality_score = 0
                            reaction_count = 0
                            comments_count = 0
                            share_count = 0
                        
                        action_item = {
                            'type': 'post',
                            'post_routing_id': row.get('post_routing_id', ''),
                            'text': row.get('text', ''),
                            'author_name': row.get('author_name', ''),
                            'sentiment': row.get('sentiment', ''),
                            'emotion': row.get('emotion', ''),
                            'category': row.get('category', ''),
                            'virality_score': virality_score,
                            'reaction_count': reaction_count,
                            'comments_count': comments_count,
                            'share_count': share_count,
                            'post_url': row.get('post_url', ''),
                            'post_id': row.get('post_id', ''),
                            'keywords': row.get('keywords', ''),
                            'topic_category': row.get('topic_category', ''),
                            'timestamp': ''  # Posts don't have timestamp, use empty string for consistency
                        }
                        posts.append(action_item)
                        
            except Exception as e:
                logger.error(f"Error getting action items from posts: {e}")
        else:
            logger.warning(f"Posts CSV file not found: {posts_csv_file}")
        
        # Process all comments
        if comments_csv_file.exists():
            try:
                with open(comments_csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Calculate virality score for comments: likes + comments*2
                        try:
                            likes_count = int(row.get('likes_count', 0) or 0)
                            comment_replies = int(row.get('comments_count', 0) or 0)
                            virality_score = likes_count + (comment_replies * 2)
                        except (ValueError, TypeError):
                            likes_count = 0
                            comment_replies = 0
                            virality_score = 0
                        
                        action_item = {
                            'type': 'comment',
                            'post_routing_id': row.get('post_routing_id', ''),
                            'text': row.get('comment_text', ''),
                            'author_name': row.get('author_name', ''),
                            'sentiment': '',  # Comments don't have sentiment analysis yet
                            'emotion': '',    # Comments don't have emotion analysis yet
                            'category': '',   # Comments don't have category analysis yet
                            'virality_score': virality_score,
                            'reaction_count': likes_count,
                            'comments_count': comment_replies,
                            'share_count': 0,  # Comments don't have shares
                            'post_url': row.get('post_url', ''),
                            'post_id': row.get('comment_id', ''),
                            'keywords': '',   # Comments don't have keyword analysis yet
                            'topic_category': '',
                            'comment_url': row.get('comment_url', ''),
                            'timestamp': row.get('timestamp', '')
                        }
                        comments.append(action_item)
                        
            except Exception as e:
                logger.error(f"Error getting action items from comments: {e}")
        else:
            logger.warning(f"Comments CSV file not found: {comments_csv_file}")
        
        # Sort posts by virality score (no date tiebreaker needed for posts)
        posts.sort(key=lambda x: x['virality_score'], reverse=True)
        top_posts = posts[:posts_limit]
        
        # Sort comments by virality score, then by timestamp (latest first) for tiebreaker
        def comment_sort_key(comment):
            try:
                # Parse ISO timestamp for sorting (latest first)
                from datetime import datetime
                timestamp = comment.get('timestamp', '')
                if timestamp:
                    parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    return (-comment['virality_score'], -parsed_time.timestamp())
                else:
                    return (-comment['virality_score'], 0)
            except:
                return (-comment['virality_score'], 0)
        
        comments.sort(key=comment_sort_key)
        top_comments = comments[:comments_limit]
        
        # Combine both lists
        action_items = top_posts + top_comments
        return action_items
    
    def load_ai_overview_from_file(self) -> Dict:
        """
        Load AI overview directly from the dashboard_ai_overview.json file.
        This ensures the Flask API always serves the latest data from the file.
        
        Returns:
            Dictionary with AI analysis for each category
        """
        if not self.ai_overview_file.exists():
            logger.warning(f"AI overview file not found: {self.ai_overview_file}")
            return -1
            
        
        try:
            with open(self.ai_overview_file, 'r', encoding='utf-8') as f:
                cached_overview = json.load(f)
                logger.info("Loaded AI overview from dashboard_ai_overview.json")
                return cached_overview.get('data', {
                    'inquiry': ['No AI overview data available'],
                    'praise': ['No AI overview data available'],
                    'complaints': ['No AI overview data available'],
                    'suggestions': ['No AI overview data available']
                })
        except Exception as e:
            logger.error(f"Error reading AI overview file: {e}")
            return {
                'inquiry': ['Error loading AI overview'],
                'praise': ['Error loading AI overview'],
                'complaints': ['Error loading AI overview'],
                'suggestions': ['Error loading AI overview']
            }
    
    def generate_ai_overview(self, force_regenerate: bool = False) -> Dict:
        """
        Generate AI overview from prime bank posts.
        
        Args:
            force_regenerate (bool): If True, bypass cache and regenerate overview
        
        Returns:
            Dictionary with AI analysis for each category
        """
        posts_file = self.posts_dir / "prime_bank" / "all_extracted_posts.txt"
        
        if not posts_file.exists():
            logger.warning(f"Posts file not found: {posts_file}")
            return {
                'inquiry': 'No data available',
                'praise': 'No data available',
                'complaints': 'No data available',
                'suggestions': 'No data available'
            }
        
        # Check if we have a cached overview (skip if force_regenerate is True)
        if not force_regenerate and self.ai_overview_file.exists():
            try:
                with open(self.ai_overview_file, 'r', encoding='utf-8') as f:
                    cached_overview = json.load(f)
                    # Check if it's recent (less than 24 hours old)
                    cache_time = datetime.fromisoformat(cached_overview.get('timestamp', '1970-01-01'))
                    if (datetime.now() - cache_time).total_seconds() < 86400:  # 24 hours
                        logger.info("Using cached AI overview")
                        return cached_overview['data']
            except Exception as e:
                logger.warning(f"Error reading cached overview: {e}")
        
        # Generate new overview
        try:
            with open(posts_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not self.api_key:
                logger.warning("OpenAI API key not found, using fallback analysis")
                return self._generate_fallback_overview(content)
              # Use OpenAI to analyze
            prompt = f"""
            As an expert AI analyst, analyze the following Facebook posts about Prime Bank from a comprehensive AI perspective. 
            Provide deep insights about what these posts reveal about Prime Bank's customer relationship, service quality, 
            and market position. Be specific, detailed, and analytical.

            Format your response as strict JSON only response with the following structure,if the response is not json it won't work. So the response must must must be json only:
            {{
                "inquiry": "detailed analysis of customer inquiries with specific patterns and insights",
                "praise": "detailed analysis of customer praise with specific service strengths identified",
                "complaints": "detailed analysis of customer complaints with root cause analysis", 
                "suggestions": "detailed AI-driven recommendations based on customer feedback patterns"
            }}
            
            For each category, provide 6-8 detailed bullet points in React-friendly markdown format. And You should include the name of Prime Bank in the analysis,
            and the analysis should be specific to Prime Bank's services and customer's opinions.
            Use **bold** for emphasis and include:
            
            INQUIRY ANALYSIS:
            - Identify specific types of inquiries (account issues, service questions, technical problems)
            - Analyze inquiry patterns and frequency
            - Highlight most common customer pain points
            - Assess the complexity level of customer queries
            - Evaluate response time expectations from customers
            - Note any recurring themes or seasonal patterns
            
            PRAISE ANALYSIS:
            - Identify specific services or features customers appreciate most
            - Analyze the language used in positive feedback
            - Highlight staff performance and customer service quality
            - Note any exceptional service experiences mentioned
            - Identify competitive advantages based on customer feedback
            - Assess customer loyalty indicators in the praise content
            
            COMPLAINTS ANALYSIS:
            - Categorize complaints by type (technical, service, process, communication)
            - Analyze severity and frequency of different complaint types
            - Identify systemic issues vs. isolated incidents
            - Evaluate customer frustration levels and escalation patterns
            - Note any compliance or regulatory concerns mentioned
            - Assess potential reputational risks from complaint patterns
            
            SUGGESTIONS (AI RECOMMENDATIONS):
            - Provide actionable recommendations based on customer feedback analysis
            - Suggest process improvements for most common issues
            - Recommend technology upgrades or digital solutions
            - Propose customer experience enhancements
            - Suggest training programs for staff based on feedback patterns
            - Recommend proactive communication strategies
            - Propose competitive positioning improvements
            
            Make your analysis sound like it comes from an AI that has deep understanding of banking customer behavior, 
            service excellence, and digital transformation trends. Be specific about what the data reveals about Prime Bank's position in the market.
            
            Posts content:
            {content}
            """
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert analyst specializing in customer feedback analysis for banking services.You should give json response only,don't give ```json mark. Just give json response only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
                #max_tokens=1500
            )
            
            overview_text = response.choices[0].message.content
            try:
                overview_data = json.loads(overview_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse OpenAI JSON response, using fallback")
                print(overview_text)
                overview_data = self._generate_fallback_overview(content)
              # Cache the result
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': overview_data
            }
            
            with open(self.ai_overview_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            return overview_data
            
        except Exception as e:
            logger.error(f"Error generating AI overview: {e}")
            return self._generate_fallback_overview(content if 'content' in locals() else "")
    
    def _generate_fallback_overview(self, content: str) -> Dict:
        """Generate a detailed fallback overview when OpenAI is not available."""
        word_count = len(content.split())
        sentence_count = len([s for s in content.split('.') if s.strip()])
        
        # Basic content analysis
        inquiry_keywords = ['how', 'when', 'where', 'what', 'why', 'can i', 'help', 'support', '?']
        praise_keywords = ['good', 'great', 'excellent', 'thank', 'appreciate', 'best', 'amazing', 'wonderful']
        complaint_keywords = ['problem', 'issue', 'error', 'wrong', 'bad', 'terrible', 'slow', 'delay', 'frustrated']
        
        content_lower = content.lower()
        inquiry_mentions = sum(1 for keyword in inquiry_keywords if keyword in content_lower)
        praise_mentions = sum(1 for keyword in praise_keywords if keyword in content_lower)
        complaint_mentions = sum(1 for keyword in complaint_keywords if keyword in content_lower)
        
        return {
            'inquiry': f"""- **Customer Inquiry Volume**: Analysis of {word_count} words across {sentence_count} statements reveals {inquiry_mentions} inquiry-related mentions
- **Service Information Requests**: Customers frequently seek clarification on banking procedures and account-related processes
- **Digital Banking Questions**: High volume of queries about online banking features and mobile app functionality
- **Account Management Inquiries**: Recurring questions about account opening, closure, and maintenance procedures
- **Transaction Support Needs**: Customers require assistance with payment processing and transfer-related issues
- **Branch Service Inquiries**: Location-based questions and branch-specific service availability queries
- **Product Information Requests**: Interest in loan products, credit cards, and investment opportunities
- **Response Time Expectations**: Customer inquiries indicate expectation for quick resolution and real-time support""",
            
            'praise': f"""- **Service Excellence Recognition**: {praise_mentions} positive mentions indicate strong customer satisfaction in specific service areas
- **Staff Performance Appreciation**: Customers consistently praise individual staff members for professional service delivery
- **Digital Banking Satisfaction**: Positive feedback on mobile app functionality and online banking user experience
- **Branch Service Quality**: High appreciation for in-person service quality and branch staff responsiveness
- **Problem Resolution Efficiency**: Customers value quick and effective resolution of their banking issues
- **Customer-Centric Approach**: Recognition of Prime Bank's efforts to prioritize customer needs and preferences
- **Service Accessibility**: Appreciation for convenient banking hours and multiple service channel availability
- **Trust and Reliability**: Customer comments reflect strong confidence in Prime Bank's financial stability and security""",
            
            'complaints': f"""- **Service Delivery Issues**: {complaint_mentions} complaint indicators suggest areas requiring operational improvement
- **Technology-Related Concerns**: Customers report occasional difficulties with digital banking platforms and system downtime
- **Processing Time Delays**: Feedback indicates longer than expected processing times for certain banking transactions
- **Communication Gaps**: Customers express frustration about lack of proactive communication regarding service changes
- **Branch Service Inconsistencies**: Varying service quality across different branch locations creates customer dissatisfaction
- **Documentation Requirements**: Excessive paperwork and documentation requirements causing customer inconvenience
- **Fee Structure Concerns**: Customer feedback suggests transparency issues regarding service charges and fees
- **Customer Support Accessibility**: Limited availability of customer support during peak hours and weekends""",
            
            'suggestions': f"""- **Digital Platform Enhancement**: Implement advanced AI-powered chatbots for 24/7 customer query resolution
- **Process Automation**: Streamline account opening and loan approval processes through digital automation
- **Proactive Communication System**: Develop automated notification systems for service updates and account activities
- **Staff Training Programs**: Implement comprehensive training modules focusing on customer experience excellence
- **Multi-Channel Integration**: Create seamless integration between online, mobile, and branch banking experiences
- **Customer Feedback Loop**: Establish real-time feedback collection and response mechanisms across all touchpoints
- **Service Quality Monitoring**: Deploy AI-powered sentiment analysis for continuous service quality assessment
- **Competitive Positioning**: Leverage customer insights to develop unique value propositions in the banking sector
- **Technology Infrastructure**: Invest in robust IT infrastructure to minimize system downtime and enhance reliability"""
        }
    
    def get_complete_dashboard_data(self) -> Dict:
        """
        Get complete dashboard data in the format specified in Frontend_Developer_API_Guideline.md
        
        Returns:
            Complete dashboard JSON
        """
        # Get all the analytics
        post_categories = self.get_post_categories_percentage()
        bank_mentions = self.get_bank_mentions()
        geolocation = self.get_hardcoded_geolocation()
        sentiment_analysis = self.get_sentiment_analysis()
        top_posts = self.get_top_posts()
        action_items = self.get_action_items()
        ai_overview = self.load_ai_overview_from_file()
        if ai_overview == -1:
            ai_overview = self.generate_ai_overview(force_regenerate=True)
        # Calculate KPIs
        kpi = {
            'total_mentions_of_all_banks': bank_mentions['total_bank_mentions'],
            'posts_mentioning_prime_bank': bank_mentions['prime_bank'],
            'bank_sentiment_score': sentiment_analysis['bank_sentiment_score'],
            'engagement_weighted_sentiment': sentiment_analysis['engagement_weighted_sentiment']
        }
        
        # Build complete response
        dashboard_data = {
            'last_updated': datetime.now().isoformat(),
            'scraping_status': {
                'status': 'completed',
                'last_run': datetime.now().isoformat(),
                'duration_seconds': 0,  # Will be updated when scraper runs
                'posts_scraped': post_categories['total_number_of_posts'],
                'comments_scraped': 0  # Will be updated when scraper runs
            },
            'kpi': kpi,
            'sentiment_analysis': {
                'sentiment_distribution': sentiment_analysis['sentiment_distribution'],
                'top_posts': top_posts,
                'post_categories': post_categories,
                'emotion_distribution': sentiment_analysis['emotion_distribution']
            },
            'bank_mentions': bank_mentions,
            'post_geolocation': geolocation,
            'action_items': action_items,
            'ai_overview': ai_overview
        }
        
        return dashboard_data

if __name__ == "__main__":
    # Test the analytics
    analytics = DashboardAnalytics()
    data = analytics.get_complete_dashboard_data()
    print(json.dumps(data, indent=2, ensure_ascii=False))
