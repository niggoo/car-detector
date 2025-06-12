import {Component, OnInit} from '@angular/core';
import {CarDetectorApiService} from '../service/car-detector-api/car-detector-api.service';
import {SessionService} from '../service/session.service';
import {ProfileInfo} from '../service/car-detector-api/profile-info';
import {Router} from '@angular/router';
import {NgForOf, NgIf} from '@angular/common';
import {environment} from '../../environments/environment';

@Component({
  selector: 'app-profile',
  imports: [
    NgForOf,
    NgIf
  ],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  profileInfo: ProfileInfo | null = null;
  apiUrl = environment.apiUrl;

  constructor(private service: CarDetectorApiService,
              private sessionService: SessionService,
              private router: Router) {
  }

  ngOnInit(): void {
    let currentUser = this.sessionService.getCurrentUser();
    if (currentUser == null) {
      this.router.navigate(["login"])
    } else {
      this.service.getProfileInfos(currentUser).subscribe(o => {
        this.profileInfo = o;
      });
    }
  }

  selectCarHandler(carPath: string) {
    this.router.navigate(["scan"], { queryParams: {carPath}});
    return false;
  }
}
