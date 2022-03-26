from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

class TestView(TestCase):
    def setUp(self):
        # 임의의 사용자 만들기
        self.client = Client()
        self.user_user1 = User.objects.create_user(username='user1', password='somepassword')
        self.user_user2 = User.objects.create_user(username='user2', password='somepassword')

        # 사용자1에 스태프 권한 부여
        self.user_user1.is_staff = True
        self.user_user1.save()

        # 임의의 카테고리 만들기
        self.category_python = Category.objects.create(name='python', slug='python')
        self.category_javascript = Category.objects.create(name='javascript', slug='javascript')

        # 임의의 태그 만들기
        self.tag_rust_kor = Tag.objects.create(name='러스트 공부', slug='러스트 공부')
        self.tag_go = Tag.objects.create(name='go', slug='go')
        self.tag_js = Tag.objects.create(name='js', slug='js')

        # 임의의 포스트 3개 만들기
        self.post_001 = Post.objects.create(
            title = '첫 번째 포스트입니다.',
            content = 'Hello World!',
            category=self.category_python,
            author = self.user_user1
        )
        # 태그 붙여주기
        self.post_001.tags.add(self.tag_rust_kor)

        self.post_002 = Post.objects.create(
            title = '두 번째 포스트입니다.',
            content = 'Nice to meet you.',
            category=self.category_javascript,
            author=self.user_user2
        )
        # 태그가 없을 수도 있음

        # 아래의 포스트는 카테고리를 지정해두지 않음
        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='category가 없을 수도 있죠',
            author=self.user_user2
        )
        #태그가 여러 개일 수도 있음
        self.post_003.tags.add(self.tag_go)
        self.post_003.tags.add(self.tag_js)


    # 네비게이션 바 테스트 코드
    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog',navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    # 카테고리 카드 테스트 코드
    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card') # 카테고리 카드인 곳을 찾아낸다.
        self.assertIn('Categories', categories_card.text) # 카테고리 카드 부분에 다음의 문구가 있는지 확인

        # 카테고리 카드 부분에 위에서 만들어 놓은 카테고리와 카테고리 포스트 갯수의 수가 표시되는지 확인
        self.assertIn(f'{self.category_python.name} ({self.category_python.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_javascript.name} ({self.category_javascript.post_set.count()})', categories_card.text)
        # 미분류인 포스트도 잘 표시되는지 확인
        self.assertIn(f'미분류 (1)', categories_card.text)

    # 포스트 리스트 페이지 테스트 코드
    def test_post_list(self):

        # 포스트가 있는 경우

        # 위에서 만든 포스트 갯수가 3과 같은지 확인
        self.assertEqual(Post.objects.count(), 3)

        # /blog/ 에 접속했을 때에
        response = self.client.get('/blog/')

        # 정상적으로 접속되는지 확인
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        # 게시물이 있는 경우이므로 아래의 문구가 표시되지 않는지 확인
        main_area = soup.find('div', id = 'main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        # 카테고리가 있는 포스트의 경우, 제목과 카테고리명이 카테고리 카드 안에 포함되어 있는지 확인
        #태그 테스트하는 코드 추가
        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_rust_kor.name, post_001_card.text)
        self.assertNotIn(self.tag_js.name, post_001_card.text)
        self.assertNotIn(self.tag_go.name, post_001_card.text)


        # 카테고리가 있는 포스트의 경우, 제목과 카테고리명이 카테고리 카드 안에 포함되어 있는지 확인
        # 태그 테스트하는 코드 추가
        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_rust_kor.name, post_002_card.text)
        self.assertNotIn(self.tag_js.name, post_002_card.text)
        self.assertNotIn(self.tag_go.name, post_002_card.text)

        # 포스트 카드 안에 '미분류' 라는 문구가 있는지, 미분류인 포스트의 제목이 포함되어 있는지 확인
        # 태그 테스트하는 코드 추가
        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)
        self.assertNotIn(self.tag_rust_kor.name, post_003_card.text)
        self.assertIn(self.tag_js.name, post_003_card.text)
        self.assertIn(self.tag_go.name, post_003_card.text)

        # 작성자의 이름이 대문자로 포함되어 있는지 확인
        self.assertIn(self.user_user1.username.upper(), main_area.text)
        self.assertIn(self.user_user2.username.upper(), main_area.text)


        # 포스트가 없는 경우 테스트

        # 포스트 모두 삭제
        Post.objects.all().delete()

        # 포스트 갯수가 0개인지 확인
        self.assertEqual(Post.objects.count(), 0)

        # /blog/ 에 접속
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id="main-area")

        # /blog/의 main-area 에 '아직 게시물이 없습니다' 라는 문구가 나오는 지 확인
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):

        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post_001.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_python.name, post_area.text)

        self.assertIn(self.user_user1.username.upper(), post_area.text)
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_rust_kor.name, post_area.text)
        self.assertNotIn(self.tag_js.name, post_area.text)
        self.assertNotIn(self.tag_go.name, post_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_python.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_python.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_python.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_rust_kor.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_rust_kor.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_rust_kor.name, main_area.text)

        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)


    def test_create_post(self):
        # 로그인하지 않으면 status code != 200
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff 가 아닌 사용자, user2가 로그인
        self.client.login(username='user2', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff인 user1가 로그인
        self.client.login(username='user1', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        # 태그 테스트
        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title' : 'Post Form 만들기',
                'content' : 'Post Form 페이지를 만듭시다.',
                'tags_str' : 'new tag; 한글 태그, js'
            }
        )
        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, 'user1')

        # 마지막 게시물의 태그가 3개가 맞는가?
        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(), 5)

    def test_update_post(self):

        # 포스트 003 작성자 = user2

        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인하지 않은 경우에는 수정 페이지에 접근이 불가능해야 함
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인은 했지만 작성자가 아닌 경우에는 수정 페이지에 접근했을 때에 403 코드(권한 없음) 이 나타나야 함
        self.assertNotEqual(self.post_003.author, self.user_user1) # 포스트3의 작성자가 user2가 아닌지 확인
        self.client.login(
            username=self.user_user1.username,
            password='somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # 작성자가 접근하는 경우, 수정이 가능해야 함
        self.client.login(
            username=self.post_003.author.username,
            password='somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        response = self.client.post(
            update_post_url,
            {
                'title' : '세 번째 포스트 수정하기',
                'content' : '안녕하세요',
                'category' : self.category_python.pk
            },
            follow=True
        )

        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트 수정하기', main_area.text)
        self.assertIn('안녕하세요', main_area.text)
        self.assertIn(self.category_python.name, main_area.text)