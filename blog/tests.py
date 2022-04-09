from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment


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
            title='첫 번째 포스트입니다.',
            content='Hello World!',
            category=self.category_python,
            author=self.user_user1
        )
        # 태그 붙여주기
        self.post_001.tags.add(self.tag_rust_kor)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='Nice to meet you.',
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
        # 태그가 여러 개일 수도 있음
        self.post_003.tags.add(self.tag_go)
        self.post_003.tags.add(self.tag_js)

        # user1이 post_001에 작성한 임의의 댓글 작성
        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_user1,
            content='first comment.'
        )

    # 네비게이션 바 테스트 코드
    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
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
        categories_card = soup.find('div', id='categories-card')  # 카테고리 카드인 곳을 찾아낸다.
        self.assertIn('Categories', categories_card.text)  # 카테고리 카드 부분에 다음의 문구가 있는지 확인

        # 카테고리 카드 부분에 위에서 만들어 놓은 카테고리와 카테고리 포스트 갯수의 수가 표시되는지 확인
        self.assertIn(f'{self.category_python.name} ({self.category_python.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_javascript.name} ({self.category_javascript.post_set.count()})',
                      categories_card.text)
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
        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        # 카테고리가 있는 포스트의 경우, 제목과 카테고리명이 카테고리 카드 안에 포함되어 있는지 확인
        # 태그 테스트하는 코드 추가
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

        # comment
        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)

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
                'title': 'Post Form 만들기',
                'content': 'Post Form 페이지를 만듭시다.',
                'tags_str': 'new tag; 한글 태그, js'
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
        self.assertNotEqual(self.post_003.author, self.user_user1)  # 포스트3의 작성자가 user2가 아닌지 확인
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

        # 태그 테스트
        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('go; js', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트 수정하기',
                'content': '안녕하세요',
                'category': self.category_python.pk,
                'tags_str': '파이썬 공부; 한글 태그, some tag'
            },
            follow=True
        )

        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트 수정하기', main_area.text)
        self.assertIn('안녕하세요', main_area.text)
        self.assertIn(self.category_python.name, main_area.text)

        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('js', main_area.text)  # 기존의 태그는 없어야 함

    def test_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)  # 전체 댓글 하나
        self.assertEqual(self.post_001.comment_set.count(), 1)  # 포스트1의 댓글 하나

        # 로그인 X
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertIn('Log in and leave a comment', comment_area.text)  # 로그인 안 한 상태면 위의 문구가 보여야 함
        self.assertFalse(comment_area.find('form', id='comment-form'))  # 로그인 안 한 상태면 댓글 폼이 보이지 않아야 함

        # 로그인 O
        self.client.login(username='user1', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('Log in and leave a comment', comment_area.text)  # 로그인했다면 위의 문구가 보이지 않아야 함

        comment_form = comment_area.find('form', id='comment-form')
        self.assertTrue(comment_form.find('textarea', id='id_content'))
        response = self.client.post(
            self.post_001.get_absolute_url() + 'new_comment/',
            {
                'content': "example comment.",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

    def test_comment_update(self):
        comment_by_user2 = Comment.objects.create( # 다른 사람이 만든 댓글 생성(유저2)
            post=self.post_001,
            author=self.user_user2,
            content='''this is user2's comment.'''
        )

        response = self.client.get(self.post_001.get_absolute_url()) # 로그인하지 않은 상태에서 댓글이 2개 있는 페이지 열기
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area') # 댓글 영역에 수정 버튼 2개가 보이지 않아야 함
        self.assertFalse(comment_area.find('a', id='comment-1-update-btn'))
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))

        # 로그인 O
        self.client.login(username='user1', password='somepassword') # 유저1로 로그인
        response=self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn')) # 유저 1이 작성한 comment-1-update-btn만 보여야 함
        comment_001_update_btn = comment_area.find('a', id='comment-1-update-btn')
        self.assertIn('edit', comment_001_update_btn.text)
        self.assertEqual(comment_001_update_btn.attrs['href'], '/blog/update_comment/1/')

        self.assertIn('edit', comment_001_update_btn.text)
        self.assertEqual(comment_001_update_btn.attrs['href'], '/blog/update_comment/1/')

        response = self.client.get('/blog/update_comment/1/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Comment - Blog', soup.title.text)
        update_comment_form = soup.find('form', id='comment-form')
        content_textarea = update_comment_form.find('textarea',id='id_content')
        self.assertIn(self.comment_001.content, content_textarea.text)

        response = self.client.post(
            f'/blog/update_comment/{self.comment_001.pk}/',
            {
                'content' : '댓글 수정 테스트.',
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_001_div = soup.find('div', id='comment-1')
        self.assertIn('댓글 수정 테스트.', comment_001_div.text)
        # 수정일시 != 작성일시 일 때에 수정일시 나타나는지 테스트 코드
        # self.assertIn('Updated :', comment_001_div.text)


    def test_delete_comment(self):
        '''
        user 1 : post001 에 'first comment.' 작성
        user 2 : post001 에 'comment by user2.' 작성
        '''
        comment_by_user2 = Comment.objects.create( # user2가 post_001에 작성한 임의의 댓글 작성
            post = self.post_001,
            author = self.user_user2,
            content = 'comment by user2.'
        )

        self.assertEqual(Comment.objects.count(), 2) # setup함수에서 작성한 댓글 + 위에서 작성한 댓글 = 총 2개의 댓글이 되어야 함
        self.assertEqual(self.post_001.comment_set.count(), 2) # 포스트 001에 달린 댓글이 2개여야 함

        #로그인 X
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn')) # 로그인하지 않은 경우 삭제 버튼이 없어야 함
        self.assertFalse(comment_area.find('a', id='comment-2-delete-btn')) # 로그인하지 않은 경우 삭제 버튼이 없어야 함

        # user2로 로그인
        self.client.login(username='user2', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn')) # user2가 작성하지 않은 댓글의 경우, 삭제 버튼이 없어야 함
        comment_002_delete_modal_btn = comment_area.find(
            'a', id='comment-2-delete-modal-btn'
        )
        self.assertIn('delete', comment_002_delete_modal_btn.text) # 모달 버튼에 'delete'라는 문구가 있어야 함
        self.assertEqual( # data-target 속성이 '#deleteCommentModal-2' 와 같아야 함
            comment_002_delete_modal_btn.attrs['data-target'],
            '#deleteCommentModal-2'
        )

        delete_comment_modal_002 = soup.find('div', id='deleteCommentModal-2')
        self.assertIn('Are you sure?', delete_comment_modal_002.text) # 모달 창에 정말 삭제할 것인지를 묻는 문구가 있는지를 확인
        really_delete_btn_002 = delete_comment_modal_002.find('a')
        self.assertIn('Delete', really_delete_btn_002.text)
        self.assertEqual(
            really_delete_btn_002.attrs['href'],
            '/blog/delete_comment/2/'
        )

        response = self.client.get('/blog/delete_comment/2/', follow=True) # 댓글 삭제 요청
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(self.post_001.title, soup.title.text)
        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('comment by user2.', comment_area.text) # 삭제한 이후에는 댓글의 내용이 보이지 않야야 함

        self.assertEqual(Comment.objects.count(), 1) # 댓글 2개 중 1개를 삭제하면 나머지 1개만 남아야 함
        self.assertEqual(self.post_001.comment_set.count(), 1)


    def test_search(self):
        post_about_rust = Post.objects.create(
            title='러스트에 대한 포스트입니다.',
            content='Hello, World!',
            author=self.user_user1
        )

        response = self.client.get('/blog/search/러스트/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')

        self.assertIn('Search: 러스트(2)', main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertIn(post_about_rust.title, main_area.text)