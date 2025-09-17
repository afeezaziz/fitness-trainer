# Fitness App - Offline Capabilities

This Fitness Trainer app now supports offline functionality through Progressive Web App (PWA) technology.

## Features

### 🌐 Offline Functionality
- **Offline Data Entry**: Log food, calories, and exercise while offline
- **Local Storage**: Data is saved locally using IndexedDB
- **Automatic Sync**: Data automatically syncs when you reconnect
- **Offline Page**: Dedicated offline page with helpful information

### 📱 Progressive Web App
- **Installable**: Can be installed as a native app on your device
- **Offline Ready**: Works without internet connection
- **App-like Experience**: Full-screen mode with app icon
- **Push Notifications**: (Future enhancement)

## How to Use Offline

### 1. Install the App
1. Visit the app in a modern browser (Chrome, Firefox, Safari, Edge)
2. Look for the "Install App" button in the bottom-right corner
3. Click install to add it to your home screen

### 2. Using Offline
- Use the app normally while online
- When you go offline, continue logging your data
- Data will be saved locally with "Offline" indicators
- When you reconnect, data will automatically sync

### 3. Sync Process
- Background sync happens automatically when online
- You'll see notifications when sync completes
- Failed syncs will retry automatically

## Technical Implementation

### Service Worker (`/static/js/service-worker.js`)
- Caches static assets for offline use
- Handles fetch requests for offline functionality
- Manages background sync for data synchronization

### Offline Manager (`/static/js/offline.js`)
- Manages IndexedDB storage
- Handles form submissions when offline
- Provides UI feedback for online/offline status
- Manages installation prompts

### App Manifest (`/static/manifest.json`)
- Defines app metadata
- Provides app icons
- Configures display modes and shortcuts

### Database Structure
- **offlineData**: Stores pending sync operations
- **fitnessData**: Stores local fitness entries for immediate display

## Browser Support

This app works best in modern browsers that support:
- Service Workers
- IndexedDB
- Cache API
- Web App Manifest

**Supported Browsers:**
- Chrome/Chromium 60+
- Firefox 60+
- Safari 11.3+
- Edge 79+

## Development Notes

### Adding New Offline Features
1. Update the service worker to cache new assets
2. Add form listeners in offline.js
3. Update the database schema if needed
4. Add appropriate display methods

### Testing Offline Functionality
1. Use Chrome DevTools → Application → Service Workers
2. Toggle "Offline" mode to test offline behavior
3. Check IndexedDB for local data storage
4. Monitor network requests and sync operations

### Deployment Considerations
- Ensure HTTPS is enabled (required for service workers)
- Test on real devices for different network conditions
- Consider adding offline analytics for usage insights
- Plan for potential data conflicts during sync

## Future Enhancements

### Short-term
- [ ] Convert SVG icons to PNG for better compatibility
- [ ] Add offline data export functionality
- [ ] Implement offline analytics tracking
- [ ] Add offline settings management

### Long-term
- [ ] Push notifications for reminders
- [ ] Offline data visualization
- [ ] Background geolocation for workout tracking
- [ ] Offline workout plans and routines

## Troubleshooting

### Common Issues

**App won't install:**
- Ensure you're using a supported browser
- Check that the site is served over HTTPS
- Clear browser cache and try again

**Data not syncing:**
- Check your internet connection
- Ensure IndexedDB has sufficient storage
- Try refreshing the page
- Check browser console for errors

**Offline features not working:**
- Enable service workers in browser settings
- Clear site data and re-register service worker
- Check for browser compatibility issues

### Debug Mode
Add `?debug=true` to any URL to enable debug logging for offline features.

---

Built with ❤️ for fitness enthusiasts who need reliable tracking, online or offline.