import { Component, ChangeDetectorRef } from '@angular/core';
import { CarDetectorApiService } from '../service/car-detector-api/car-detector-api.service';
import { Router } from '@angular/router';
import { SessionService } from '../service/session.service';
import { FormsModule } from '@angular/forms';
import {NgIf} from '@angular/common';

@Component({
  selector: 'app-login-register',
  imports: [
    FormsModule,
    NgIf
  ],
  templateUrl: './login-register.component.html',
  styleUrl: './login-register.component.css'
})
export class LoginRegisterComponent {
  email: string = "";
  password: string = "";
  emailError: string | null = null;
  passwordError: string | null = null;

  constructor(
    private carDetectorService: CarDetectorApiService,
    private sessionService: SessionService,
    private router: Router
  ) {}

  validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  validatePassword(password: string): boolean {
    return password.length >= 8;
  }

  onEmailChange() {
    if (!this.validateEmail(this.email)) {
      this.emailError = "Please enter a valid email address.";
    } else {
      this.emailError = null;
    }
  }

  onPasswordChange() {
    if (!this.validatePassword(this.password)) {
      this.passwordError = "Password must be at least 8 characters long.";
    } else {
      this.passwordError = null;
    }
  }

  loginHandler() {
    console.log("login try")
    if (!this.validateInputs()) return;

    this.carDetectorService.login(this.email, this.password).subscribe({
      next: (r) => {
        this.sessionService.setCurrentUser(r.user_id);
        this.router.navigate(["profile"]);
      },
      error: (error) => {
        console.error('Login failed:', error);
        alert('Login failed. Please check your credentials.');
      }
    });
  }

  registerHandler() {
    if (!this.validateInputs()) return;

    this.carDetectorService.signup(this.email, this.password).subscribe({
      next: (r) => {
        this.sessionService.setCurrentUser(r.user_id);
        this.router.navigate(["scan"]);
      },
      error: (error) => {
        console.error('Registration failed:', error);
        alert('Registration failed. Please try again.');
      }
    });
  }

  validateInputs(): boolean {
    let isValid = true;
    if (!this.validateEmail(this.email)) {
      isValid = false;
    }
    if (!this.validatePassword(this.password)) {
      isValid = false;
    }
    return isValid;
  }
}
