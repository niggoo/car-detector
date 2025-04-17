import { Routes } from '@angular/router';
import {HomeComponent} from './home/home.component';
import {ScanComponent} from './scan/scan.component';
import {BrowseCarsComponent} from './browse-cars/browse-cars.component';

export const routes: Routes = [
  {
    path: 'home',
    component: HomeComponent,
    title: "Home"
  },
  {
    path: 'scan',
    component: ScanComponent,
    title: "Scan Car"
  },
  {
    path: 'browse',
    component: BrowseCarsComponent,
    title: "Browse Cars"
  },
  {
    path: '',
    redirectTo: 'home',
    pathMatch: "full"
  }
];
