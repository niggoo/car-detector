import {CarListItem} from './car-list-item';

export interface SimilarityImageResponse {
  url: string,
  model: string,
  make: string,
  alternatives: Array<CarListItem>
}
