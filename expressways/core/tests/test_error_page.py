from django.test import RequestFactory, TestCase
from django.urls import reverse

from expressways.core.factories import UserFactory, RoadFactory
from expressways.core.models import Road
from expressways.core.views import custom500, custom404

class TestDesignComponentSelection(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.road = RoadFactory()
        self.factory = RequestFactory()

        self.client.force_login(self.user)

    def test_with_invalid_road_id(self):
        '''
        When user navigates to page with invalid road i.e. does not exist,
        custom error page with expressways header bar is raised 
        '''
        test_road_id = 1234
        self.assertEqual(0, Road.objects.filter(id=test_road_id).count())
        data = {
            'road_id': test_road_id
        }

        response = self.client.get(reverse('core:home', kwargs=data))
        html = response.content.decode()
        self.assertTemplateUsed(response, '404.html')
        self.assertInHTML("<p>We're sorry, but the requested page could not be found. The road does not exist.</p>", html)
        self.assertInHTML('<div><span class="navbar-text">Expressways</span></div>', html)

    def test_404_error_page_handler(self):
        '''
        When user navigates to invalid page route,
        custom error page with expressways header bar is raised 
        '''
        request = self.factory.get('/')
        response = custom404(request)
        html = response.content.decode()
        self.assertEqual(response.status_code, 404)
        self.assertInHTML("<h2>Page not found</h2>", html)
        self.assertInHTML("<p>We're sorry, but the requested page could not be found.</p>", html)
        self.assertInHTML('<div><span class="navbar-text">Expressways</span></div>', html)

    def test_500_error_page_handler(self):
        '''
        When system produces 500 error page,
        custom error page with expressways header bar is raised 
        '''
        request = self.factory.get('/')
        response = custom500(request)
        html = response.content.decode()
        self.assertEqual(response.status_code, 500)
        self.assertInHTML("<h2>Server error</h2>", html)
        self.assertInHTML("<p>We're sorry, but something has gone wrong with the server.</p>", html)
        self.assertInHTML('<div><span class="navbar-text">Expressways</span></div>', html)
