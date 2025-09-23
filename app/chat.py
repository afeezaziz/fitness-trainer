from flask import request, jsonify
from flask_socketio import emit, join_room, leave_room, rooms
from app.models import db, User, ChatRoom, ChatMessage, ChatParticipant
from datetime import datetime
import json

def init_chat(socketio):

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        if 'user_id' not in request.session:
            return False  # Reject connection if not authenticated
        emit('status', {'message': 'Connected to chat server'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            # Update online status for all rooms
            participations = ChatParticipant.query.filter_by(user_id=user_id, is_online=True).all()
            for participation in participations:
                participation.is_online = False
                participation.last_active = datetime.utcnow()

                # Notify room that user left
                room_name = participation.room.name
                emit('user_left', {
                    'user_id': user_id,
                    'user_name': participation.user.name,
                    'room': room_name
                }, room=room_name)

            db.session.commit()

    @socketio.on('join_room')
    def handle_join_room(data):
        """Handle user joining a chat room"""
        if 'user_id' not in request.session:
            emit('error', {'message': 'Not authenticated'})
            return

        try:
            user_id = request.session['user_id']
            room_name = data['room']

            # Get room and user
            room = ChatRoom.query.filter_by(name=room_name, is_active=True).first()
            user = User.query.get(user_id)

            if not room or not user:
                emit('error', {'message': 'Room or user not found'})
                return

            # Join socket.io room
            join_room(room_name)

            # Add or update participant
            participant = ChatParticipant.query.filter_by(
                user_id=user_id,
                room_id=room.id
            ).first()

            if participant:
                participant.is_online = True
                participant.last_active = datetime.utcnow()
                join_message = f"{user.name} reconnected to the room"
            else:
                participant = ChatParticipant(
                    user_id=user_id,
                    room_id=room.id,
                    is_online=True,
                    last_active=datetime.utcnow()
                )
                db.session.add(participant)
                join_message = f"{user.name} joined the room"

            db.session.commit()

            # Send join message
            join_msg = ChatMessage(
                room_id=room.id,
                user_id=user_id,
                message=join_message,
                message_type='join'
            )
            db.session.add(join_msg)
            db.session.commit()

            # Notify room
            emit('user_joined', {
                'user_id': user_id,
                'user_name': user.name,
                'room': room_name,
                'message': join_message,
                'timestamp': join_msg.created_at.isoformat()
            }, room=room_name)

            # Send room info to user
            recent_messages = ChatMessage.query.filter_by(room_id=room.id)\
                .order_by(ChatMessage.created_at.desc())\
                .limit(50)\
                .all()

            participants = ChatParticipant.query.filter_by(
                room_id=room.id,
                is_online=True
            ).all()

            emit('room_joined', {
                'room': room_name,
                'room_description': room.description,
                'messages': [{
                    'id': msg.id,
                    'user_id': msg.user_id,
                    'user_name': msg.user.name,
                    'message': msg.message,
                    'message_type': msg.message_type,
                    'timestamp': msg.created_at.isoformat(),
                    'is_edited': msg.is_edited
                } for msg in recent_messages[::-1]],  # Reverse for chronological order
                'participants': [{
                    'user_id': p.user_id,
                    'user_name': p.user.name,
                    'is_online': p.is_online
                } for p in participants]
            })

        except Exception as e:
            emit('error', {'message': f'Failed to join room: {str(e)}'})

    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Handle user leaving a chat room"""
        if 'user_id' not in request.session:
            return

        try:
            user_id = request.session['user_id']
            room_name = data['room']

            room = ChatRoom.query.filter_by(name=room_name).first()
            user = User.query.get(user_id)

            if not room or not user:
                return

            # Leave socket.io room
            leave_room(room_name)

            # Update participant status
            participant = ChatParticipant.query.filter_by(
                user_id=user_id,
                room_id=room.id
            ).first()

            if participant:
                participant.is_online = False
                participant.last_active = datetime.utcnow()
                db.session.commit()

                # Send leave message
                leave_msg = ChatMessage(
                    room_id=room.id,
                    user_id=user_id,
                    message=f"{user.name} left the room",
                    message_type='leave'
                )
                db.session.add(leave_msg)
                db.session.commit()

                # Notify room
                emit('user_left', {
                    'user_id': user_id,
                    'user_name': user.name,
                    'room': room_name,
                    'message': f"{user.name} left the room",
                    'timestamp': leave_msg.created_at.isoformat()
                }, room=room_name)

        except Exception as e:
            emit('error', {'message': f'Failed to leave room: {str(e)}'})

    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle sending a chat message"""
        if 'user_id' not in request.session:
            emit('error', {'message': 'Not authenticated'})
            return

        try:
            user_id = request.session['user_id']
            room_name = data['room']
            message = data['message'].strip()

            if not message:
                emit('error', {'message': 'Message cannot be empty'})
                return

            # Get room and verify user is participant
            room = ChatRoom.query.filter_by(name=room_name, is_active=True).first()
            participant = ChatParticipant.query.filter_by(
                user_id=user_id,
                room_id=room.id
            ).first()

            if not room or not participant:
                emit('error', {'message': 'Not authorized to send message in this room'})
                return

            user = User.query.get(user_id)

            # Create message
            chat_message = ChatMessage(
                room_id=room.id,
                user_id=user_id,
                message=message,
                message_type='text'
            )
            db.session.add(chat_message)

            # Update participant activity
            participant.last_active = datetime.utcnow()
            participant.is_online = True

            db.session.commit()

            # Broadcast message to room
            emit('new_message', {
                'id': chat_message.id,
                'user_id': user_id,
                'user_name': user.name,
                'message': message,
                'message_type': 'text',
                'timestamp': chat_message.created_at.isoformat(),
                'is_edited': False
            }, room=room_name)

        except Exception as e:
            emit('error', {'message': f'Failed to send message: {str(e)}'})

    @socketio.on('get_rooms')
    def handle_get_rooms():
        """Get list of available chat rooms"""
        try:
            rooms = ChatRoom.query.filter_by(is_active=True).all()
            emit('rooms_list', [{
                'name': room.name,
                'description': room.description,
                'created_at': room.created_at.isoformat()
            } for room in rooms])
        except Exception as e:
            emit('error', {'message': f'Failed to get rooms: {str(e)}'})

    @socketio.on('typing_start')
    def handle_typing_start(data):
        """Handle user typing indicator"""
        if 'user_id' not in request.session:
            return

        try:
            user_id = request.session['user_id']
            room_name = data['room']
            user = User.query.get(user_id)

            emit('user_typing', {
                'user_id': user_id,
                'user_name': user.name,
                'is_typing': True
            }, room=room_name)

        except Exception as e:
            pass  # Silently handle typing errors

    @socketio.on('typing_stop')
    def handle_typing_stop(data):
        """Handle user stopped typing indicator"""
        if 'user_id' not in request.session:
            return

        try:
            user_id = request.session['user_id']
            room_name = data['room']
            user = User.query.get(user_id)

            emit('user_typing', {
                'user_id': user_id,
                'user_name': user.name,
                'is_typing': False
            }, room=room_name)

        except Exception as e:
            pass  # Silently handle typing errors