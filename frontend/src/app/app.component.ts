import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { environment } from '../environments/environment';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'frontend';
  apiUrl = environment.apiUrl;

  // Dynamic State variables for the Dashboard
  activeProject = 'Project Alpha (E-commerce)';
  systemStatus = 'All Systems Go';

  approvalQueue: any[] = [];
  swarmLogs: { time: string, agent: string, message: string, color: string }[] = [];

  constructor() {
    // We will soon fetch this from the Django API, but for now we initialize empty sets
    // to prove the UI is dynamic and no longer hardcoded dummies.
  }
}
