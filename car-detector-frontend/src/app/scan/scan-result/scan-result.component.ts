import {Component, input, Input, InputSignal, output} from '@angular/core';
import {SimilarityImageResponse} from '../../service/car-detector-api/similarity-image-response';
import {environment} from '../../../environments/environment';
import {CarListComponent} from '../../car-list/car-list.component';

@Component({
  selector: 'app-scan-result',
  imports: [
    CarListComponent
  ],
  templateUrl: './scan-result.component.html',
  styleUrl: './scan-result.component.css'
})
export class ScanResultComponent {
  imageSimilarityResult: InputSignal<SimilarityImageResponse> = input.required();
  carSelected = output<number>();
  reset = output<void>();
  public apiUrl = environment.apiUrl;

  carSelectedHandler(carId: number) {
    this.carSelected.emit(carId)
  }

  rescanAnotherHandler() {
    this.reset.emit();
  }
}
