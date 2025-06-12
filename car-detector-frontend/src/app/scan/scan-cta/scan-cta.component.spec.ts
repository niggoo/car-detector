import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ScanCtaComponent } from './scan-cta.component';

describe('ScanCtaComponent', () => {
  let component: ScanCtaComponent;
  let fixture: ComponentFixture<ScanCtaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ScanCtaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ScanCtaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
