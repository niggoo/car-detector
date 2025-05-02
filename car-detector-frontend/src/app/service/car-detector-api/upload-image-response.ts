import {CarListItem} from './car-list-item';

export interface UploadImageResponse {
  url: string,
  model: string,
  make: string,
  alternatives: Array<CarListItem>
}
