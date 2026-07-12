"""
Chat routes
Handles chat messages and AI interaction
"""

from flask import Blueprint, request, jsonify, current_app, Response
import os
import json
from datetime import datetime

bp = Blueprint('chat', __name__)


def get_session_dir(project_name, session_id):
    """Get session directory path"""
    workspace_root = current_app.config['WORKSPACE_ROOT']
    return os.path.join(workspace_root, project_name, 'chat', session_id)


def load_session_messages(project_name, session_id):
    """Load all messages from session history"""
    session_dir = get_session_dir(project_name, session_id)
    history_file = os.path.join(session_dir, 'history.jsonl')
    
    messages = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))
    
    return messages


def append_message(project_name, session_id, message):
    """Append a message to session history"""
    session_dir = get_session_dir(project_name, session_id)
    history_file = os.path.join(session_dir, 'history.jsonl')
    
    # Ensure directory exists
    os.makedirs(session_dir, exist_ok=True)
    
    # Append message
    with open(history_file, 'a') as f:
        f.write(json.dumps(message) + '\n')
    
    # Update message count in session metadata
    session_meta_file = os.path.join(session_dir, 'session.json')
    if os.path.exists(session_meta_file):
        with open(session_meta_file, 'r') as f:
            session = json.load(f)
        
        session['message_count'] = session.get('message_count', 0) + 1
        session['updated_at'] = datetime.now().isoformat()
        
        with open(session_meta_file, 'w') as f:
            json.dump(session, f, indent=2)


@bp.route('/<project_name>/<session_id>/messages', methods=['GET'])
def get_messages(project_name, session_id):
    """Get all messages in a session"""
    try:
        # Verify session exists
        session_dir = get_session_dir(project_name, session_id)
        if not os.path.exists(session_dir):
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        messages = load_session_messages(project_name, session_id)
        return jsonify({
            'success': True,
            'data': messages,
            'count': len(messages)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/<session_id>/messages', methods=['POST'])
def send_message(project_name, session_id):
    """Send a message to the chat session"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'success': False, 'error': 'Message content is required'}), 400
        
        # Verify session exists
        session_dir = get_session_dir(project_name, session_id)
        if not os.path.exists(session_dir):
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Create user message
        user_message = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'role': 'user',
            'content': data['content'],
            'timestamp': datetime.now().isoformat(),
            'tokens': data.get('tokens', 0)
        }
        
        # Append user message
        append_message(project_name, session_id, user_message)
        
        # Load context for AI response
        messages = load_session_messages(project_name, session_id)
        
        # Load project constitution and session summary for context
        project_dir = os.path.join(current_app.config['WORKSPACE_ROOT'], project_name)
        project_meta_file = os.path.join(project_dir, 'project.json')
        
        constitution = {}
        if os.path.exists(project_meta_file):
            with open(project_meta_file, 'r') as f:
                project_meta = json.load(f)
                constitution = project_meta.get('constitution', {})
        
        session_summary = ''
        summary_file = os.path.join(session_dir, 'summary.md')
        if os.path.exists(summary_file):
            with open(summary_file, 'r') as f:
                session_summary = f.read()
        
        # Build prompt with context (simplified - in production this would call Claude/OpenCode)
        system_prompt = build_system_prompt(constitution, session_summary)
        
        # Generate AI response (mock for now - would integrate with Claude CLI)
        ai_response_content = generate_ai_response(
            system_prompt=system_prompt,
            messages=messages,
            user_content=data['content']
        )
        
        # Create AI message
        ai_message = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'role': 'assistant',
            'content': ai_response_content,
            'timestamp': datetime.now().isoformat(),
            'tokens': len(ai_response_content.split()) // 4  # Rough estimate
        }
        
        # Append AI message
        append_message(project_name, session_id, ai_message)
        
        return jsonify({
            'success': True,
            'data': {
                'user_message': user_message,
                'ai_message': ai_message
            },
            'message': 'Message sent successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/<session_id>/stream', methods=['POST'])
def stream_message(project_name, session_id):
    """Stream a message response (Server-Sent Events)"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'success': False, 'error': 'Message content is required'}), 400
        
        def generate():
            # Send user message acknowledgment
            yield f"data: {json.dumps({'type': 'user_message', 'content': data['content']})}\n\n"
            
            # Simulate streaming response (in production this would stream from Claude)
            response_text = "This is a simulated streaming response. In production, this would stream from Claude Code CLI."
            words = response_text.split()
            
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/<session_id>/stop', methods=['POST'])
def stop_generation(project_name, session_id):
    """Stop ongoing generation"""
    try:
        # In production, this would signal the AI process to stop
        return jsonify({
            'success': True,
            'message': 'Generation stopped'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def build_system_prompt(constitution, session_summary):
    """Build system prompt with constitution and session context"""
    prompt_parts = []
    
    # Add constitution rules
    if constitution:
        prompt_parts.append("## Project Constitution")
        for key, value in constitution.items():
            prompt_parts.append(f"- {key}: {value}")
    
    # Add session summary
    if session_summary:
        prompt_parts.append("\n## Session Summary")
        prompt_parts.append(session_summary)
    
    return "\n".join(prompt_parts)


def generate_ai_response(system_prompt, messages, user_content):
    """
    Generate AI response
    In production, this would call Claude Code CLI or OpenCode
    For now, returns a mock response
    """
    # TODO: Integrate with Claude Code CLI
    # Example integration:
    # from app.services.claude_runner import ClaudeRunner
    # runner = ClaudeRunner()
    # response = runner.run(user_content, context=messages, system_prompt=system_prompt)
    
    return f"Received your message: '{user_content}'. This is a mock response. Claude Code integration pending."
