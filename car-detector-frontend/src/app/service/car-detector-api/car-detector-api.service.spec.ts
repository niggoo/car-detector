import { TestBed } from '@angular/core/testing';

import { CarDetectorApiService } from './car-detector-api.service';

describe('CarDetectorApiService', () => {
  let service: CarDetectorApiService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CarDetectorApiService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
