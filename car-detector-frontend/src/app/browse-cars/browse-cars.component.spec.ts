import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BrowseCarsComponent } from './browse-cars.component';

describe('BrowseCarsComponent', () => {
  let component: BrowseCarsComponent;
  let fixture: ComponentFixture<BrowseCarsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BrowseCarsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BrowseCarsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
