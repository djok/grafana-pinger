#!/usr/bin/env python3
"""
Host Management API for Prometheus Blackbox Exporter
Provides REST API for adding/removing monitoring targets
Uses file-based service discovery
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
TARGETS_DIR = os.environ.get('TARGETS_DIR', '/targets')
TARGETS_FILE = os.path.join(TARGETS_DIR, 'hosts.json')

# Ensure targets directory exists
os.makedirs(TARGETS_DIR, exist_ok=True)


def load_hosts() -> List[Dict]:
    """Load hosts from JSON file"""
    if not os.path.exists(TARGETS_FILE):
        return []

    try:
        with open(TARGETS_FILE, 'r') as f:
            data = json.load(f)
            # Check if data is already in our internal format or Prometheus format
            if isinstance(data, list):
                # It's in Prometheus file_sd format, convert it
                return convert_from_prometheus_format(data)
            else:
                # Legacy format or error
                return data.get('hosts', [])
    except Exception as e:
        app.logger.error(f"Error loading hosts: {e}")
        return []


def save_hosts(hosts: List[Dict]) -> bool:
    """Save hosts to JSON file in Prometheus file_sd format"""
    try:
        # Convert to Prometheus file_sd format
        targets = []
        for host in hosts:
            targets.append({
                "targets": [host['target']],
                "labels": {
                    "id": host['id'],
                    "name": host['name'],
                    "group": host['group'],
                    "created": host['created']
                }
            })

        # Write to file
        with open(TARGETS_FILE, 'w') as f:
            json.dump(targets, f, indent=2)

        app.logger.info(f"Saved {len(hosts)} hosts to {TARGETS_FILE}")
        return True
    except Exception as e:
        app.logger.error(f"Error saving hosts: {e}")
        return False


def convert_from_prometheus_format(prom_data: List[Dict]) -> List[Dict]:
    """Convert Prometheus file_sd format to our internal format"""
    hosts = []
    for item in prom_data:
        if 'targets' in item and item['targets']:
            labels = item.get('labels', {})
            hosts.append({
                'id': labels.get('id', str(uuid.uuid4())),
                'target': item['targets'][0],
                'name': labels.get('name', item['targets'][0]),
                'group': labels.get('group', 'default'),
                'created': labels.get('created', datetime.utcnow().isoformat())
            })
    return hosts


@app.route('/')
def index():
    """Serve the main UI"""
    return send_from_directory('static', 'index.html')


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'targets_file': TARGETS_FILE,
        'targets_dir': TARGETS_DIR
    })


@app.route('/api/hosts', methods=['GET'])
def get_hosts():
    """Get all monitored hosts"""
    hosts = load_hosts()
    return jsonify({
        'success': True,
        'count': len(hosts),
        'hosts': hosts
    })


@app.route('/api/hosts', methods=['POST'])
def add_host():
    """Add a new host to monitoring"""
    data = request.get_json()

    # Validate input
    if not data or 'target' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required field: target'
        }), 400

    target = data['target'].strip()
    name = data.get('name', target).strip()
    group = data.get('group', 'default').strip()

    if not target:
        return jsonify({
            'success': False,
            'error': 'Target cannot be empty'
        }), 400

    # Load existing hosts
    hosts = load_hosts()

    # Check for duplicates
    for host in hosts:
        if host['target'] == target:
            return jsonify({
                'success': False,
                'error': f'Host {target} already exists'
            }), 409

    # Create new host
    new_host = {
        'id': str(uuid.uuid4()),
        'target': target,
        'name': name,
        'group': group,
        'created': datetime.utcnow().isoformat()
    }

    hosts.append(new_host)

    # Save to file
    if save_hosts(hosts):
        return jsonify({
            'success': True,
            'host': new_host
        }), 201
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to save host'
        }), 500


@app.route('/api/hosts/<host_id>', methods=['DELETE'])
def delete_host(host_id):
    """Delete a host from monitoring"""
    hosts = load_hosts()

    # Find and remove host
    original_count = len(hosts)
    hosts = [h for h in hosts if h['id'] != host_id]

    if len(hosts) == original_count:
        return jsonify({
            'success': False,
            'error': 'Host not found'
        }), 404

    # Save to file
    if save_hosts(hosts):
        return jsonify({
            'success': True,
            'message': 'Host deleted successfully'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to delete host'
        }), 500


@app.route('/api/hosts/<host_id>', methods=['PUT'])
def update_host(host_id):
    """Update a host"""
    data = request.get_json()
    hosts = load_hosts()

    # Find host
    host_index = None
    for i, h in enumerate(hosts):
        if h['id'] == host_id:
            host_index = i
            break

    if host_index is None:
        return jsonify({
            'success': False,
            'error': 'Host not found'
        }), 404

    # Update fields
    if 'name' in data:
        hosts[host_index]['name'] = data['name'].strip()
    if 'group' in data:
        hosts[host_index]['group'] = data['group'].strip()
    if 'target' in data:
        hosts[host_index]['target'] = data['target'].strip()

    # Save to file
    if save_hosts(hosts):
        return jsonify({
            'success': True,
            'host': hosts[host_index]
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to update host'
        }), 500


@app.route('/api/hosts/bulk', methods=['POST'])
def bulk_add_hosts():
    """Bulk add hosts from JSON array"""
    data = request.get_json()

    if not data or 'hosts' not in data or not isinstance(data['hosts'], list):
        return jsonify({
            'success': False,
            'error': 'Invalid request format. Expected: {"hosts": [...]}'
        }), 400

    hosts = load_hosts()
    existing_targets = {h['target'] for h in hosts}

    added = []
    skipped = []

    for item in data['hosts']:
        target = item.get('target', '').strip()
        if not target:
            skipped.append({'target': target, 'reason': 'Empty target'})
            continue

        if target in existing_targets:
            skipped.append({'target': target, 'reason': 'Already exists'})
            continue

        new_host = {
            'id': str(uuid.uuid4()),
            'target': target,
            'name': item.get('name', target).strip(),
            'group': item.get('group', 'default').strip(),
            'created': datetime.utcnow().isoformat()
        }

        hosts.append(new_host)
        existing_targets.add(target)
        added.append(new_host)

    # Save to file
    if save_hosts(hosts):
        return jsonify({
            'success': True,
            'added': len(added),
            'skipped': len(skipped),
            'hosts': added,
            'skipped_details': skipped
        }), 201
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to save hosts'
        }), 500


@app.route('/api/groups', methods=['GET'])
def get_groups():
    """Get all unique groups"""
    hosts = load_hosts()
    groups = list(set(h['group'] for h in hosts))
    groups.sort()

    return jsonify({
        'success': True,
        'groups': groups
    })


if __name__ == '__main__':
    # Initialize with empty file if doesn't exist
    if not os.path.exists(TARGETS_FILE):
        save_hosts([])
        app.logger.info(f"Initialized empty targets file: {TARGETS_FILE}")

    app.run(host='0.0.0.0', port=5000, debug=False)
