import {Component} from '@angular/core';
import {CarDetectorApiService} from '../service/car-detector-api/car-detector-api.service';
import {NgIf} from '@angular/common';
import {ScanResultComponent} from './scan-result/scan-result.component';
import {environment} from '../../environments/environment';
import {UploadImageResponse} from '../service/car-detector-api/upload-image-response';
import {ScanCtaComponent} from './scan-cta/scan-cta.component';

@Component({
  selector: 'app-scan',
  imports: [
    NgIf,
    ScanResultComponent,
    ScanCtaComponent
  ],
  templateUrl: './scan.component.html',
  styleUrl: './scan.component.css'
})
export class ScanComponent {
  public uploadResponse: UploadImageResponse | undefined;

  uploadChanged($event: UploadImageResponse) {
    this.uploadResponse = $event;
  }
}
