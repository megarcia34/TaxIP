const fs = require('fs');

const appJson = {
  "expo": {
    "name": "TaxIP Chofer",
    "slug": "taxip-chofer",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "scheme": "taxip",
    "userInterfaceStyle": "light",
    "ios": { "supportsTablet": true, "bundleIdentifier": "com.taxip.chofer" },
    "android": {
      "package": "com.taxip.chofer",
      "adaptiveIcon": {
        "backgroundColor": "#1A3A52",
        "foregroundImage": "./assets/android-icon-foreground.png",
        "backgroundImage": "./assets/android-icon-background.png",
        "monochromeImage": "./assets/android-icon-monochrome.png"
      },
      "predictiveBackGestureEnabled": false,
      "permissions": ["CAMERA", "ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION", "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE"]
    },
    "web": { "favicon": "./assets/favicon.png" },
    "plugins": [
      "expo-router",
      "expo-camera",
      "expo-image-picker",
      "expo-location",
      "expo-notifications",
      ["expo-splash-screen", { "image": "./assets/splash-icon.png", "resizeMode": "contain", "backgroundColor": "#1A3A52", "imageWidth": 200 }],
      ["expo-build-properties", { "android": { "usesCleartextTraffic": true } }]
    ],
    "experiments": { "typedRoutes": false },
    "extra": { "router": { "origin": false }, "eas": { "projectId": "" } }
  }
};

const packageJson = {
  "name": "app-chofer",
  "version": "1.0.0",
  "main": "expo-router/entry",
  "dependencies": {
    "@expo/ngrok": "^4.1.3",
    "@hookform/resolvers": "^5.9.1",
    "@react-native-async-storage/async-storage": "2.2.0",
    "@react-native-community/netinfo": "12.0.1",
    "axios": "^1.20.0",
    "date-fns": "^4.4.0",
    "expo": "~57.0.24",
    "expo-build-properties": "~57.0.21",
    "expo-camera": "~57.0.4",
    "expo-constants": "~57.0.17",
    "expo-file-system": "~57.0.6",
    "expo-image-picker": "~57.0.19",
    "expo-linear-gradient": "~57.0.1",
    "expo-linking": "~57.0.9",
    "expo-location": "~57.0.19",
    "expo-notifications": "~57.0.20",
    "expo-router": "~57.0.22",
    "expo-splash-screen": "~57.0.9",
    "expo-status-bar": "~57.0.1",
    "expo-task-manager": "~57.0.19",
    "react": "19.2.3",
    "react-hook-form": "^7.87.0",
    "react-native": "0.86.3",
    "react-native-google-places-autocomplete": "^2.6.5",
    "react-native-maps": "1.27.2",
    "react-native-paper": "^5.15.3",
    "react-native-reanimated": "4.5.1",
    "react-native-safe-area-context": "~5.7.0",
    "react-native-screens": "~4.26.0",
    "react-native-toast-message": "^2.5.2",
    "react-native-worklets": "0.10.1",
    "zod": "^4.6.1",
    "zustand": "^5.0.15"
  },
  "devDependencies": {
    "@types/react": "~19.2.2",
    "typescript": "~6.0.3",
    "patch-package": "^8.0.1"
  },
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "postinstall": "patch-package"
  },
  "private": true,
  "overrides": {
    "react": "19.2.3",
    "react-dom": "19.2.3",
    "react-server-dom-webpack": { "react": "19.2.3", "react-dom": "19.2.3" }
  }
};

fs.writeFileSync('app.json', JSON.stringify(appJson, null, 2) + '\n', 'utf8');
fs.writeFileSync('package.json', JSON.stringify(packageJson, null, 2) + '\n', 'utf8');
console.log('✅ Archivos corregidos y guardados con formato JSON 100% limpio (sin espacios ni BOM).');