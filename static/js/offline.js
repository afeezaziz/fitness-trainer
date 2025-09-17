class OfflineManager {
  constructor() {
    this.dbName = 'FitnessAppDB';
    this.dbVersion = 1;
    this.isOnline = navigator.onLine;
    this.init();
  }

  async init() {
    // Initialize IndexedDB
    await this.initDB();

    // Register service worker
    await this.registerServiceWorker();

    // Set up event listeners
    this.setupEventListeners();

    // Set up background sync
    this.setupBackgroundSync();

    // Check for pending sync on load
    await this.syncPendingData();
  }

  async initDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Create object stores for offline data
        if (!db.objectStoreNames.contains('offlineData')) {
          const offlineStore = db.createObjectStore('offlineData', { keyPath: 'id', autoIncrement: true });
          offlineStore.createIndex('timestamp', 'timestamp', { unique: false });
          offlineStore.createIndex('synced', 'synced', { unique: false });
        }

        // Create object store for local fitness data
        if (!db.objectStoreNames.contains('fitnessData')) {
          const fitnessStore = db.createObjectStore('fitnessData', { keyPath: 'id', autoIncrement: true });
          fitnessStore.createIndex('type', 'type', { unique: false });
          fitnessStore.createIndex('date', 'date', { unique: false });
        }
      };

      request.onsuccess = (event) => {
        this.db = event.target.result;
        resolve();
      };

      request.onerror = (event) => {
        console.error('Database initialization failed:', event.target.error);
        reject(event.target.error);
      };
    });
  }

  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
        console.log('Service Worker registered successfully:', registration);

        // Check for updates
        registration.addEventListener('updatefound', () => {
          const installingWorker = registration.installing;
          installingWorker.addEventListener('statechange', () => {
            if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.showUpdateNotification();
            }
          });
        });

      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    }
  }

  setupEventListeners() {
    // Online/offline event listeners
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.updateOnlineStatus();
      this.syncPendingData();
      this.hideOfflineNotification();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.updateOnlineStatus();
      this.showOfflineNotification();
    });

    // Form submission listeners
    this.setupFormListeners();
  }

  setupFormListeners() {
    // Food form
    const foodForm = document.querySelector('form[action="/add_food"]');
    if (foodForm) {
      foodForm.addEventListener('submit', (e) => this.handleFormSubmit(e, '/add_food', 'food'));
    }

    // Calories form
    const caloriesForm = document.querySelector('form[action="/add_calories"]');
    if (caloriesForm) {
      caloriesForm.addEventListener('submit', (e) => this.handleFormSubmit(e, '/add_calories', 'calories'));
    }

    // Exercise form
    const exerciseForm = document.querySelector('form[action="/add_exercise"]');
    if (exerciseForm) {
      exerciseForm.addEventListener('submit', (e) => this.handleFormSubmit(e, '/add_exercise', 'exercise'));
    }
  }

  async handleFormSubmit(event, endpoint, type) {
    if (!this.isOnline) {
      event.preventDefault();

      const formData = new FormData(event.target);
      const data = this.formDataToObject(formData);

      // Store offline data locally
      await this.storeOfflineData(endpoint, 'POST', data);

      // Also store in local fitness data for immediate display
      await this.storeFitnessData(type, data);

      // Show success message
      this.showOfflineSuccessMessage(type);

      // Reset form
      event.target.reset();
    }
  }

  formDataToObject(formData) {
    const obj = {};
    formData.forEach((value, key) => {
      obj[key] = value;
    });
    return obj;
  }

  async storeOfflineData(url, method, payload) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['offlineData'], 'readwrite');
      const store = transaction.objectStore('offlineData');

      const data = {
        url,
        method,
        payload,
        timestamp: new Date().toISOString(),
        synced: false
      };

      const request = store.add(data);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async storeFitnessData(type, data) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['fitnessData'], 'readwrite');
      const store = transaction.objectStore('fitnessData');

      const fitnessData = {
        type,
        data,
        date: new Date().toISOString(),
        timestamp: new Date().toISOString()
      };

      const request = store.add(fitnessData);

      request.onsuccess = () => {
        this.updateLocalDisplay(type, data);
        resolve();
      };
      request.onerror = () => reject(request.error);
    });
  }

  updateLocalDisplay(type, data) {
    // Update the local display with new data
    switch (type) {
      case 'food':
        this.addFoodToDisplay(data);
        break;
      case 'calories':
        this.addCaloriesToDisplay(data);
        break;
      case 'exercise':
        this.addExerciseToDisplay(data);
        break;
    }
  }

  addFoodToDisplay(data) {
    const container = document.querySelector('.food-entries');
    if (container) {
      const entry = document.createElement('div');
      entry.className = 'bg-white p-4 rounded-lg shadow-sm border-l-4 border-yellow-500 mb-3';
      entry.innerHTML = `
        <div class="flex justify-between items-start">
          <div>
            <h4 class="font-semibold text-gray-800">${data['food-name']}</h4>
            <p class="text-sm text-gray-600">${data['meal-type']} - ${data['portion-size']}</p>
            <p class="text-xs text-gray-500">${new Date().toLocaleString()}</p>
          </div>
          <span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">Offline</span>
        </div>
      `;
      container.insertBefore(entry, container.firstChild);
    }
  }

  addCaloriesToDisplay(data) {
    const container = document.querySelector('.calorie-entries');
    if (container) {
      const entry = document.createElement('div');
      entry.className = 'bg-white p-4 rounded-lg shadow-sm border-l-4 border-blue-500 mb-3';
      entry.innerHTML = `
        <div class="flex justify-between items-start">
          <div>
            <h4 class="font-semibold text-gray-800">${data['food-item']}</h4>
            <p class="text-sm text-gray-600">${data['calories']} calories - ${data['quantity']}</p>
            <p class="text-xs text-gray-500">${new Date().toLocaleString()}</p>
          </div>
          <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">Offline</span>
        </div>
      `;
      container.insertBefore(entry, container.firstChild);
    }
  }

  addExerciseToDisplay(data) {
    const container = document.querySelector('.exercise-entries');
    if (container) {
      const entry = document.createElement('div');
      entry.className = 'bg-white p-4 rounded-lg shadow-sm border-l-4 border-green-500 mb-3';
      entry.innerHTML = `
        <div class="flex justify-between items-start">
          <div>
            <h4 class="font-semibold text-gray-800">${data['exercise-name']}</h4>
            <p class="text-sm text-gray-600">${data['exercise-type']} - ${data['sets']} sets × ${data['reps']} reps</p>
            ${data.weight ? `<p class="text-sm text-gray-600">${data.weight} lbs</p>` : ''}
            <p class="text-xs text-gray-500">${new Date().toLocaleString()}</p>
          </div>
          <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">Offline</span>
        </div>
      `;
      container.insertBefore(entry, container.firstChild);
    }
  }

  async syncPendingData() {
    if (!this.isOnline) return;

    try {
      const offlineData = await this.getOfflineData();

      for (const data of offlineData) {
        try {
          const response = await fetch(data.url, {
            method: data.method,
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(data.payload)
          });

          if (response.ok) {
            await this.removeOfflineData(data.id);
          }
        } catch (error) {
          console.error('Sync failed for:', data, error);
        }
      }

      if (offlineData.length > 0) {
        this.showSyncCompleteMessage();
      }
    } catch (error) {
      console.error('Error syncing pending data:', error);
    }
  }

  async getOfflineData() {
    return new Promise((resolve) => {
      const transaction = this.db.transaction(['offlineData'], 'readonly');
      const store = transaction.objectStore('offlineData');
      const getAll = store.getAll();

      getAll.onsuccess = () => resolve(getAll.result);
      getAll.onerror = () => resolve([]);
    });
  }

  async removeOfflineData(id) {
    return new Promise((resolve) => {
      const transaction = this.db.transaction(['offlineData'], 'readwrite');
      const store = transaction.objectStore('offlineData');
      const request = store.delete(id);

      request.onsuccess = () => resolve();
      request.onerror = () => resolve();
    });
  }

  setupBackgroundSync() {
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      navigator.serviceWorker.ready.then((registration) => {
        this.registration = registration;
      });
    }
  }

  showOfflineNotification() {
    this.showNotification('You are offline. Data will be saved locally and synced when you reconnect.', 'warning');
  }

  hideOfflineNotification() {
    const notification = document.querySelector('.offline-notification');
    if (notification) {
      notification.remove();
    }
  }

  showOfflineSuccessMessage(type) {
    const messages = {
      food: 'Food entry saved locally. Will sync when online.',
      calories: 'Calorie entry saved locally. Will sync when online.',
      exercise: 'Exercise entry saved locally. Will sync when online.'
    };

    this.showNotification(messages[type], 'success');
  }

  showSyncCompleteMessage() {
    this.showNotification('Offline data has been synced successfully!', 'success');
  }

  showUpdateNotification() {
    this.showNotification('New version available. Refresh to update.', 'info');
  }

  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${this.getNotificationClass(type)}`;
    notification.innerHTML = `
      <div class="flex items-center">
        <span>${message}</span>
        <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    `;

    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);
  }

  getNotificationClass(type) {
    const classes = {
      success: 'bg-green-500 text-white',
      warning: 'bg-yellow-500 text-white',
      error: 'bg-red-500 text-white',
      info: 'bg-blue-500 text-white'
    };
    return classes[type] || classes.info;
  }

  updateOnlineStatus() {
    const statusElement = document.querySelector('.online-status');
    if (statusElement) {
      statusElement.textContent = this.isOnline ? 'Online' : 'Offline';
      statusElement.className = `online-status ${this.isOnline ? 'text-green-600' : 'text-red-600'}`;
    }
  }
}

// Initialize the offline manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
  // Check if it's a logged-in page (has forms)
  if (document.querySelector('form[action^="/add_"]')) {
    window.offlineManager = new OfflineManager();
  }

  // Add install button functionality
  setupInstallButton();
});

// Install button functionality
let deferredPrompt;

function setupInstallButton() {
  const installBtn = document.getElementById('installBtn');
  if (!installBtn) return;

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    installBtn.style.display = 'block';
  });

  installBtn.addEventListener('click', async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      deferredPrompt = null;
      installBtn.style.display = 'none';
    }
  });

  window.addEventListener('appinstalled', () => {
    installBtn.style.display = 'none';
    console.log('Fitness App was installed');
  });
}