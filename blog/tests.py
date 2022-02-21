from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

class TestView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_list(self):
        # 포스트 목록 페이지 가져오기
        response = self.client.get('/blog/')

        # 페이지 로드되는 것 확인
        self.assertEqual(response.status_code, 200)

        # 페이지 타이틀 이름 == Blog
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')

        # 네비게이션 바가 있다.
        navbar = soup.nav

        # Blog, About Me라는 문구가 네비게이션 바에 존재하는지 확인
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        # 메인 영역에 게시물이 하나도 없으면
        self.assertEqual(Post.objects.count(), 0)

        # '아직 게시물이 없습니다.' 라는 문구가 보이는지 확인
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

        # 게시물이 두 개 있다면
        post_001 = Post.objects.create(
            title = '첫 번째 포스트입니다.',
            content = 'Hello World!'
        )
        post_002 = Post.objects.create(
            title = '두 번째 포스트입니다.',
            content = 'Nice to meet you.'
        )
        self.assertEqual(Post.objects.count(), 2)

        # 포스트 목록 페이지를 새로고침했을 때에
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)

        # 메인 영역에 포스트 2개의 제목이 존재한다.
        main_area = soup.find('div', id = 'main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)

        # '아직 게시물이 없습니다.' 라는 문구는 더이상 보이지 않아야 한다.
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)


    def test_post_detail(self):
        # 포스트가 하나 있다.
        post_001 = Post.objects.create(
            title = "첫 번째 포스트입니다.",
            content = "Hello, World!"
        )

        # 그 포스트의 url은 blog/1/이다.
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        # 첫 번째 post url로 접근하면 정상적으로 작동한다.
        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 포스트 목록 페이지와 똑같은 네비게이션 바가 있다.
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        # 첫 번째 포스트의 제목이 웹 브라우저 타이틀의 탭에 들어 있다.
        self.assertIn(post_001.title, soup.title.text)

        # 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(post_001.title, post_area.text)

        # 첫 번째 포스트의 작성자가 포스트 영역에 있다.


        # 첫 번째 포스트의 내용이 포스트 영역에 있다.
        self.assertIn(post_001.content, post_area.text)
