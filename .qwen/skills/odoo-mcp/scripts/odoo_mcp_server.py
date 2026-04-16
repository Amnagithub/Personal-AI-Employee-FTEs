#!/usr/bin/env python3
"""
Odoo MCP Server - Integration with Odoo Community Edition via JSON-RPC API

This server exposes Odoo's accounting and business functions to Qwen Code
via the Model Context Protocol (MCP).
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import xmlrpc.client
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent.parent.parent / '.env')

# Configuration
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'ai_employee')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'admin')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('odoo_mcp')

class OdooClient:
    """Client for interacting with Odoo via XML-RPC"""
    
    def __init__(self):
        self.url = ODOO_URL
        self.db = ODOO_DB
        self.username = ODOO_USERNAME
        self.password = ODOO_PASSWORD
        
        # XML-RPC endpoints
        common_url = f'{self.url}/xmlrpc/2/common'
        self.common = xmlrpc.client.ServerProxy(common_url)
        
        # Authenticate
        self.uid = self.common.authenticate(
            self.db, self.username, self.password, {}
        )
        if not self.uid:
            raise Exception('Failed to authenticate with Odoo')
        
        # Object endpoint
        object_url = f'{self.url}/xmlrpc/2/object'
        self.models = xmlrpc.client.ServerProxy(object_url)
        
        logger.info(f'Authenticated with Odoo as user ID: {self.uid}')
    
    def execute_kw(self, model, method, args=None, kwargs=None):
        """Execute a method on a model"""
        args = args or []
        kwargs = kwargs or {}
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )
    
    def create_invoice(self, partner_name, partner_email, invoice_lines, 
                      payment_term='30 days', currency='USD'):
        """Create a new invoice"""
        try:
            # Find or create partner
            partner = self.execute_kw(
                'res.partner', 'search_read',
                [[('email', '=', partner_email)]],
                {'fields': ['id', 'name'], 'limit': 1}
            )
            
            if not partner:
                # Create new partner
                partner_id = self.execute_kw(
                    'res.partner', 'create', [{
                        'name': partner_name,
                        'email': partner_email,
                        'customer_rank': 1
                    }]
                )
            else:
                partner_id = partner[0]['id']
            
            # Get currency
            currency_id = self.execute_kw(
                'res.currency', 'search_read',
                [[('name', '=', currency)]],
                {'fields': ['id'], 'limit': 1}
            )
            currency_id = currency_id[0]['id'] if currency_id else 1
            
            # Create invoice
            invoice_id = self.execute_kw(
                'account.move', 'create', [{
                    'move_type': 'out_invoice',
                    'partner_id': partner_id,
                    'currency_id': currency_id,
                    'invoice_line_ids': [(0, 0, line) for line in invoice_lines],
                    'invoice_payment_term_id': payment_term
                }]
            )
            
            # Get invoice number
            invoice = self.execute_kw(
                'account.move', 'read',
                [invoice_id],
                {'fields': ['name', 'amount_total', 'state']}
            )
            
            return {
                'success': True,
                'invoice_id': invoice_id,
                'invoice_number': invoice[0].get('name', 'Draft'),
                'total_amount': invoice[0].get('amount_total', 0),
                'status': invoice[0].get('state', 'draft')
            }
            
        except Exception as e:
            logger.error(f'Error creating invoice: {e}')
            return {'success': False, 'error': str(e)}
    
    def validate_invoice(self, invoice_id):
        """Validate/post an invoice"""
        try:
            self.execute_kw(
                'account.move', 'action_post',
                [[invoice_id]]
            )
            
            invoice = self.execute_kw(
                'account.move', 'read',
                [invoice_id],
                {'fields': ['name', 'amount_total', 'state']}
            )
            
            return {
                'success': True,
                'invoice_number': invoice[0].get('name'),
                'status': invoice[0].get('state'),
                'amount_total': invoice[0].get('amount_total')
            }
        except Exception as e:
            logger.error(f'Error validating invoice: {e}')
            return {'success': False, 'error': str(e)}
    
    def register_payment(self, invoice_id, amount, payment_method='bank_transfer', 
                        journal_id=1):
        """Register payment for an invoice"""
        try:
            # Create payment
            payment = self.execute_kw(
                'account.payment', 'create', [{
                    'invoice_ids': [(4, invoice_id)],
                    'amount': amount,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'journal_id': journal_id,
                    'payment_method_id': payment_method
                }]
            )
            
            # Post payment
            self.execute_kw(
                'account.payment', 'action_post',
                [[payment]]
            )
            
            return {
                'success': True,
                'payment_id': payment,
                'amount': amount,
                'invoice_id': invoice_id
            }
        except Exception as e:
            logger.error(f'Error registering payment: {e}')
            return {'success': False, 'error': str(e)}
    
    def get_partners(self, filter_type='all'):
        """List business partners"""
        try:
            domain = []
            if filter_type == 'customer':
                domain = [('customer_rank', '>', 0)]
            elif filter_type == 'vendor':
                domain = [('supplier_rank', '>', 0)]
            
            partners = self.execute_kw(
                'res.partner', 'search_read',
                [domain],
                {'fields': ['id', 'name', 'email', 'phone', 'company_name'], 
                 'limit': 100}
            )
            
            return {'success': True, 'partners': partners}
        except Exception as e:
            logger.error(f'Error getting partners: {e}')
            return {'success': False, 'error': str(e)}
    
    def get_invoices(self, status=None, date_from=None, date_to=None):
        """Retrieve invoices with filters"""
        try:
            domain = []
            if status:
                domain.append(('state', '=', status))
            if date_from:
                domain.append(('date', '>=', date_from))
            if date_to:
                domain.append(('date', '<=', date_to))
            
            invoices = self.execute_kw(
                'account.move', 'search_read',
                [domain],
                {'fields': ['id', 'name', 'partner_id', 'amount_total', 
                           'amount_residual', 'state', 'invoice_date', 
                           'invoice_date_due'],
                 'order': 'invoice_date DESC',
                 'limit': 100}
            )
            
            return {'success': True, 'invoices': invoices}
        except Exception as e:
            logger.error(f'Error getting invoices: {e}')
            return {'success': False, 'error': str(e)}
    
    def get_financial_summary(self, date_from=None, date_to=None):
        """Get accounting summary for reports"""
        try:
            from datetime import date
            if not date_from:
                date_from = date.today().replace(day=1).isoformat()
            if not date_to:
                date_to = date.today().isoformat()
            
            # Get invoices
            invoices = self.execute_kw(
                'account.move', 'search_read',
                [[('move_type', '=', 'out_invoice'), 
                  ('invoice_date', '>=', date_from),
                  ('invoice_date', '<=', date_to)]],
                {'fields': ['amount_total', 'amount_residual', 'state']}
            )
            
            # Get payments
            payments = self.execute_kw(
                'account.payment', 'search_read',
                [[('payment_type', '=', 'inbound'),
                  ('date', '>=', date_from),
                  ('date', '<=', date_to)]],
                {'fields': ['amount', 'state']}
            )
            
            total_invoiced = sum(inv['amount_total'] for inv in invoices)
            total_paid = sum(pay['amount'] for pay in payments if pay['state'] == 'posted')
            total_outstanding = total_invoiced - total_paid
            
            return {
                'success': True,
                'period': {'from': date_from, 'to': date_to},
                'total_invoiced': total_invoiced,
                'total_paid': total_paid,
                'total_outstanding': total_outstanding,
                'invoice_count': len(invoices),
                'payment_count': len(payments)
            }
        except Exception as e:
            logger.error(f'Error getting financial summary: {e}')
            return {'success': False, 'error': str(e)}
    
    def create_contact(self, name, email, phone=None, company=None, type='customer'):
        """Create a new business contact"""
        try:
            contact_id = self.execute_kw(
                'res.partner', 'create', [{
                    'name': name,
                    'email': email,
                    'phone': phone or '',
                    'company_name': company or '',
                    'customer_rank': 1 if type == 'customer' else 0,
                    'supplier_rank': 1 if type == 'vendor' else 0
                }]
            )
            
            return {
                'success': True,
                'contact_id': contact_id,
                'name': name,
                'email': email
            }
        except Exception as e:
            logger.error(f'Error creating contact: {e}')
            return {'success': False, 'error': str(e)}


class OdooMCPServer(BaseHTTPRequestHandler):
    """HTTP server for MCP integration"""
    
    odoo_client = None
    
    def do_POST(self):
        """Handle MCP tool calls"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data.decode('utf-8'))
            
            tool_name = request.get('tool')
            params = request.get('params', {})
            
            logger.info(f'Tool call: {tool_name}')
            
            # Route to appropriate method
            result = self.route_tool(tool_name, params)
            
            # Send response
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
    
    def route_tool(self, tool_name, params):
        """Route MCP tool call to Odoo method"""
        if not self.odoo_client:
            return {'success': False, 'error': 'Odoo client not initialized'}
        
        try:
            if tool_name == 'odoo_create_invoice':
                return self.odoo_client.create_invoice(**params)
            elif tool_name == 'odoo_validate_invoice':
                return self.odoo_client.validate_invoice(**params)
            elif tool_name == 'odoo_register_payment':
                return self.odoo_client.register_payment(**params)
            elif tool_name == 'odoo_get_partners':
                return self.odoo_client.get_partners(**params)
            elif tool_name == 'odoo_get_invoices':
                return self.odoo_client.get_invoices(**params)
            elif tool_name == 'odoo_get_financial_summary':
                return self.odoo_client.get_financial_summary(**params)
            elif tool_name == 'odoo_create_contact':
                return self.odoo_client.create_contact(**params)
            else:
                return {'success': False, 'error': f'Unknown tool: {tool_name}'}
        except Exception as e:
            logger.error(f'Error in {tool_name}: {e}')
            return {'success': False, 'error': str(e)}
    
    def do_GET(self):
        """Health check endpoint"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'healthy',
                'odoo_url': ODOO_URL,
                'odoo_db': ODOO_DB,
                'timestamp': datetime.now().isoformat()
            }).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use logger"""
        logger.info(f'{args}')


def main():
    """Start the MCP server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Odoo MCP Server')
    parser.add_argument('--port', type=int, default=8810,
                       help='Port to listen on (default: 8810)')
    parser.add_argument('--host', default='localhost',
                       help='Host to bind to (default: localhost)')
    args = parser.parse_args()
    
    try:
        # Initialize Odoo client
        OdooMCPServer.odoo_client = OdooClient()
        
        # Start HTTP server
        server = HTTPServer((args.host, args.port), OdooMCPServer)
        logger.info(f'Odoo MCP Server starting on {args.host}:{args.port}')
        
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
