import { Routes } from '@angular/router';
import {HomeComponent} from './home/home.component';
import {ScanComponent} from './scan/scan.component';
import {BrowseCarsComponent} from './browse-cars/browse-cars.component';
import {LoginRegisterComponent} from './login-register/login-register.component';
import {ProfileComponent} from './profile/profile.component';

export const routes: Routes = [
  {
    path: 'home',
    component: HomeComponent,
    title: "Home"
  },
  {
    path: 'login-register',
    component: LoginRegisterComponent,
    title: "Login / Register"
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
    path: 'profile',
    component: ProfileComponent,
    title: "My Profile"
  },
  {
    path: '',
    redirectTo: 'home',
    pathMatch: "full"
  }
];
