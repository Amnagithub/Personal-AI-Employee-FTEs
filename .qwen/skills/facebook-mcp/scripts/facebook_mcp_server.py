#!/usr/bin/env python3
"""
Facebook/Instagram MCP Server - Integration with Facebook Graph API

This server exposes Facebook Page and Instagram Business posting capabilities
to Qwen Code via the Model Context Protocol (MCP).
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent.parent.parent / '.env')

# Configuration
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
INSTAGRAM_ACCOUNT_ID = os.getenv('INSTAGRAM_ACCOUNT_ID')
FACEBOOK_API_VERSION = 'v19.0'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('facebook_mcp')

class FacebookClient:
    """Client for interacting with Facebook Graph API"""
    
    def __init__(self):
        self.base_url = f'https://graph.facebook.com/{FACEBOOK_API_VERSION}'
        self.page_id = FACEBOOK_PAGE_ID
        self.access_token = FACEBOOK_ACCESS_TOKEN
        self.instagram_id = INSTAGRAM_ACCOUNT_ID
        
        if not self.access_token:
            raise Exception('FACEBOOK_ACCESS_TOKEN not set in .env')
    
    def _make_request(self, endpoint, method='GET', params=None):
        """Make authenticated request to Graph API"""
        url = f'{self.base_url}/{endpoint}'
        
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, params=params, timeout=30)
            else:
                raise ValueError(f'Unsupported method: {method}')
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f'API request failed: {e}')
            raise
    
    def create_post(self, message, link=None, photo_url=None):
        """Create a post on Facebook Page"""
        try:
            params = {
                'message': message
            }
            
            if link:
                params['link'] = link
            
            if photo_url:
                params['url'] = photo_url
                endpoint = f'{self.page_id}/photos'
            else:
                endpoint = f'{self.page_id}/feed'
            
            result = self._make_request(endpoint, method='POST', params=params)
            
            return {
                'success': True,
                'post_id': result.get('id'),
                'permalink': f'https://facebook.com/{self.page_id}/posts/{result.get("id", "").split("_")[-1]}'
            }
            
        except Exception as e:
            logger.error(f'Error creating Facebook post: {e}')
            return {'success': False, 'error': str(e)}
    
    def get_posts(self, limit=10):
        """Get recent posts from Page"""
        try:
            params = {
                'fields': 'id,message,created_time,likes.summary(true),comments.summary(true),shares',
                'limit': limit
            }
            
            result = self._make_request(f'{self.page_id}/posts', params=params)
            
            posts = result.get('data', [])
            return {
                'success': True,
                'posts': posts,
                'count': len(posts)
            }
            
        except Exception as e:
            logger.error(f'Error getting Facebook posts: {e}')
            return {'success': False, 'error': str(e)}
    
    def get_insights(self, post_id=None, period='week'):
        """Get engagement metrics"""
        try:
            if post_id:
                # Get insights for specific post
                params = {
                    'metric': 'post_impressions,post_engagements,post_clicks',
                    'period': 'lifetime'
                }
                result = self._make_request(f'{post_id}/insights', params=params)
                
                return {
                    'success': True,
                    'post_id': post_id,
                    'insights': result.get('data', [])
                }
            else:
                # Get page insights
                from datetime import datetime, timedelta
                
                if period == 'week':
                    since = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                elif period == 'month':
                    since = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                else:
                    since = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                
                params = {
                    'metric': 'page_impressions,page_engaged_users,page_posts_impressions',
                    'period': 'day',
                    'since': since,
                    'until': datetime.now().strftime('%Y-%m-%d')
                }
                
                result = self._make_request(f'{self.page_id}/insights', params=params)
                
                return {
                    'success': True,
                    'period': {'from': since, 'to': datetime.now().strftime('%Y-%m-%d')},
                    'insights': result.get('data', [])
                }
                
        except Exception as e:
            logger.error(f'Error getting insights: {e}')
            return {'success': False, 'error': str(e)}
    
    def get_summary(self, date_from=None, date_to=None):
        """Get Page summary for reports"""
        try:
            from datetime import datetime, timedelta
            
            if not date_from:
                date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            if not date_to:
                date_to = datetime.now().strftime('%Y-%m-%d')
            
            # Get posts in period
            params = {
                'fields': 'id,message,created_time,likes.summary(true),comments.summary(true),shares',
                'since': date_from,
                'until': date_to,
                'limit': 100
            }
            
            result = self._make_request(f'{self.page_id}/posts', params=params)
            posts = result.get('data', [])
            
            # Calculate metrics
            total_likes = sum(
                post.get('likes', {}).get('summary', {}).get('total_count', 0)
                for post in posts
            )
            total_comments = sum(
                post.get('comments', {}).get('summary', {}).get('total_count', 0)
                for post in posts
            )
            total_shares = sum(
                post.get('shares', {}).get('count', 0)
                for post in posts
            )
            
            # Find top post
            top_post = None
            max_engagement = 0
            for post in posts:
                engagement = (
                    post.get('likes', {}).get('summary', {}).get('total_count', 0) +
                    post.get('comments', {}).get('summary', {}).get('total_count', 0) +
                    post.get('shares', {}).get('count', 0)
                )
                if engagement > max_engagement:
                    max_engagement = engagement
                    top_post = {
                        'id': post.get('id'),
                        'message': post.get('message', '')[:100],
                        'likes': post.get('likes', {}).get('summary', {}).get('total_count', 0),
                        'comments': post.get('comments', {}).get('summary', {}).get('total_count', 0),
                        'shares': post.get('shares', {}).get('count', 0)
                    }
            
            return {
                'success': True,
                'period': {'from': date_from, 'to': date_to},
                'posts_count': len(posts),
                'total_likes': total_likes,
                'total_comments': total_comments,
                'total_shares': total_shares,
                'total_engagement': total_likes + total_comments + total_shares,
                'top_post': top_post
            }
            
        except Exception as e:
            logger.error(f'Error getting summary: {e}')
            return {'success': False, 'error': str(e)}
    
    def instagram_create_post(self, caption, image_url):
        """Create a post on Instagram Business"""
        try:
            # Step 1: Create media container
            params = {
                'image_url': image_url,
                'caption': caption
            }
            
            result = self._make_request(
                f'{self.instagram_id}/media',
                method='POST',
                params=params
            )
            
            container_id = result.get('id')
            
            # Step 2: Publish container
            publish_params = {
                'creation_id': container_id
            }
            
            publish_result = self._make_request(
                f'{self.instagram_id}/media_publish',
                method='POST',
                params=publish_result
            )
            
            return {
                'success': True,
                'post_id': publish_result.get('id'),
                'status': 'published'
            }
            
        except Exception as e:
            logger.error(f'Error creating Instagram post: {e}')
            return {'success': False, 'error': str(e)}
    
    def instagram_create_reel(self, caption, video_url):
        """Create a reel on Instagram"""
        try:
            # Step 1: Create video container
            params = {
                'video_url': video_url,
                'caption': caption,
                'media_type': 'REELS'
            }
            
            result = self._make_request(
                f'{self.instagram_id}/media',
                method='POST',
                params=params
            )
            
            container_id = result.get('id')
            
            # Step 2: Publish container
            publish_params = {
                'creation_id': container_id
            }
            
            publish_result = self._make_request(
                f'{self.instagram_id}/media_publish',
                method='POST',
                params=publish_params
            )
            
            return {
                'success': True,
                'post_id': publish_result.get('id'),
                'status': 'published',
                'type': 'reel'
            }
            
        except Exception as e:
            logger.error(f'Error creating Instagram reel: {e}')
            return {'success': False, 'error': str(e)}
    
    def instagram_get_posts(self, limit=10):
        """Get recent Instagram posts"""
        try:
            params = {
                'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
                'limit': limit
            }
            
            result = self._make_request(f'{self.instagram_id}/media', params=params)
            
            posts = result.get('data', [])
            return {
                'success': True,
                'posts': posts,
                'count': len(posts)
            }
            
        except Exception as e:
            logger.error(f'Error getting Instagram posts: {e}')
            return {'success': False, 'error': str(e)}


class FacebookMCPServer:
    """HTTP server for MCP integration"""
    
    facebook_client = None
    
    @classmethod
    def initialize(cls):
        """Initialize Facebook client"""
        cls.facebook_client = FacebookClient()
        logger.info('Facebook client initialized')


def handle_request(request_data):
    """Handle MCP tool call"""
    if not FacebookMCPServer.facebook_client:
        return {'success': False, 'error': 'Facebook client not initialized'}
    
    tool_name = request_data.get('tool')
    params = request_data.get('params', {})
    
    logger.info(f'Tool call: {tool_name}')
    
    client = FacebookMCPServer.facebook_client
    
    try:
        # Facebook tools
        if tool_name == 'facebook_create_post':
            return client.create_post(**params)
        elif tool_name == 'facebook_get_posts':
            return client.get_posts(**params)
        elif tool_name == 'facebook_get_insights':
            return client.get_insights(**params)
        elif tool_name == 'facebook_get_summary':
            return client.get_summary(**params)
        
        # Instagram tools
        elif tool_name == 'instagram_create_post':
            return client.instagram_create_post(**params)
        elif tool_name == 'instagram_create_reel':
            return client.instagram_create_reel(**params)
        elif tool_name == 'instagram_get_posts':
            return client.instagram_get_posts(**params)
        
        else:
            return {'success': False, 'error': f'Unknown tool: {tool_name}'}
            
    except Exception as e:
        logger.error(f'Error in {tool_name}: {e}')
        return {'success': False, 'error': str(e)}


def main():
    """Start the MCP server"""
    import argparse
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse
    
    parser = argparse.ArgumentParser(description='Facebook/Instagram MCP Server')
    parser.add_argument('--port', type=int, default=8811,
                       help='Port to listen on (default: 8811)')
    parser.add_argument('--host', default='localhost',
                       help='Host to bind to (default: localhost)')
    args = parser.parse_args()
    
    try:
        # Initialize Facebook client
        FacebookMCPServer.initialize()
        
        # Define request handler
        class RequestHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    request = json.loads(post_data.decode('utf-8'))
                    
                    result = handle_request(request)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode('utf-8'))
                    
                except Exception as e:
                    logger.error(f'Error handling request: {e}')
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'error': str(e)
                    }).encode('utf-8'))
            
            def do_GET(self):
                parsed_path = urlparse(self.path)
                
                if parsed_path.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'status': 'healthy',
                        'page_id': FACEBOOK_PAGE_ID,
                        'instagram_id': INSTAGRAM_ACCOUNT_ID,
                        'timestamp': datetime.now().isoformat()
                    }).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                logger.info(f'{args}')
        
        # Start HTTP server
        server = HTTPServer((args.host, args.port), RequestHandler)
        logger.info(f'Facebook/Instagram MCP Server starting on {args.host}:{args.port}')
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info('Shutting down server...')
            server.shutdown()
            
    except Exception as e:
        logger.error(f'Failed to start server: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
