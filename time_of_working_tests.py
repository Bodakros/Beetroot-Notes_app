import json
import time
from datetime import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from notes.models import Note, Category


class PerformanceTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.performance_results = []

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            password='Testpass123$'
        )

        #Login
        self.client.login(username='testuser', password='Testpass123$')

        # Create category
        self.category = Category.objects.create(
            title='Test Category',
            user=self.user
        )

        # Create note
        self.note = Note.objects.create(
            title='Test Note',
            text='This is a test note.',
            category=self.category,
            user=self.user
        )


    def measure_view_performance(self, test_name, method, url, data=None):
        start_time = time.perf_counter()

        if method == 'get':
            response = self.client.get(url)
        else:
            response = self.client.post(url, data)

        end_time = time.perf_counter()
        fin_time = end_time - start_time

        result = {
            'test_name': test_name,
            'method': method.upper(),
            'url': url,
            'status_code': response.status_code,
            'fin_time': round(fin_time, 4)
        }

        self.__class__.performance_results.append(result)

        return response, fin_time

    def test_home_page_load(self):
        response, fin_time = self.measure_view_performance(
            'Home Page Load', 'get', '/notes/'
        )
        self.assertEqual(response.status_code, 200)
        print(f"Home Page Load: {fin_time:.4f} seconds. Status: {response.status_code}")

    def testcreate_note_form_page(self):
        response, fin_time = self.measure_view_performance(
            'Create Note Form Page', 'get', '/notes/create/'
        )
        self.assertEqual(response.status_code, 200)
        print(f"Create Note Form Page: {fin_time:.4f} seconds. Status: {response.status_code}")

    def test_submit_create_note(self):
        note_data = {
            'title': f'Performance Test Note {int(time.time())}',
            'text': 'This is a performance test note.',
            'category': self.category.id,
            'reminder': ''
        }

        response, fin_time = self.measure_view_performance(
            'Submit Create Note Form', 'post', '/notes/create/', note_data
        )
        self.assertEqual(response.status_code, 302)
        print(f"Submit Create Note Form: {fin_time:.4f} seconds. Status: {response.status_code}")

    def test_note_detail_page(self):
        response, fin_time = self.measure_view_performance(
            'Note Detail Page', 'get', f'/notes/{self.note.id}/'
        )
        self.assertEqual(response.status_code, 200)
        print(f"Note Detail Page: {fin_time:.4f} seconds. Status: {response.status_code}")

    def test_edit_note_form_page(self):
        response, fin_time = self.measure_view_performance(
            'Edit Note Form Page', 'get', f'/notes/{self.note.id}/edit/'
        )
        self.assertEqual(response.status_code, 200)
        print(f"Edit Note Form Page: {fin_time:.4f} seconds. Status: {response.status_code}")

    def test_submit_edit_note(self):
        update_data = {
            'title': f'Updated Test Note {int(time.time())}',
            'text': 'This is an updated test note.',
            'category': self.category.id,
            'reminder': ''
        }

        response, fin_time = self.measure_view_performance(
            'Submit Edit Note Form', 'post', f'/notes/{self.note.id}/edit/', update_data
        )
        self.assertEqual(response.status_code, 302)
        print(f"Submit Edit Note Form: {fin_time:.4f} seconds. Status: {response.status_code}")

    def test_category_creation_page(self):
        response, fin_time = self.measure_view_performance(
            'Category Creation Page', 'get', '/notes/category/create/'
        )
        self.assertEqual(response.status_code, 200)
        print(f"Category Creation Page: {fin_time:.4f} seconds. Status: {response.status_code}")

    def test_search_notes(self):
        response, fin_time = self.measure_view_performance(
            'Search Notes', 'get', '/notes/?search_query=Test'
        )
        self.assertEqual(response.status_code, 200)
        print(f"Search Notes: {fin_time:.4f} seconds. Status: {response.status_code}")

    def test_profile_page(self):
        response, fin_time = self.measure_view_performance(
            'Profile Page', 'get', '/users/profile/'
        )
        self.assertEqual(response.status_code, 302)
        print(f"Profile Page: {fin_time:.4f} seconds. Status: {response.status_code}")

    def test_delete_note_page(self):
        response, fin_time = self.measure_view_performance(
            'Delete Note Page', 'get', f'/notes/{self.note.id}/delete/'
        )
        self.assertEqual(response.status_code, 200)
        print(f"Delete Note Page: {fin_time:.4f} seconds. Status: {response.status_code}")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        total_time = sum(result['fin_time'] for result in cls.performance_results)

        output = {
            'test_type': 'sync_views',
            'total_tests': len(cls.performance_results),
            'total_time': round(total_time, 4),
            'average_time': round(total_time / len(cls.performance_results), 4) if cls.performance_results else 0,
            'results': cls.performance_results
        }

        with open('speed_tests/async_performance_results.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
