const { app, BrowserWindow, session } = require('electron');

app.commandLine.appendSwitch('enable-logging');
app.commandLine.appendSwitch('no-sandbox');
app.commandLine.appendSwitch('ignore-gpu-blacklist');
app.commandLine.appendSwitch('enable-gpu-rasterization');

const createWindow = () => {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
  });

  if (args.includes('development')) {
    console.log('Developer mode enabled: loading from localhost:4200');
    app.commandLine.appendSwitch('enable-logging');
    win.webContents.openDevTools();

    win.loadURL('http://localhost:4200');
  } else {
    win.loadFile('dist/electron-app/browser/index.html');
  }
};

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
