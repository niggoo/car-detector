import {Component, OnInit} from '@angular/core';
import {CarListComponent} from '../car-list/car-list.component';
import {CarDetectorApiService} from '../service/car-detector-api/car-detector-api.service';
import {CarListItem} from '../service/car-detector-api/car-list-item';
import {Router} from '@angular/router';

@Component({
  selector: 'app-browse-cars',
  imports: [
    CarListComponent
  ],
  templateUrl: './browse-cars.component.html',
  styleUrl: './browse-cars.component.css'
})
export class BrowseCarsComponent implements OnInit {
  private currentPage: number = 1;
  private pageSize: number = 8;
  private totalItems!: number;

  cars: Array<CarListItem> = [];

  constructor(private carDetectorApiService: CarDetectorApiService,
              private router: Router) {
  }

  ngOnInit(): void {
    this.fetchCars();
  }


  private fetchCars() {
    this.carDetectorApiService.getCars(this.currentPage, this.pageSize).subscribe({
      next: (response) => {
        this.cars = response.cars;
        this.currentPage = response.page;
        this.pageSize = response.page_size;
        this.totalItems = response.total_items;
      }
    });
  }

  next() {
    if (this.currentPage + 1 <= this.totalItems / this.pageSize) {
      this.currentPage++;
      this.fetchCars()
    }
  }

  prev() {
    if (this.currentPage - 1 >= 1) {
      this.currentPage--;
      this.fetchCars();
    }
  }

  carSelected(carId: number) {
    this.router.navigate(["scan"], { queryParams: {carId } });
  }
}
