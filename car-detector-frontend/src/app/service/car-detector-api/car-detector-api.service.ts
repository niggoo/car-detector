import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import { Observable } from 'rxjs';
import {SimilarityImageResponse} from './similarity-image-response';
import {environment} from '../../../environments/environment';
import {CarsResponse} from './cars-response';
import {ProfileInfo} from './profile-info';

@Injectable({
  providedIn: 'root'
})
export class CarDetectorApiService {

  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  signup(username: string, password: string): Observable<{ user_id: string }> {
    return this.http.post<{ user_id: string }>(`${this.apiUrl}/signup/`, { username, password });
  }

  login(username: string, password: string): Observable<{ user_id: string }> {
    return this.http.post<{ user_id: string }>(`${this.apiUrl}/login/`, { username, password });
  }

  uploadImage(file: File, userId: string | null): Observable<SimilarityImageResponse> {
      const formData = new FormData();
      formData.append('file', file);

      let headers = new HttpHeaders();

      if (userId !== null) {
        headers = headers.append('Authorization', `Bearer ${userId}`);
      }

      return this.http.post<SimilarityImageResponse>(
        `${this.apiUrl}/upload-image/`,
        formData,
        { headers: headers }
      );
  }


  findSimilarCarsById(carId: number): Observable<SimilarityImageResponse> {
    return this.http.get<SimilarityImageResponse>(`${this.apiUrl}/find-similar/?car_id=${carId}`);
  }

  findSimilarCarsByPath(carPath: string): Observable<SimilarityImageResponse> {
    return this.http.get<SimilarityImageResponse>(`${this.apiUrl}/find-similar/?car_path=${carPath}`);
  }

  getCars(page: number = 1, pageSize: number = 10): Observable<CarsResponse> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
    return this.http.get<CarsResponse>(`${this.apiUrl}/cars/`, { params });
  }

  getProfileInfos(userId: string): Observable<ProfileInfo> {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${userId}`
    });

    return this.http.get<ProfileInfo>(`${this.apiUrl}/profile/`, { headers });
  }
}
