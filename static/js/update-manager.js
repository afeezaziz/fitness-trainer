class UpdateManager {
  constructor() {
    this.currentVersion = '1.0.0';
    this.updateAvailable = false;
    this.registration = null;
    this.deferredPrompt = null;
    this.updateNotification = null;

    this.init();
  }

  async init() {
    // Set up service worker listener for updates
    this.setupServiceWorkerListener();

    // Set up periodic update checking
    this.startPeriodicUpdateCheck();

    // Check for updates immediately
    this.checkForUpdates();

    // Set up update button
    this.setupUpdateButton();

    // Add version info to UI
    this.addVersionInfo();
  }

  setupServiceWorkerListener() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'UPDATE_AVAILABLE') {
          this.handleUpdateAvailable(event.data);
        }
      });
    }
  }

  handleUpdateAvailable(data) {
    this.updateAvailable = true;
    console.log('Update available:', data);

    // Don't show update notification immediately - wait for user idle time
    this.scheduleUpdateNotification();
  }

  scheduleUpdateNotification() {
    // Wait 10 seconds before showing update notification
    setTimeout(() => {
      if (this.updateAvailable && this.shouldShowUpdateNotification()) {
        this.showUpdateNotification();
      }
    }, 10000);
  }

  shouldShowUpdateNotification() {
    // Don't show if user is actively using forms
    const activeElement = document.activeElement;
    const isInForm = activeElement && (
      activeElement.tagName === 'INPUT' ||
      activeElement.tagName === 'TEXTAREA' ||
      activeElement.tagName === 'SELECT'
    );

    return !isInForm && !this.updateNotification;
  }

  showUpdateNotification() {
    if (this.updateNotification) return;

    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-blue-600 text-white p-6 rounded-lg shadow-xl z-50 max-w-sm transform transition-all duration-300 translate-x-full';
    notification.innerHTML = `
      <div class="flex items-start space-x-3">
        <svg class="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
        </svg>
        <div class="flex-1">
          <h4 class="font-semibold mb-1">Update Available</h4>
          <p class="text-sm text-blue-100 mb-4">A new version of the Fitness App is available with improvements and bug fixes.</p>
          <div class="flex space-x-2">
            <button onclick="updateManager.applyUpdate()" class="bg-white text-blue-600 px-4 py-2 rounded text-sm font-medium hover:bg-blue-50 transition-colors">
              Update Now
            </button>
            <button onclick="updateManager.snoozeUpdate()" class="bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-800 transition-colors">
              Later
            </button>
          </div>
        </div>
        <button onclick="updateManager.dismissUpdate()" class="text-blue-200 hover:text-white">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.classList.remove('translate-x-full');
    }, 100);

    this.updateNotification = notification;
  }

  applyUpdate() {
    if (this.registration && this.registration.waiting) {
      // Send message to service worker to skip waiting
      this.registration.waiting.postMessage({ type: 'SKIP_WAITING' });

      // Show updating message
      this.showUpdatingMessage();

      // Reload page after a short delay
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    } else {
      // Fallback - just reload the page
      window.location.reload();
    }
  }

  showUpdatingMessage() {
    if (this.updateNotification) {
      this.updateNotification.innerHTML = `
        <div class="flex items-center space-x-3">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
          <div>
            <h4 class="font-semibold">Updating...</h4>
            <p class="text-sm text-blue-100">Please wait while we update your app.</p>
          </div>
        </div>
      `;
    }
  }

  snoozeUpdate() {
    this.dismissUpdate();

    // Show reminder after 1 hour
    setTimeout(() => {
      if (this.updateAvailable) {
        this.showUpdateNotification();
      }
    }, 60 * 60 * 1000); // 1 hour
  }

  dismissUpdate() {
    if (this.updateNotification) {
      this.updateNotification.classList.add('translate-x-full');
      setTimeout(() => {
        if (this.updateNotification && this.updateNotification.parentElement) {
          this.updateNotification.remove();
        }
        this.updateNotification = null;
      }, 300);
    }
  }

  async checkForUpdates() {
    try {
      if ('serviceWorker' in navigator) {
        this.registration = await navigator.serviceWorker.getRegistration();

        if (this.registration) {
          // Check for service worker updates
          await this.registration.update();

          // Get current version info
          await this.getVersionInfo();
        }
      }
    } catch (error) {
      console.error('Error checking for updates:', error);
    }
  }

  async getVersionInfo() {
    if (this.registration && this.registration.active) {
      // Create message channel for version info
      const messageChannel = new MessageChannel();

      this.registration.active.postMessage({
        type: 'GET_VERSION'
      }, [messageChannel.port2]);

      messageChannel.port1.onmessage = (event) => {
        if (event.data && event.data.type === 'VERSION_INFO') {
          this.currentVersion = event.data.version;
          this.updateVersionDisplay();
        }
      };
    }
  }

  startPeriodicUpdateCheck() {
    // Check for updates every 30 minutes
    setInterval(() => {
      this.checkForUpdates();
    }, 30 * 60 * 1000); // 30 minutes

    // Also check when user comes back online
    window.addEventListener('online', () => {
      this.checkForUpdates();
    });
  }

  setupUpdateButton() {
    const updateBtn = document.getElementById('manualUpdateBtn');
    if (updateBtn) {
      updateBtn.addEventListener('click', () => {
        this.checkForUpdates();
        this.showManualUpdateMessage();
      });
    }
  }

  showManualUpdateMessage() {
    const message = document.createElement('div');
    message.className = 'fixed bottom-4 left-4 bg-gray-800 text-white px-4 py-2 rounded-lg text-sm z-40';
    message.textContent = 'Checking for updates...';

    document.body.appendChild(message);

    setTimeout(() => {
      message.remove();
    }, 3000);
  }

  addVersionInfo() {
    // Add version info to footer or settings
    const footer = document.querySelector('footer');
    if (footer) {
      const versionDiv = document.createElement('div');
      versionDiv.className = 'text-center mt-4';
      versionDiv.innerHTML = `
        <span class="text-gray-400 text-xs">
          Version <span class="version-number">${this.currentVersion}</span>
          <span class="update-status ml-2"></span>
        </span>
      `;

      const bottomBar = footer.querySelector('.border-t');
      if (bottomBar) {
        bottomBar.appendChild(versionDiv);
        this.updateVersionDisplay();
      }
    }
  }

  updateVersionDisplay() {
    const versionNumber = document.querySelector('.version-number');
    const updateStatus = document.querySelector('.update-status');

    if (versionNumber) {
      versionNumber.textContent = this.currentVersion;
    }

    if (updateStatus) {
      if (this.updateAvailable) {
        updateStatus.innerHTML = `
          <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
            </svg>
            Update Available
          </span>
        `;
      } else {
        updateStatus.innerHTML = `
          <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
            Up to date
          </span>
        `;
      }
    }
  }

  // Force update (useful for debugging or admin features)
  async forceUpdate() {
    try {
      // Clear all caches
      if ('caches' in window) {
        const cacheNames = await caches.keys();
        await Promise.all(cacheNames.map(name => caches.delete(name)));
      }

      // Unregister service worker
      if ('serviceWorker' in navigator) {
        const registrations = await navigator.serviceWorker.getRegistrations();
        await Promise.all(registrations.map(reg => reg.unregister()));
      }

      // Reload page
      window.location.reload(true);
    } catch (error) {
      console.error('Error forcing update:', error);
      window.location.reload(true);
    }
  }
}

// Initialize update manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.updateManager = new UpdateManager();
});

// Global function for manual updates
async function checkForUpdates() {
  if (window.updateManager) {
    await window.updateManager.checkForUpdates();
  }
}

// Global function for force updates
async function forceUpdate() {
  if (window.updateManager) {
    await window.updateManager.forceUpdate();
  }
}