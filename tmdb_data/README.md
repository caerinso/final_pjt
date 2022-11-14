### TMDB DATA

- 설정

```bash
$ python -m venv venv
                            # 가상환경 설정
$ pip install -r requirements.txt

$ python manage.py makemgirations

$ python manage.py migrate

$ python manage.py runserver
```



- TMDB API KEY 

```
**movies/tmdb_views.py** 파일에서 API_KEY에 TMDB API KEY 설정 
```



- view함수 실행하기

```markdown
- 서버 실행하기 

- **movies/tmdb_views.py**  파링의 tmdb_data() 실행 
```



- dump

```bash
$ mkdir movies/fixtures
$ python -Xutf8 manage.py dumpdata movies --indent 4 > ./movies/fixtures/movies.json
```

- load

```bash
$ python manage.py loaddata movies.json
```
