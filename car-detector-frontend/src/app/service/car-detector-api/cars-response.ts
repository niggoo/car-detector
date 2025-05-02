import {CarListItem} from './car-list-item';

export interface CarsResponse {
  page: number;
  page_size: number;
  total_items: number;
  cars: Array<CarListItem>;
}
