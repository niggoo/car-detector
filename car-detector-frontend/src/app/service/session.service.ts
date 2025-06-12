import { Injectable } from '@angular/core';
import {BehaviorSubject} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SessionService {

  private userIdSubject = new BehaviorSubject<string | null>(null);
  public userId$ = this.userIdSubject.asObservable();

  constructor() {
    const currentUserId = localStorage.getItem("userId");
    if (currentUserId) {
      this.userIdSubject.next(currentUserId);
    }
  }

  setCurrentUser(userId: string) {
    localStorage.setItem("userId", userId);
    this.userIdSubject.next(userId);
  }

  getCurrentUser() {
    let userId = localStorage.getItem("userId");
    return userId == null || userId == "" ? null : userId;
  }

  reset() {
    localStorage.removeItem("userId");
    this.userIdSubject.next(null);
  }
}
