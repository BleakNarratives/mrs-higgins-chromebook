#!/bin/bash
# =============================================================================
# DEPLOY_ALL_SAAS.sh - Autonomous SaaS Package Deployment
# =============================================================================
#
# This script deploys ALL SaaS packages in the saas_packages/ directory
# to the Mrs Higgins SaaS platform. It runs automatically when new packages
# are added or existing ones are modified.
#
# USAGE:
#   ./DEPLOY_ALL_SAAS.sh                    # Deploy all packages
#   ./DEPLOY_ALL_SAAS.sh --watch             # Watch for changes and auto-deploy
#   ./DEPLOY_ALL_SAAS.sh --test              # Test deployment without actually deploying
#   ./DEPLOY_ALL_SAAS.sh package_name.json  # Deploy single package
#
# REQUIREMENTS:
#   - Python 3.10+
#   - front_desk_lady.py (Mrs Higgins router)
#   - Lightning wallet configured
#   - Nostr keys available
#
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAAS_PACKAGES_DIR="$SCRIPT_DIR/saas_packages"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/deploy_all_saas.log"
STATUS_FILE="$SCRIPT_DIR/.deploy.status"
LAST_DEPLOY_FILE="$SCRIPT_DIR/.last_deploy"

# Mrs Higgins
FRONT_DESK_LADY="$SCRIPT_DIR/front_desk_lady.py"
BOOKKEEPER="$SCRIPT_DIR/bookkeeper.py"

# Lightning config
LNBITS_URL=${LNBITS_URL:-"https://payments.voltage.cloud"}
LNBITS_INVOICE_KEY=${LNBITS_INVOICE_KEY:-""}
LIGHTNING_ACCOUNT=${LIGHTNING_ACCOUNT:-"bleaknarratives@speed.app"}

# =============================================================================
# LOGGING & TRACKING
# =============================================================================

log() {
    local msg="$1"
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo "[$timestamp] $msg" | tee -a "$LOG_FILE"
}

log_error() {
    local msg="$1"
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo "[$timestamp] [ERROR] $msg" | tee -a "$LOG_FILE" >&2
}

track_deployment() {
    local package="$1"
    local status="$2"
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    echo "{" >> "$SCRIPT_DIR/.deploy_events.log"
    echo "  \"timestamp\": \"$timestamp\"," >> "$SCRIPT_DIR/.deploy_events.log"
    echo "  \"package\": \"$package\"," >> "$SCRIPT_DIR/.deploy_events.log"
    echo "  \"status\": \"$status\"" >> "$SCRIPT_DIR/.deploy_events.log"
    echo "}" >> "$SCRIPT_DIR/.deploy_events.log"
}

# =============================================================================
# DIRECTORY SETUP
# =============================================================================

setup_directories() {
    mkdir -p "$LOG_DIR"
    mkdir -p "$SAAS_PACKAGES_DIR"
    touch "$STATUS_FILE"
    touch "$LAST_DEPLOY_FILE"
    touch "$SCRIPT_DIR/.deploy_events.log"
}

# =============================================================================
# VALIDATION
# =============================================================================

validate_package() {
    local package_file="$1"
    local package_name="$(basename "$package_file")"
    
    # Check file exists
    if [ ! -f "$package_file" ]; then
        log_error "Package file not found: $package_file"
        return 1
    fi
    
    # Check valid JSON
    if ! python3 -m json.tool "$package_file" > /dev/null 2>&1; then
        log_error "Invalid JSON in: $package_name"
        return 1
    fi
    
    # Check required fields
    local name=$(python3 -c "import json; print(json.load(open('$package_file'))['name'])" 2>/dev/null)
    local price_sats=$(python3 -c "import json; print(json.load(open('$package_file'))['price_sats'])" 2>/dev/null)
    
    if [ -z "$name" ] || [ -z "$price_sats" ]; then
        log_error "Missing required fields in: $package_name"
        return 1
    fi
    
    log " $package_name validated"
    return 0
}

# =============================================================================
# DEPLOY SINGLE PACKAGE
# =============================================================================

deploy_package() {
    local package_file="$1"
    local package_name="$(basename "$package_file")"
    
    log "Deploying: $package_name..."
    
    # Validate
    if ! validate_package "$package_file"; then
        track_deployment "$package_name" "validation_failed"
        return 1
    fi
    
    # Extract package data
    local name=$(python3 -c "import json; print(json.load(open('$package_file'))['name'])")
    local tagline=$(python3 -c "import json; print(json.load(open('$package_file'))['tagline'])")
    local price_sats=$(python3 -c "import json; print(json.load(open('$package_file'))['price_sats'])")
    local url=$(python3 -c "import json; print(json.load(open('$package_file'))['url'])" 2>/dev/null || echo "")
    
    # Create routing entry for Mrs Higgins
    # Mrs Higgins front_desk_lady.py loads packages from saas_packages/
    # So just placing the JSON file there is enough for deployment
    
    # Verify it's in the right place
    if [ "$(dirname "$package_file")" != "$SAAS_PACKAGES_DIR" ]; then
        # Copy to saas_packages if not already there
        cp "$package_file" "$SAAS_PACKAGES_DIR/"
        package_file="$SAAS_PACKAGES_DIR/$package_name"
        log "  Copied to: $package_file"
    fi
    
    # Register with front_desk_lady
    log "  Registering with Mrs Higgins..."
    
    # Update front_desk_routing_log.json
    python3 << PYEOF
import json
from pathlib import Path

routing_log = Path("$SCRIPT_DIR/front_desk_routing_log.json")

# Load existing log
if routing_log.exists():
    with open(routing_log) as f:
        log_data = json.load(f)
else:
    log_data = {"packages": [], "total_routed": 0}

# Add new package entry
new_entry = {
    "package_name": "$name",
    "file": "$package_name",
    "price_sats": $price_sats,
    "tagline": "$tagline",
    "status": "ROUTED",
    "platforms": ["Fiverr", "Upwork", "Nostr", "Direct"],
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "source": "auto_deploy"
}

log_data["packages"].append(new_entry)
log_data["total_routed"] = len(log_data["packages"])

with open(routing_log, 'w') as f:
    json.dump(log_data, f, indent=2)

print(f"  Registered {name} in routing log")
PYEOF
    
    # Trigger front_desk_lady to process new package
    log "  Triggering front_desk_lady..."
    nohup python3 "$FRONT_DESK_LADY" --process-new >> "$LOG_DIR/front_desk.log" 2>&1 &
    
    track_deployment "$package_name" "deployed"
    log " $package_name deployed successfully!"
    
    return 0
}

# =============================================================================
# DEPLOY ALL PACKAGES
# =============================================================================

deploy_all_packages() {
    log "=========================================="
    log "DEPLOYING ALL SAAS PACKAGES"
    log "=========================================="
    
    local deployed=0
    local failed=0
    
    for package_file in "$SAAS_PACKAGES_DIR"/*.json; do
        if [ -f "$package_file" ]; then
            if deploy_package "$package_file"; then
                deployed=$((deployed + 1))
            else
                failed=$((failed + 1))
            fi
        fi
    done
    
    log ""
    log "Deployment Summary:"
    log "  Deployed: $deployed"
    log "  Failed: $failed"
    log "  Total packages: $(ls "$SAAS_PACKAGES_DIR"/*.json 2>/dev/null | wc -l)"
    
    # Update status
    echo "last_deploy=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" > "$STATUS_FILE"
    echo "deployed=$deployed" >> "$STATUS_FILE"
    echo "failed=$failed" >> "$STATUS_FILE"
    
    # Update last deploy timestamp
    date -u +"%Y-%m-%dT%H:%M:%SZ" > "$LAST_DEPLOY_FILE"
    
    if [ $failed -eq 0 ]; then
        log " All packages deployed successfully!"
        return 0
    else
        log_error " $failed packages failed to deploy"
        return 1
    fi
}

# =============================================================================
# WATCH MODE
# =============================================================================

watch_mode() {
    log "=========================================="
    log "WATCH MODE: Monitoring for changes..."
    log "=========================================="
    log "Press Ctrl+C to stop"
    log ""
    
    # Initial deployment
    deploy_all_packages
    
    # Watch for changes
    local last_count=$(ls "$SAAS_PACKAGES_DIR"/*.json 2>/dev/null | wc -l)
    
    while true; do
        local current_count=$(ls "$SAAS_PACKAGES_DIR"/*.json 2>/dev/null | wc -l)
        
        if [ $current_count -gt $last_count ]; then
            # New packages added
            log "Detected new packages!"
            deploy_all_packages
            last_count=$current_count
        else
            # Check for modified packages
            local modified=0
            for package_file in "$SAAS_PACKAGES_DIR"/*.json; do
                if [ -f "$package_file" ]; then
                    local mtime=$(stat -c %Y "$package_file" 2>/dev/null || echo 0)
                    local last_deploy=$(cat "$LAST_DEPLOY_FILE" 2>/dev/null || echo 0)
                    local last_deploy_ts=$(date -d "$last_deploy" +%s 2>/dev/null || echo 0)
                    
                    if [ $mtime -gt $last_deploy_ts ]; then
                        log "Modified package detected: $(basename "$package_file")"
                        deploy_package "$package_file"
                        modified=$((modified + 1))
                    fi
                fi
            done
            
            if [ $modified -gt 0 ]; then
                deploy_all_packages
                last_count=$current_count
            fi
        fi
        
        sleep 30
    done
}

# =============================================================================
# STATUS CHECK
# =============================================================================

check_status() {
    log "Checking deployment status..."
    
    if [ ! -f "$STATUS_FILE" ]; then
        echo "No deployments yet"
        return 1
    fi
    
    echo "Deployment Status:"
    cat "$STATUS_FILE"
    echo ""
    
    echo "Last Deployment:"
    cat "$LAST_DEPLOY_FILE" 2>/dev/null || echo "Never"
    echo ""
    
    echo "Deployed Packages:"
    python3 << PYEOF
import json
from pathlib import Path

routing_log = Path("$SCRIPT_DIR/front_desk_routing_log.json")
if routing_log.exists():
    with open(routing_log) as f:
        data = json.load(f)
    
    for pkg in data.get("packages", []):
        status = pkg.get("status", "UNKNOWN")
        name = pkg.get("package_name", "UNKNOWN")
        price = pkg.get("price_sats", 0)
        print(f"  - {name}: {status} ({price} sats)")
    
    print(f"\nTotal: {data.get('total_routed', 0)} packages")
else:
    print("  No routing log found")
PYEOF
}

# =============================================================================
# REVENUE TRACKING
# =============================================================================

start_revenue_monitor() {
    log "Starting revenue monitor..."
    
    # This would integrate with the existing bookkeeper.py
    # For now, just ensure it's running
    if ! pgrep -f "python3.*bookkeeper.py" > /dev/null 2>&1; then
        nohup python3 "$BOOKKEEPER" >> "$LOG_DIR/bookkeeper.log" 2>&1 &
        log "Bookkeeper started"
    else
        log "Bookkeeper already running"
    fi
}

# =============================================================================
# MAIN
# =============================================================================

# Parse arguments
setup_directories

ACTION="deploy_all"
for arg in "$@"; do
    case "$arg" in
        --watch|-w)
            ACTION="watch"
            ;;
        --test|-t)
            ACTION="test"
            ;;
        --status|-s)
            ACTION="status"
            ;;
        --revenue-monitor)
            ACTION="revenue_monitor"
            ;;
        *)
            if [ -f "$arg" ]; then
                ACTION="deploy_single"
                TARGET="$arg"
            fi
            ;;
    esac
done

# Execute action
case "$ACTION" in
    deploy_all)
        deploy_all_packages
        ;;
    deploy_single)
        deploy_package "$TARGET"
        ;;
    watch)
        watch_mode
        ;;
    test)
        log "TEST MODE: Validating all packages without deploying..."
        for package_file in "$SAAS_PACKAGES_DIR"/*.json; do
            if [ -f "$package_file" ]; then
                validate_package "$package_file" && echo "  PASS" || echo "  FAIL"
            fi
        done
        ;;
    status)
        check_status
        ;;
    revenue_monitor)
        start_revenue_monitor
        ;;
    *)
        echo "Unknown action: $ACTION"
        echo "Usage: $0 [--watch|--test|--status|package.json]"
        exit 1
        ;;
esac

exit 0
