import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { PlotlyModule } from 'angular-plotly.js';
// @ts-ignore
import Plotly from 'plotly.js-dist-min';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    ...(PlotlyModule.forRoot(Plotly).providers ?? []),
  ],
};
