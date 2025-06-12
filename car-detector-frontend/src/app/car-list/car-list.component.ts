import {Component, input, numberAttribute, output} from '@angular/core';
import {NgForOf} from "@angular/common";
import {environment} from '../../environments/environment';
import {CarListItem} from '../service/car-detector-api/car-list-item';

@Component({
  selector: 'app-car-list',
    imports: [
        NgForOf
    ],
  templateUrl: './car-list.component.html',
  styleUrl: './car-list.component.css'
})
export class CarListComponent {
  public apiUrl = environment.apiUrl;
  public cars = input.required<Array<CarListItem>>();
  public carSelected = output<number>();


  selectCar(carId: number) {
    this.carSelected.emit(carId);
  }
}
