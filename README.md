https://hermercur.pythonanywhere.com/

This is my first web development project which is based on Django. You're welcome to take a look at the code.

What it does is very straightforward: You rate 10 movies on a 5-stars scale, then it recommends you a bunch of movies that'll (hopefully) suit your taste.

You can browse the site either by signing up, or by using a guest account. Use the latter option if you are worried about any security/privacy issues.

---

https://hermercur.pythonanywhere.com/

머신러닝과 TMDb API를 활용한 영화 추천 사이트입니다.

유저가 처음 로그인하면 먼저 영화를 10개 평가해 달라고 안내해 줍니다. 10개를 다 채운 후 "홈"으로 가면 추천 영화 목록이 계산되어서 나옵니다.

계정을 직접 생성하시거나, 혹은 편리하게 게스트 계정으로 로그인하셔서 사이트를 둘러보실 수 있습니다.

---

### CREDITS

- 본 사이트는 TMDb API를 사용합니다. 단, TMDb가 어떠한 보증 혹은 인증을 하지는 않습니다. ("This product uses the TMDb API but is not endorsed or certified by TMDb.")

- 머신 러닝에 사용된 영화 평점 및 태그 데이터는 The MovieLens Datasets에서 추출하였습니다.

- 영화 데이터의 일부(감독, 배우, 영문제목 등)는 IMDb Datasets에서 가져왔습니다.

- '별점 주기' 스크립트는 star-rating-svg를 개조하여 사용하였습니다. (https://github.com/nashio/star-rating-svg)

---

### 웹 개발 도구

- 백엔드: Django, Django REST framework, SQLite, etc

- 프론트엔드: jQuery, Bootstrap

---

### ML 알고리즘

추천 시스템은 MovieLens의 평점 및 태그 데이터를 기반으로 작동하며, 복수의 알고리즘이 함께 활용됩니다. [더 자세한 내용은 블로그에...](https://blog.naver.com/hermercur/221836101047)

#### 평점 예측

- matrix factorization 기반의 협업 필터링 시스템을 NumPy로 구현하여 사용합니다. 유저 평점 데이터를 바탕으로 전체 영화에 대한 예상 점수를 계산합니다.
  [더 자세한 내용은 블로그에...](https://blog.naver.com/hermercur/221803243551)

#### 비슷한 영화 찾기

- 영화 태그 데이터를 feature로 활용하여 영화 간 cosine similarity를 계산합니다. 유저가 직접 '비슷한 영화 보기' 버튼을 눌렀을 때뿐만 아니라 영화 추천에도 활용됩니다.
  [더 자세한 내용은 블로그에...](https://blog.naver.com/hermercur/221801410506)

#### 영화 자동 분류

- 추천 영화 목록은 hierarchical clustering을 통해 자동으로 분류됩니다. 먼저 비슷한 영화끼리 같은 그룹으로 묶은 뒤, 각 그룹을 대표하는 장르를 추출하여 유저에게 표시해 줍니다.

---

### 개발 목표

#### 머신러닝

- 저사양 웹서버에서 구동할 수 있는 실시간 추천 시스템을 구현하는 게 주요 목표였습니다. matrix factorization("Funk SVD") 기반 알고리즘을 NumPy로 직접 구현하였고, 학습된 파라미터들 중 신규 유저를 위한 실시간 추천에 필요한 파라미터만 남기고 모두 제거하여 '가볍게' 사용할 수 있도록 설계하였습니다.

- 또한 영화의 feature를 기반으로 아이템-아이템 유사도를 계산할 때는 PCA에 의한 차원축소를 적용하여 CPU와 메모리 부담을 최소화하였습니다.

#### 백엔드

- 다양한 출처의 데이터를 일관성 있게 관리할 수 있는 DB를 설계하는 게 가장 큰 과제였습니다. 여러 가지 설계 방안을 비교하며 검토하였고, '중복 데이터 최소화'와 '쿼리 단순화' 사이에서 합리적인 타협점을 찾아가는 과정을 연습해볼 수 있었습니다.

- HTTP 요청과 응답을 처리하는 일반적인 백엔드 로직으로부터 머신러닝 알고리즘을 최대한 숨겼습니다. Django view(MVC 패턴의 "controller"에 해당)에서는 머신러닝 알고리즘을 직접 호출하지 않고 별도의 인터페이스를 통해서만 해당 작업을 요청하도록 어플리케이션을 설계하였습니다.

#### 프론트엔드

- 사이트 특성상 한 화면에 다량의 콘텐츠와 이미지를 띄우게 되므로 성능에 대한 고려가 필수적이었습니다. 따라서 HTML 요소의 삽입 및 이미지 로딩을 브라우저 이벤트(스크롤 등)에 반응하여 최대한 lazy하게 처리하도록 구현하였습니다.

---

### 데이터 특징

이 프로젝트의 핵심이 되는 MovieLens 데이터에는 62,000개 영화에 대한 162,000명 유저들의 평점 및 태그 데이터가 들어 있습니다. 머신러닝 모델의 학습에 활용할 수 있는 데이터입니다. 이 중에서 실제 어플리케이션에 사용하기 적합한 9,500개 영화만 골라냅니다.

그리고 그 영화들에 해당하는 영화 정보(제목, 포스터 이미지, 장르 등)를 IMDb 혹은 TMDb 같은 영화 정보 사이트에서 가져오는데요. 미리 구해놓을 수 있는 데이터는 DB에 미리 입력해 놓고, 그럴 수 없는 데이터는 외부 API로부터 실시간으로 가져옵니다(단, 캐싱 목적으로 일정 기간 저장해 놓습니다).

이런 특성 때문에 2019년 12월까지 개봉된 영화들만 포함이 되어 있고, 그 이후 개봉된 영화들은 나오지 않습니다.
