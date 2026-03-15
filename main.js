const { app, BrowserWindow, session } = require('electron');
const log = require('electron-log');
const path = require('path');
const childProcess = require('child_process');

// Launch server from python script
const useScript = process.argv.includes('script');

// Development vs Production URL
const electronIsDev = path.basename(app.getPath('exe')) === 'electron.exe';
const isDevelopment = process.argv.includes('development');
let port = isDevelopment ? 4200 : 8080;
const createUrl = () => `http://localhost:${port}`;

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
log.transports.file.resolvePathFn = () =>
  electronIsDev
    ? path.join(__dirname, 'electron-log.log')
    : path.join(__dirname, '..', '..', '..', '..', 'electron-log.log');
log.transports.file.format = logFormat;
log.transports.console.format = logFormat;

Object.assign(console, log.functions);

// Chrome Flags
app.commandLine.appendSwitch('enable-logging');
// app.commandLine.appendSwitch('v', '4');
app.commandLine.appendSwitch('no-sandbox');
app.commandLine.appendSwitch('ignore-gpu-blacklist');
app.commandLine.appendSwitch('enable-gpu-rasterization');

let cookieMatch;
let portMatch;
let serverProcess;

const startServer = () => {
  if (useScript) {
    serverProcess = childProcess.execFile('python', ['-m', 'server', 'server']);
  } else {
    let exePath;
    if (electronIsDev) {
      exePath = path.join(__dirname, 'deployment', 'ElectronServer', 'ElectronServer.exe');
    } else {
      exePath = path.join(app.getAppPath(), '..', '..', 'extras', 'ElectronServer.exe');
    }
    log.debug(`Executable Path: ${exePath}`);
    serverProcess = childProcess.execFile(exePath, ['server']);
  }

  serverProcess.stdout.on('data', (data) => {
    output = data.toString().trim();
    log.info(`Python output: ${output}`);

    // Split the value to extract the cookie name and value
    const cookieRegex = /^Cookie::(?<cookie_name>[^:]+)::(?<cookie_value>.*)$/gm;
    cookieMatch = cookieMatch ?? cookieRegex.exec(output);

    startApp();
  });

  serverProcess.stderr.on('data', (data) => {
    output = data.toString().trim();
    log.error(`Python error: ${output}`);

    // Find the port the server is listening on
    const portRegex = /^.*?Listening on port (?<port>\d+)\.\.\./gm;
    portMatch = portMatch ?? portRegex.exec(output);
    startApp();
  });

  serverProcess.on('close', (code) => {
    log.info(`Python process exited with code ${code}`);
    if (mainWindow) app.quit();
  });
};

const startApp = () => {
  if (!cookieMatch || !portMatch || BrowserWindow.getAllWindows().length > 0) return;

  log.debug(`Cookie Name: ${cookieMatch.groups.cookie_name}`);
  log.debug(`Cookie Value: ${cookieMatch.groups.cookie_value}`);
  port = portMatch.groups.port;

  createWindow(cookieMatch.groups.cookie_name, cookieMatch.groups.cookie_value);

  session.defaultSession.cookies
    .get({ url: createUrl() })
    .then((cookies) => log.info('Cookies retrieved:', cookies))
    .catch((error) => log.info(error));
};

let mainWindow;
const createWindow = (name, value) => {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    // autoHideMenuBar: true,
  });

  if (isDevelopment) log.info('Developer mode enabled: loading from localhost:4200');

  const url = createUrl();
  log.debug(`Loading URL ${url}...`);
  mainWindow.webContents.openDevTools();
  mainWindow.loadURL(url);

  if (name && value) {
    const cookieDetails = {
      url: url, // The URL to associate the cookie with
      name: name,
      value: value,
      secure: true,
      httpOnly: true,
    };

    mainWindow.webContents.session.cookies
      .set(cookieDetails)
      .then(() => log.info(`Cookie "${name}" set for ${url}`))
      .catch((error) => console.error(error));
  }

  mainWindow.on('closed', () => {
    mainWindow.removeAllListeners('close');
    mainWindow = null;
  });
};

app.whenReady().then(() => {
  log.info('Starting Electron app');

  // Create window without cookies and server in development mode
  if (isDevelopment) createWindow();
  else startServer();
});

app.on('before-quit', async () => {
  try {
    log.info('App is about to quit, performing cleanup');
    if (serverProcess) serverProcess.kill();

    if (!useScript) {
      log.debug(`Killing server processes...`);
      killProcess('ElectronServer');
    }
  } catch (error) {
    log.error('Error in handleData:', error);
  }
});

app.on('will-quit', () => {
  log.info('App is quitting, cleaning up resources');
});

app.on('quit', () => {
  log.info('App has quit, exiting process');
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    log.info('All windows closed, quitting app');
    app.quit();
  }
});

function killProcess(name) {
  switch (process.platform) {
    case 'win32':
      childProcess.exec(`taskkill /F /IM ' ${name}.exe /T`);
      break;
    default: //Linux + Darwin
      childProcess.exec(`pkill -f ${name}`);
      break;
  }
}
