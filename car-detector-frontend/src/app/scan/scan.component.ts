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
  public similarityImageResponse: SimilarityImageResponse | undefined | null;
  public isLoading: boolean = false; // Add loading state

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
    this.isLoading = true; // Set loading to true before API call
    this.carService.findSimilarCarsById(carId).subscribe({
      next: (o) => {
        this.similarityImageResponse = o;
        this.isLoading = false; // Set loading to false when API call is successful
      },
      error: (err) => {
        console.error('Error finding similar cars by ID: ', err);
        this.isLoading = false; // Also set loading to false if there's an error
      }
    });
  }

  private findSimilarCarsByPath(carPath: string) {
    this.isLoading = true; // Set loading to true before API call
    this.carService.findSimilarCarsByPath(carPath).subscribe({
      next: (o) => {
        this.similarityImageResponse = o;
        this.isLoading = false; // Set loading to false when API call is successful
      },
      error: (err) => {
        console.error('Error finding similar cars by path: ', err);
        this.isLoading = false; // Also set loading to false if there's an error
      }
    });
  }

  uploadChanged($event: SimilarityImageResponse) {
    this.isLoading = true; // Set loading to true
    this.similarityImageResponse = $event;
    this.isLoading = false; // Set loading to false as the response is already received
  }

  carSelectedHandler(carId: number) {
    this.findSimilarCarsById(carId);
  }

  resetHandler() {
    this.similarityImageResponse = null;
  }
}
