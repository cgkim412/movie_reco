https://hermercur.pythonanywhere.com/

This is my first web development project which is based on Django. You're welcome to take a look at the code.

What it does is straight and simple: You rate 10 movies on a 5-stars scale, then it recommends you a bunch of movies that'll (hopefully) suit your taste.

You can browse the site by either signing up, or using a guest account. Use the latter option if you are worried about any security/privacy issues.

---

https://hermercur.pythonanywhere.com/

간단한 영화 추천 사이트입니다.

유저가 처음 로그인하면 먼저 영화를 10개 평가해 달라고 안내해 줍니다. 10개를 다 채운 후 "홈"으로 가면 추천 영화 목록이 계산되어서 나옵니다.

계정을 직접 생성하시거나, 혹은 자동생성되는 게스트 계정으로 로그인하셔서 사이트를 둘러보실 수 있습니다.

---

** 아래 내용은 실제 사이트 접속 후 '소개' 페이지로 가면 더 자세히 나와 있습니다. **

/////////// CREDITS ///////////

본 사이트는 TMDb API를 사용합니다. 단, TMDb가 어떠한 보증 혹은 인증을 하지는 않습니다. ("This product uses the TMDb API but is not endorsed or certified by TMDb.")

머신 러닝에 사용된 영화 평점 및 태그 데이터는 The MovieLens Datasets에서 추출하였습니다.

영화 데이터의 일부(감독, 배우, 영문제목 등)는 IMDb Datasets에서 가져왔습니다.

'별점 주기' 스크립트는 star-rating-svg를 개조하여 사용하였습니다. (https://github.com/nashio/star-rating-svg)

/////////////// 웹 개발 도구 ///////////////

백엔드: Django, Django REST framework, SQLite, etc

프론트엔드: jQuery, Bootstrap

////////////// ML 알고리즘 //////////////

추천 시스템은 MovieLens의 평점 및 태그 데이터를 기반으로 작동하며, 복수의 알고리즘이 함께 활용됩니다.

평점 예측: matrix factorization 기반의 협업 필터링 시스템을 NumPy로 구현하여 사용합니다. 유저 평점 데이터를 바탕으로 전체 영화에 대한 예상 점수를 계산합니다.

비슷한 영화 찾기: 영화 태그 데이터를 feature로 활용하여 영화 간 cosine similarity를 계산합니다. 유저가 직접 '비슷한 영화 보기' 버튼을 눌렀을 때뿐만 아니라 영화 추천에도 활용됩니다.

영화 자동 분류: 추천 영화 목록은 hierarchical clustering을 통해 자동으로 분류됩니다. 먼저 비슷한 영화끼리 같은 그룹으로 묶은 뒤, 각 그룹을 대표하는 장르를 추출하여 유저에게 표시해 줍니다.

//////////// 설계 과정 ////////////

이 프로젝트의 핵심이 되는 MovieLens 데이터에는 62,000개 영화에 대한 162,000명 유저들의 평점 및 태그 데이터가 들어 있습니다. 머신러닝 모델의 학습에 활용할 수 있는 데이터입니다. 이 중에서 실제 어플리케이션에 사용하기 적합한 9,500개 영화만 골라냅니다.

그리고 그 영화들에 해당하는 영화 정보(제목, 포스터 이미지, 장르 등)를 IMDb 혹은 TMDb 같은 영화 정보 사이트에서 가져오는데요. 미리 구해놓을 수 있는 데이터는 DB에 미리 입력해 놓고, 그럴 수 없는 데이터는 외부 API로부터 실시간으로 가져옵니다(단, 캐싱 목적으로 일정 기간 저장해 놓습니다).

이런 특성 때문에 2019년 12월까지 개봉된 영화들만 포함이 되어 있고, 그 이후 개봉된 영화들은 나오지 않습니다.

//////////// 개발 목표 ////////////

이 사이트는 웹 개발 겸 데이터 사이언스 프로젝트로 만들기 시작했습니다. 추천 알고리즘을 구현해서 머신러닝용 데이터에 적용해 보는 게 첫 번째 목표였고, 추천된 영화에 대한 정보를 표시할 수 있도록 웹 어플리케이션을 구축하는 게 두 번째 목표였습니다.

머신러닝 알고리즘을 적용할 때는 엔지니어링 측면을 많이 고려했는데요. 저사양 웹서버에서 구동된다는 점을 고려해서 "최소한의 연산으로 적당한 성능의 추천을 제공하자"라는 모토로 추천 시스템을 설계하였습니다. PCA로 데이터의 차원을 축소하거나, 일부 계산값을 DB에 미리 저장해놓는 등의 방법으로 연산량을 최소화하였습니다.

백엔드 개발을 할 때는 주로 데이터베이스 설계 과정을 연습해 보려고 했습니다. 데이터를 어떤 형식으로 저장할 것인지, 테이블을 어디까지 정규화할 것인지, '데이터 중복 최소화 vs 쿼리 단순화' 사이에서 어느 쪽을 선택할 것인지 등이 주된 고민이었습니다.

프론트엔드 개발은 사실 계획 없이 급하게 배워서 작업한 부분이라, 정리되지 않은 부분이 많습니다. 디자인적인 측면에는 비중을 두지 않았고 다만,

1. JavaScript를 통해 DOM 오브젝트를 조작하는 방법,
2. ajax의 비동기적 특성 이해하고 활용하기
3. element 삽입 및 이미지 로딩 lazy하게 처리하기
   등을 주로 연습해 보려고 했습니다.
