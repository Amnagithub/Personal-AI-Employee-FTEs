#!/bin/bash
# Master Email Processing Script - Watches, Processes, and Sends Emails
# 
# This script:
# 1. Starts Gmail Watcher (monitors for new emails)
# 2. Starts Email Auto-Processor (processes and replies)
# 3. Optionally starts Email MCP server (for sending)
#
# Usage:
#   bash run_email_system.sh              # Interactive mode
#   bash run_email_system.sh --daemon     # Background mode
#   bash run_email_system.sh --help       # Show help

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_PATH="$SCRIPT_DIR"
LOG_DIR="$VAULT_PATH/logs"
CHECK_INTERVAL=120  # Check for new emails every 2 minutes
PROCESS_INTERVAL=60  # Process emails every 1 minute

# Create log directory
mkdir -p "$LOG_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "============================================================"
    echo "  AI Employee - Autonomous Email Processing System"
    echo "============================================================"
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON=python3
    elif command -v python &> /dev/null; then
        PYTHON=python
    else
        print_error "Python not found! Please install Python 3.8+"
        exit 1
    fi
    print_status "Python found: $PYTHON"
}

check_mcp_server() {
    if curl -s http://localhost:8809/tools/list &> /dev/null; then
        print_status "Email MCP server is running on port 8809"
        return 0
    else
        print_warning "Email MCP server is NOT running"
        echo ""
        echo "To start the MCP server:"
        echo "  1. Set up Gmail API credentials:"
        echo "     - Go to https://console.cloud.google.com/"
        echo "     - Enable Gmail API"
        echo "     - Create OAuth 2.0 credentials"
        echo "     - Download credentials.json to ~/.ai_employee/gmail_credentials.json"
        echo ""
        echo "  2. Start the server:"
        echo "     bash .qwen/skills/email-mcp/scripts/start-server.sh"
        echo ""
        print_warning "Emails will be saved as drafts for manual sending until MCP is running"
        return 1
    fi
}

start_mcp_server() {
    local mcp_script="$SCRIPT_DIR/.qwen/skills/email-mcp/scripts/start-server.sh"
    if [ -f "$mcp_script" ]; then
        print_info "Starting Email MCP server..."
        bash "$mcp_script" &
        sleep 3
        check_mcp_server
    else
        print_warning "MCP start script not found at: $mcp_script"
    fi
}

start_watcher() {
    local watcher_script="$VAULT_PATH/scripts/watchers/gmail_watcher.py"
    if [ -f "$watcher_script" ]; then
        print_info "Starting Gmail Watcher (check interval: ${CHECK_INTERVAL}s)..."
        if [ "$DAEMON_MODE" = true ]; then
            $PYTHON "$watcher_script" "$VAULT_PATH" --interval $CHECK_INTERVAL \
                >> "$LOG_DIR/gmail_watcher.log" 2>&1 &
            WATCHER_PID=$!
            print_status "Gmail Watcher started (PID: $WATCHER_PID)"
            echo $WATCHER_PID > "$LOG_DIR/gmail_watcher.pid"
        else
            $PYTHON "$watcher_script" "$VAULT_PATH" --interval $CHECK_INTERVAL --verbose &
            WATCHER_PID=$!
            print_status "Gmail Watcher started (PID: $WATCHER_PID)"
        fi
    else
        print_error "Gmail Watcher script not found!"
        return 1
    fi
}

start_processor() {
    local processor_script="$VAULT_PATH/scripts/email_auto_processor.py"
    if [ -f "$processor_script" ]; then
        print_info "Starting Email Auto-Processor (check interval: ${PROCESS_INTERVAL}s)..."
        if [ "$DAEMON_MODE" = true ]; then
            $PYTHON "$processor_script" "$VAULT_PATH" --loop --loop-interval $PROCESS_INTERVAL --auto-send --use-qwen \
                >> "$LOG_DIR/email_processor.log" 2>&1 &
            PROCESSOR_PID=$!
            print_status "Email Auto-Processor started (PID: $PROCESSOR_PID)"
            echo $PROCESSOR_PID > "$LOG_DIR/email_processor.pid"
        else
            $PYTHON "$processor_script" "$VAULT_PATH" --loop --loop-interval $PROCESS_INTERVAL --auto-send --use-qwen --verbose &
            PROCESSOR_PID=$!
            print_status "Email Auto-Processor started (PID: $PROCESSOR_PID)"
        fi
    else
        print_error "Email Auto-Processor script not found!"
        return 1
    fi
}

stop_all() {
    print_info "Stopping all services..."
    
    # Stop Gmail Watcher
    if [ -f "$LOG_DIR/gmail_watcher.pid" ]; then
        local pid=$(cat "$LOG_DIR/gmail_watcher.pid")
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_status "Gmail Watcher stopped (PID: $pid)"
        fi
        rm -f "$LOG_DIR/gmail_watcher.pid"
    fi
    
    # Stop Email Auto-Processor
    if [ -f "$LOG_DIR/email_processor.pid" ]; then
        local pid=$(cat "$LOG_DIR/email_processor.pid")
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_status "Email Auto-Processor stopped (PID: $pid)"
        fi
        rm -f "$LOG_DIR/email_processor.pid"
    fi
    
    print_status "All services stopped"
}

cleanup() {
    echo ""
    print_info "Received shutdown signal"
    stop_all
    exit 0
}

show_status() {
    echo ""
    echo "============================================================"
    echo "  System Status"
    echo "============================================================"
    echo ""
    
    # Check Gmail Watcher
    if [ -f "$LOG_DIR/gmail_watcher.pid" ]; then
        local pid=$(cat "$LOG_DIR/gmail_watcher.pid")
        if kill -0 $pid 2>/dev/null; then
            print_status "Gmail Watcher: Running (PID: $pid)"
        else
            print_error "Gmail Watcher: Not running (stale PID)"
        fi
    else
        print_warning "Gmail Watcher: Not running"
    fi
    
    # Check Email Auto-Processor
    if [ -f "$LOG_DIR/email_processor.pid" ]; then
        local pid=$(cat "$LOG_DIR/email_processor.pid")
        if kill -0 $pid 2>/dev/null; then
            print_status "Email Auto-Processor: Running (PID: $pid)"
        else
            print_error "Email Auto-Processor: Not running (stale PID)"
        fi
    else
        print_warning "Email Auto-Processor: Not running"
    fi
    
    # Check MCP Server
    if curl -s http://localhost:8809/tools/list &> /dev/null; then
        print_status "Email MCP Server: Running (port 8809)"
    else
        print_warning "Email MCP Server: Not running"
    fi
    
    # Check pending emails
    local pending=$(ls "$VAULT_PATH/Needs_Action/EMAIL_"*.md 2>/dev/null | wc -l)
    echo ""
    print_info "Pending emails in Needs_Action: $pending"
    
    # Check pending approvals
    local approvals=$(ls "$VAULT_PATH/Pending_Approval/"*.md 2>/dev/null | wc -l)
    print_info "Pending approvals: $approvals"
    
    echo ""
}

show_logs() {
    echo ""
    echo "============================================================"
    echo "  Recent Logs"
    echo "============================================================"
    echo ""
    
    if [ -f "$LOG_DIR/gmail_watcher.log" ]; then
        echo "--- Gmail Watcher Log (last 20 lines) ---"
        tail -n 20 "$LOG_DIR/gmail_watcher.log"
        echo ""
    fi
    
    if [ -f "$LOG_DIR/email_processor.log" ]; then
        echo "--- Email Processor Log (last 20 lines) ---"
        tail -n 20 "$LOG_DIR/email_processor.log"
        echo ""
    fi
}

# Parse arguments
DAEMON_MODE=false
ACTION="start"

while [[ $# -gt 0 ]]; do
    case $1 in
        --daemon)
            DAEMON_MODE=true
            shift
            ;;
        --stop)
            ACTION="stop"
            shift
            ;;
        --status)
            ACTION="status"
            shift
            ;;
        --logs)
            ACTION="logs"
            shift
            ;;
        --help|-h)
            ACTION="help"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            ACTION="help"
            shift
            ;;
    esac
done

# Main execution
case $ACTION in
    start)
        print_header
        check_python
        check_mcp_server || true  # Continue even if MCP not running
        
        # Set up signal handlers
        trap cleanup SIGINT SIGTERM
        
        # Start services
        start_watcher
        start_processor
        
        echo ""
        print_status "============================================================"
        print_status "All services started successfully!"
        print_status "============================================================"
        echo ""
        print_info "Gmail Watcher: Checking every ${CHECK_INTERVAL}s"
        print_info "Email Processor: Checking every ${PROCESS_INTERVAL}s"
        echo ""
        print_info "Press Ctrl+C to stop all services"
        echo ""
        
        # Wait for background processes
        wait
        ;;
    stop)
        stop_all
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help)
        print_header
        echo "Usage: bash run_email_system.sh [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --daemon      Run in background mode (logs to files)"
        echo "  --stop        Stop all services"
        echo "  --status      Show service status"
        echo "  --logs        Show recent logs"
        echo "  --help, -h    Show this help message"
        echo ""
        echo "Examples:"
        echo "  # Run interactively (foreground)"
        echo "  bash run_email_system.sh"
        echo ""
        echo "  # Run in background"
        echo "  bash run_email_system.sh --daemon"
        echo ""
        echo "  # Check status"
        echo "  bash run_email_system.sh --status"
        echo ""
        echo "  # View logs"
        echo "  bash run_email_system.sh --logs"
        echo ""
        echo "  # Stop all services"
        echo "  bash run_email_system.sh --stop"
        ;;
esac
