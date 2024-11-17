const path = require('path');
const { app, BrowserWindow } = require('electron');

let mainWindow = null;

// Create the mainWindow
const createWindow = () => {
    mainWindow = new BrowserWindow({
        width: 900,
        height: 700,
        frame: false,
        transparent: true,
        vibrancy: "sidebar", // Try "titlebar" for less transparency
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            contextIsolation: true,
        },
    });
    

  mainWindow.loadFile('index.html');

  mainWindow.on('ready-to-show', () => {
    if (mainWindow) {
      mainWindow.show();
    }
  });

  mainWindow.on('focus', () => {
    if (mainWindow) {
      mainWindow.setVibrancy('ultra-dark'); // Reapply vibrancy on focus
      mainWindow.setOpacity(1); // Fully visible when focused
    }
  });

  mainWindow.on('blur', () => {
    if (mainWindow) {
      mainWindow.setOpacity(0.98); // Slightly dim when out of focus
      mainWindow.setVibrancy('ultra-dark');
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
};

// App lifecycle
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  } else {
    mainWindow.show();
  }
});

app.whenReady().then(createWindow);
