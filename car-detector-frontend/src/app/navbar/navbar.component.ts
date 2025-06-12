import { Component } from '@angular/core';
import {NgClass, NgIf} from '@angular/common';
import {Router, RouterLink} from '@angular/router';
import {SessionService} from '../service/session.service';

@Component({
  selector: 'app-navbar',
  imports: [
    NgIf,
    NgClass,
    RouterLink
  ],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent {
  isOpen = false;
  isLoggedIn: boolean = false;

  constructor(private sessionService: SessionService,
              private router: Router) {
    this.sessionService.userId$.subscribe(userId => {
      this.isLoggedIn = userId !== null;
    })
  }

  toggleMenu() {
    this.isOpen = !this.isOpen;
  }

  logoutHandler() {
    this.sessionService.reset();
    this.router.navigate([""]);
  }
}
