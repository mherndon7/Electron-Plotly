const { app, BrowserWindow, session } = require('electron');
const log = require('electron-log');
const path = require('path');

function logFormat(data) {
  const date = new Date();
  const d = date.toISOString().split('T');
  const datePart = d[0];
  const timePart = d[1].split('.')[0];
  timestamp = `${datePart} ${timePart}`;

  // data.data contains the original arguments passed to the log function
  const message = data.data.join(' ');
  return [`[${timestamp}] [${data.level.toUpperCase()}]: ${message}`];
}

log.initialize();
log.transports.file = 'debug';
log.transports.console = 'debug';
log.transports.file.format = logFormat;
log.transports.console.format = logFormat;

log.transports.file.resolvePathFn = () => path.join(__dirname, 'electron-log.log');

Object.assign(console, log.functions);

app.commandLine.appendSwitch('enable-logging');
// app.commandLine.appendSwitch('v', '4');
app.commandLine.appendSwitch('no-sandbox');
app.commandLine.appendSwitch('ignore-gpu-blacklist');
app.commandLine.appendSwitch('enable-gpu-rasterization');

let mainWindow;

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    autoHideMenuBar: true,
  });

  if (process.argv.includes('development')) {
    console.log('Developer mode enabled: loading from localhost:4200');
    const url = 'http://localhost:4200';

    const cookieDetails = {
      url: url, // The URL to associate the cookie with
      name: 'session_token',
      value: 'super_secret_value',
      secure: true,
      // httpOnly: true,
    };

    mainWindow.webContents.session.cookies
      .set(cookieDetails)
      .then(() => {
        console.log('Cookie "session_token" set for localhost:4200');
      })
      .catch((error) => {
        console.error(error);
      });

    mainWindow.webContents.openDevTools();
    mainWindow.loadURL(url);
  } else {
    mainWindow.webContents.openDevTools();
    mainWindow.loadFile('dist/electron-app/browser/index.html');
  }

  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    console.log(message + ' ' + sourceId + ' (' + line + ')');
  });

  mainWindow.on('closed', function () {
    mainWindow.removeAllListeners('close');
    mainWindow = null;
  });
};

app.whenReady().then(() => {
  createWindow();
  log.info('Hello, log');
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();

  session.defaultSession.cookies
    .get({ url: 'http://localhost:4200' })
    .then((cookies) => {
      console.log('Cookies retrieved:', cookies);
    })
    .catch((error) => {
      console.log(error);
    });
});

app.on('before-quit', () => {
  console.log('App is about to quit, performing cleanup');
});

app.on('will-quit', () => {
  console.log('App is quitting, cleaning up resources');
});

app.on('quit', () => {
  console.log('App has quit, exiting process');
  app.exit(0);
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    console.log('All windows closed, quitting app');
    app.quit();
  }
});
