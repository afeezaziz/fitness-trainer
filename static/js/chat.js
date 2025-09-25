/* Chat page logic extracted from templates/chat.html for Minimal & Clean UI */
(function () {
  'use strict';

  class FitnessChat {
    constructor() {
      this.socket = null;
      this.currentRoom = null;
      this.currentUser = null;
      this.typingTimeout = null;
      this.typingUsers = new Set();

      this.initializeChat();
      this.setupEventListeners();
    }

    readConfig() {
      try {
        const el = document.getElementById('chat-config');
        if (!el) return {};
        return JSON.parse(el.textContent || '{}');
      } catch (e) {
        console.error('Failed to parse chat config', e);
        return {};
      }
    }

    initializeChat() {
      // Current user from server-provided JSON config
      const cfg = this.readConfig();
      this.currentUser = {
        id: cfg.user_id ?? null,
        name: cfg.user_name ?? 'User'
      };

      // Connect to Socket.IO
      this.socket = io({
        auth: { user_id: this.currentUser.id }
      });

      this.setupSocketHandlers();
    }

    setupSocketHandlers() {
      this.socket.on('connect', () => {
        this.updateConnectionStatus('Connected', 'green');
        this.loadRooms();
      });

      this.socket.on('disconnect', () => {
        this.updateConnectionStatus('Disconnected', 'red');
      });

      this.socket.on('status', (data) => {
        console.log('Status:', data.message);
      });

      this.socket.on('rooms_list', (data) => {
        this.displayRooms(data);
      });

      this.socket.on('room_joined', (data) => {
        this.joinRoom(data);
      });

      this.socket.on('new_message', (data) => {
        this.displayMessage(data);
      });

      this.socket.on('user_joined', (data) => {
        this.displaySystemMessage(data.message);
        this.updateParticipants();
      });

      this.socket.on('user_left', (data) => {
        this.displaySystemMessage(data.message);
        this.updateParticipants();
      });

      this.socket.on('user_typing', (data) => {
        this.handleTypingIndicator(data);
      });

      this.socket.on('error', (data) => {
        this.showError(data.message);
      });
    }

    setupEventListeners() {
      // Message form
      const messageForm = document.getElementById('message-form');
      const messageInput = document.getElementById('message-input');

      if (messageForm) {
        messageForm.addEventListener('submit', (e) => {
          e.preventDefault();
          this.sendMessage();
        });
      }

      // Typing indicators
      if (messageInput) {
        messageInput.addEventListener('input', () => this.startTyping());
        messageInput.addEventListener('blur', () => this.stopTyping());
      }
    }

    loadRooms() {
      this.socket.emit('get_rooms');
    }

    displayRooms(rooms) {
      const roomsList = document.getElementById('rooms-list');
      if (!roomsList) return;
      roomsList.innerHTML = '';

      rooms.forEach(room => {
        const roomElement = document.createElement('div');
        roomElement.className = 'p-3 rounded-lg cursor-pointer transition-all duration-200 hover:bg-gray-100 border border-transparent hover:border-gray-200';
        roomElement.dataset.roomName = room.name;
        roomElement.innerHTML = `
          <div class="font-medium text-gray-800">${room.name}</div>
          <div class="text-sm text-gray-600">${room.description}</div>
        `;
        roomElement.addEventListener('click', () => this.selectRoom(room.name));
        roomsList.appendChild(roomElement);
      });

      // If we already have a current room, update active styling
      if (this.currentRoom) this.updateRoomHeader(this.currentRoom);
    }

    selectRoom(roomName) {
      if (this.currentRoom === roomName) return;

      // Leave current room if any
      if (this.currentRoom) {
        this.socket.emit('leave_room', { room: this.currentRoom });
      }

      // Join new room
      this.currentRoom = roomName;
      this.socket.emit('join_room', { room: roomName });

      // Update UI
      this.updateRoomHeader(roomName);
      this.clearMessages();
      this.enableMessageInput();
    }

    joinRoom(data) {
      const welcome = document.getElementById('welcome-message');
      const list = document.getElementById('messages-list');
      if (welcome) welcome.classList.add('hidden');
      if (list) list.classList.remove('hidden');

      // Display existing messages
      (data.messages || []).forEach(message => {
        this.displayMessage(message, false);
      });

      // Update participants
      this.updateParticipants(data.participants || []);

      // Update room header
      const nameEl = document.getElementById('current-room-name');
      const descEl = document.getElementById('current-room-description');
      const participants = document.getElementById('room-participants');
      if (nameEl) nameEl.textContent = data.room || '';
      if (descEl) descEl.textContent = data.room_description || '';
      if (participants) participants.classList.remove('hidden');
    }

    sendMessage() {
      const input = document.getElementById('message-input');
      const message = (input?.value || '').trim();
      if (!message || !this.currentRoom) return;

      this.socket.emit('send_message', { room: this.currentRoom, message });
      if (input) input.value = '';
      this.stopTyping();
    }

    displayMessage(message, scrollToBottom = true) {
      const messagesList = document.getElementById('messages-list');
      if (!messagesList) return;
      const messageElement = document.createElement('div');

      const isCurrentUser = message.user_id === this.currentUser.id;
      const isSystem = message.message_type !== 'text';

      if (isSystem) {
        messageElement.className = 'text-center';
        messageElement.innerHTML = `
          <span class="inline-block bg-gray-200 text-gray-600 px-3 py-1 rounded-full text-xs">${message.message}</span>
        `;
      } else {
        messageElement.className = `flex ${isCurrentUser ? 'justify-end' : 'justify-start'}`;
        messageElement.innerHTML = `
          <div class="max-w-xs lg:max-w-md">
            <div class="flex items-center space-x-2 mb-1 ${isCurrentUser ? 'justify-end' : 'justify-start'}">
              <span class="text-xs text-gray-500">${message.user_name}</span>
              <span class="text-xs text-gray-400">${this.formatTime(message.timestamp)}</span>
            </div>
            <div class="px-4 py-2 rounded-lg ${isCurrentUser ? 'bg-primary text-white' : 'bg-gray-200 text-gray-800'}">
              <p class="text-sm">${this.escapeHtml(message.message)}</p>
            </div>
          </div>
        `;
      }

      messagesList.appendChild(messageElement);
      if (scrollToBottom) this.scrollToBottom();
    }

    displaySystemMessage(message) {
      this.displayMessage({ message, message_type: 'system', timestamp: new Date().toISOString() });
    }

    startTyping() {
      if (this.typingTimeout) return;
      this.socket.emit('typing_start', { room: this.currentRoom });
      this.typingTimeout = setTimeout(() => this.stopTyping(), 1000);
    }

    stopTyping() {
      if (this.typingTimeout) {
        clearTimeout(this.typingTimeout);
        this.typingTimeout = null;
      }
      this.socket.emit('typing_stop', { room: this.currentRoom });
    }

    handleTypingIndicator(data) {
      const indicator = document.getElementById('typing-indicator');
      const typingText = document.getElementById('typing-text');
      if (!indicator || !typingText) return;

      if (data.is_typing && data.user_id !== this.currentUser.id) {
        this.typingUsers.add(data.user_id);
        typingText.textContent = `${data.user_name} is typing...`;
        indicator.classList.remove('hidden');
      } else {
        this.typingUsers.delete(data.user_id);
        if (this.typingUsers.size === 0) {
          indicator.classList.add('hidden');
        } else {
          typingText.textContent = `${this.typingUsers.size} people are typing...`;
        }
      }
    }

    updateParticipants(participants = []) {
      const participantsElement = document.getElementById('online-users');
      const participantCount = document.getElementById('participant-count');
      if (participantCount) participantCount.textContent = String(participants.length);
      if (!participantsElement) return;

      participantsElement.innerHTML = '';
      participants.forEach(participant => {
        const userElement = document.createElement('div');
        userElement.className = 'flex items-center space-x-2 p-2 rounded-lg bg-gray-50';
        userElement.innerHTML = `
          <div class="w-2 h-2 bg-green-500 rounded-full"></div>
          <span class="text-sm text-gray-700">${participant.user_name}</span>
        `;
        participantsElement.appendChild(userElement);
      });
    }

    updateRoomHeader(roomName) {
      // Toggle active state on sidebar rooms
      document.querySelectorAll('#rooms-list > div').forEach(r => {
        if (r instanceof HTMLElement) {
          const isActive = r.dataset.roomName === roomName;
          r.classList.toggle('bg-primary', isActive);
          r.classList.toggle('text-white', isActive);
          r.classList.toggle('hover:bg-gray-100', !isActive);
        }
      });
    }

    clearMessages() {
      const messagesList = document.getElementById('messages-list');
      if (messagesList) messagesList.innerHTML = '';
    }

    enableMessageInput() {
      const input = document.getElementById('message-input');
      const button = document.querySelector('#message-form button');
      const inputArea = document.getElementById('message-input-area');
      if (input) input.disabled = false;
      if (button) button.disabled = false;
      if (inputArea) inputArea.classList.remove('hidden');
      if (input) input.focus();
    }

    updateConnectionStatus(status, color) {
      const indicator = document.getElementById('status-indicator');
      const text = document.getElementById('status-text');
      if (indicator) indicator.className = `w-2 h-2 bg-${color}-500 rounded-full`;
      if (text) text.textContent = status;

      // Hide status after 3 seconds if connected
      const bar = document.getElementById('connection-status');
      if (!bar) return;
      if (status === 'Connected') {
        setTimeout(() => bar.classList.add('hidden'), 3000);
      } else {
        bar.classList.remove('hidden');
      }
    }

    scrollToBottom() {
      const container = document.getElementById('messages-container');
      if (container) container.scrollTop = container.scrollHeight;
    }

    formatTime(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    showError(message) {
      // Create a toast notification
      const toast = document.createElement('div');
      toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
      toast.textContent = message;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    }
  }

  // Initialize chat when page loads
  window.addEventListener('DOMContentLoaded', () => {
    window.chat = new FitnessChat();
  });
})();
