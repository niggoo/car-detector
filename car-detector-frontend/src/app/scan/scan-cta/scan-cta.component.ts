import {Component, output, Output, OutputEmitterRef} from '@angular/core';
import {CarDetectorApiService} from '../../service/car-detector-api/car-detector-api.service';
import {SimilarityImageResponse} from '../../service/car-detector-api/similarity-image-response';
import {SessionService} from '../../service/session.service';

@Component({
  selector: 'app-scan-cta',
  imports: [],
  templateUrl: './scan-cta.component.html',
  styleUrl: './scan-cta.component.css'
})
export class ScanCtaComponent {
  uploadResponse: OutputEmitterRef<SimilarityImageResponse> = output<SimilarityImageResponse>();

  constructor(private carDetectorApiService: CarDetectorApiService,
              private sessionService: SessionService) {
  }

  onFileSelected(event: any): void {
    const file: File = event.target.files[0];
    if (file) {
      this.uploadImage(file);
    }
  }

  uploadImage(file: File): void {
    this.carDetectorApiService.uploadImage(file, this.sessionService.getCurrentUser()).subscribe({
      next: (response) => {
        this.uploadResponse.emit(response);
      },
      error: (e) => console.error(e),
    });
  }
}
