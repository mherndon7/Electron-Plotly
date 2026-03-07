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

    win.webContents.session.cookies
      .set(cookieDetails)
      .then(() => {
        console.log('Cookie "session_token" set for localhost:4200');
      })
      .catch((error) => {
        console.error(error);
      });

    win.webContents.openDevTools();
    win.loadURL(url);
  } else {
    win.loadFile('dist/electron-app/browser/index.html');
  }
};

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();

      session.defaultSession.cookies
        .get({ url: 'http://localhost:4200' })
        .then((cookies) => {
          console.log('Cookies retrieved:', cookies);
        })
        .catch((error) => {
          console.log(error);
        });
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
