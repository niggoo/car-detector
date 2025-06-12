import {Component, OnInit} from '@angular/core';
import {CarDetectorApiService} from '../service/car-detector-api/car-detector-api.service';
import {NgIf} from '@angular/common';
import {ScanResultComponent} from './scan-result/scan-result.component';
import {environment} from '../../environments/environment';
import {SimilarityImageResponse} from '../service/car-detector-api/similarity-image-response';
import {ScanCtaComponent} from './scan-cta/scan-cta.component';
import {ActivatedRoute} from '@angular/router';

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
export class ScanComponent implements OnInit {
  public similarityImageResponse: SimilarityImageResponse | undefined;

  constructor(private route: ActivatedRoute,
              private carService: CarDetectorApiService) {
  }

ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      const carId = params['carId'];
      const carPath = params['carPath'];

      if (carId && carPath) {
        console.error('Both carId and carPath provided. Only one should be provided.');
      } else if (carId) {
        this.findSimilarCarsById(carId);
      } else if (carPath) {
        this.findSimilarCarsByPath(carPath);
      }
    });
  }


  private findSimilarCarsById(carId: number) {
    this.carService.findSimilarCarsById(carId).subscribe(o => {
      this.similarityImageResponse = o;
    });
  }


  private findSimilarCarsByPath(carPath: string) {
    this.carService.findSimilarCarsByPath(carPath).subscribe(o => {
      this.similarityImageResponse = o;
    });
  }

  uploadChanged($event: SimilarityImageResponse) {
    this.similarityImageResponse = $event;
  }

  carSelectedHandler(carId: number) {
    this.findSimilarCarsById(carId);
  }
}
