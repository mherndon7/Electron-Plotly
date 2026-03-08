const { app, BrowserWindow, session } = require('electron');
const log = require('electron-log');
const path = require('path');
const spawn = require('child_process').execFile;

// Custom log format to include timestamp and log level
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
log.transports.file.resolvePathFn = () => path.join(__dirname, 'electron-log.log');
log.transports.file.format = logFormat;
log.transports.console.format = logFormat;

Object.assign(console, log.functions);

// Chrome Flags
app.commandLine.appendSwitch('enable-logging');
// app.commandLine.appendSwitch('v', '4');
app.commandLine.appendSwitch('no-sandbox');
app.commandLine.appendSwitch('ignore-gpu-blacklist');
app.commandLine.appendSwitch('enable-gpu-rasterization');

// Spawn the Python process, passing data as a command-line argument
const pythonProcess = spawn('python', ['-m', 'server', 'cookies']);
// const process = spawn('python', ['-m', 'cookies', ' cookies']);

pythonProcess.stdout.on('data', (data) => {
  log.info(`Python output: ${data.toString()}`);
});

pythonProcess.stderr.on('data', (data) => {
  log.error(`Python error: ${data.toString()}`);
});

pythonProcess.on('close', (code) => {
  log.info(`Python process exited with code ${code}`);
});

// Development vs Production URL
const isDevelopment = process.argv.includes('development');
let url = isDevelopment ? 'http://localhost:4200' : 'http://localhost:8888';

let mainWindow;
const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    // autoHideMenuBar: true,
  });

  if (isDevelopment) log.info('Developer mode enabled: loading from localhost:4200');

  mainWindow.webContents.openDevTools();
  mainWindow.loadURL(url);
  const cookieDetails = {
    url: url, // The URL to associate the cookie with
    name: 'session_token',
    value: 'super_secret_value',
    secure: true,
    httpOnly: true,
  };

  mainWindow.webContents.session.cookies
    .set(cookieDetails)
    .then(() => {
      log.info(`Cookie "session_token" set for ${url}`);
    })
    .catch((error) => {
      console.error(error);
    });

  mainWindow.on('closed', function () {
    mainWindow.removeAllListeners('close');
    mainWindow = null;
  });
};

app.whenReady().then(() => {
  createWindow();
  session.defaultSession.cookies
    .get({ url: url })
    .then((cookies) => log.info('Cookies retrieved:', cookies))
    .catch((error) => log.info(error));
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();

  session.defaultSession.cookies
    .get({ url: url })
    .then((cookies) => log.info('Cookies retrieved:', cookies))
    .catch((error) => log.info(error));
});

app.on('before-quit', () => {
  log.info('App is about to quit, performing cleanup');
});

app.on('will-quit', () => {
  log.info('App is quitting, cleaning up resources');
});

app.on('quit', () => {
  log.info('App has quit, exiting process');
  app.exit(0);
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    log.info('All windows closed, quitting app');
    app.quit();
  }
});
