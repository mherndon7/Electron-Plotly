import { Component } from '@angular/core';
import { PlotlyModule } from 'angular-plotly.js';

@Component({
  selector: 'app-root',
  imports: [PlotlyModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  readonly graph = {
    data: [
      {
        x: [1, 2, 3, 4, 5],
        y: [10, 8, 12, 10, 14],
        z: [5, 6, 7, 8, 9],
        mode: 'markers',
        marker: {
          size: 12,
          color: 'rgb(127, 127, 127)',
          opacity: 0.8,
        },
        type: 'scatter3d', // Key property for 3D scatter plot
      },
    ],
    layout: {
      autosize: true,
      title: '3D Scatter Plot Example',
      height: 300,
      width: 400,
      scene: {
        // Define 3D scene layout
        xaxis: { title: 'X Value' },
        yaxis: { title: 'Y Value' },
        zaxis: { title: 'Z Value' },
      },
      margin: { l: 0, r: 0, b: 0, t: 30 },
    },
  };
}
