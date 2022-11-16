from django.http import JsonResponse, HttpResponse
import requests
from .models import Genre, Movie, Actor
from django.shortcuts import get_list_or_404, render
from .serializer import MovieTitleSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view


#==================================


API_KEY = '184ad71ecc9874efbe281ead5597e503'
GENRE_URL = 'https://api.themoviedb.org/3/genre/movie/list'
POPULAR_MOVIE_URL = 'https://api.themoviedb.org/3/movie/popular'

def tmdb_genres():
    response = requests.get(
        GENRE_URL,
        params={
            'api_key': API_KEY,
            'language': 'ko-KR',            
        }
    ).json()    
    for genre in response.get('genres'):
        if Genre.objects.filter(pk=genre['id']).exists(): continue        
        print(genre)
        Genre.objects.create(
            id=genre['id'],
            name=genre['name']
        )
    return JsonResponse(response)


def get_youtube_key(movie_dict):    
    movie_id = movie_dict.get('id')
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}/videos',
        params={
            'api_key': API_KEY
        }
    ).json()
    for video in response.get('results'):
        if video.get('site') == 'YouTube':
            return video.get('key')
    return 'nothing'

def get_actors(movie):
    movie_id = movie.id
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}/credits',
        params={
            'api_key': API_KEY,
            'language': 'ko-kr',
        }
    ).json()
    
    for person in response.get('cast'):
        if person.get('known_for_department') != 'Acting': continue
        actor_id = person.get('id')
        if not Actor.objects.filter(pk=actor_id).exists():
            actor = Actor.objects.create(
                id=person.get('id'),
                name=person.get('name')
            )
        movie.actors.add(actor_id)
        if movie.actors.count() == 5:       # 5명의 배우 정보만 저장
            break

def movie_data(page=1):
    response = requests.get(
        POPULAR_MOVIE_URL,
        params={
            'api_key': API_KEY,
            'language': 'ko-kr',     
            'page': page,       
        }
    ).json()

    for movie_dict in response.get('results'):
        if not movie_dict.get('release_date'): continue   # 없는 필드 skip
        # 유투브 key 조회
        youtube_key = get_youtube_key(movie_dict)

        movie = Movie.objects.create(
            id=movie_dict.get('id'),
            title=movie_dict.get('title'),
            release_date=movie_dict.get('release_date'),
            popularity=movie_dict.get('popularity'),
            vote_count=movie_dict.get('vote_count'),
            vote_average=movie_dict.get('vote_average'),
            overview=movie_dict.get('overview'),
            poster_path=movie_dict.get('poster_path'),   
            youtube_key=youtube_key         
        )
        for genre_id in movie_dict.get('genre_ids', []):
            movie.genres.add(genre_id)

        # 배우들 저장
        get_actors(movie)
        print('>>>', movie.title, '==>', movie.youtube_key)    


def tmdb_data(request):
    Genre.objects.all().delete()
    Actor.objects.all().delete()
    Movie.objects.all().delete()

    tmdb_genres()
    for i in range(1, 6):
        movie_data(i)
    return HttpResponse('OK >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

@api_view(['GET'])
def movie_list(request):
    movies = get_list_or_404(Movie)
    serializer = MovieTitleSerializer(movies, many=True)
    return Response(serializer.data)
    
    
    
import pandas as pd 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# 줄거리 유사도로 영화 추천 
def overview_sim(request):
    movies = Movie.objects.all().values()
    data = pd.DataFrame(movies)
    print(data)
    data['overview'] = data['overview'].fillna('')
    print(data.overview)
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(data['overview'])
    print(tfidf.vocabulary_)
    print(tfidf_matrix)
    print('TF-IDF 행렬의 크기(shape) :',tfidf_matrix.shape)
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    print('코사인 유사도 연산 결과 :',cosine_sim.shape)
    print(cosine_sim)
    title_to_index = dict(zip(data['title'], data.index))
    print(title_to_index)
    #=========================================
    idx = title_to_index['20세기 소녀']
    print(idx)
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    print(sim_scores)
    movie_indices = [idx[0] for idx in sim_scores]
    print(movie_indices)
    print(data['title'].iloc[movie_indices])
    context = {
        'movies': movies
    }
    return JsonResponse(context)

# 제목 유사도로 영화 추천 
def title_sim(request):
    movies = Movie.objects.all().values()
    data = pd.DataFrame(movies)
    print(data)
    data['title'] = data['title'].fillna('')
    print(data.title)
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(data['title'])
    print(tfidf.vocabulary_)
    print(tfidf_matrix)
    print('TF-IDF 행렬의 크기(shape) :',tfidf_matrix.shape)
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    print('코사인 유사도 연산 결과 :',cosine_sim.shape)
    print(cosine_sim)
    title_to_index = dict(zip(data['title'], data.index))
    print(title_to_index)
    #=========================================
    idx = title_to_index['아바타']
    print(idx)
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    print(sim_scores)
    movie_indices = [idx[0] for idx in sim_scores]
    print(data['title'].iloc[movie_indices])

def genre_sim(request):
    movies = Movie.objects.all().values()

