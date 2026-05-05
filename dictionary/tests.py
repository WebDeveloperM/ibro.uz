from django.test import TestCase
from django.urls import reverse

from .models import Category, Word


class HomeCollectionLinksTests(TestCase):
	def setUp(self):
		category = Category.objects.create(name='Ko‘p xato', slug='kop-xato-qilinadigan-sozlar')
		self.word = Word.objects.create(
			word='Sinov',
			definition='Sinov ta’rifi',
			pronunciation='sinov',
			letter_count=5,
			search_count=10,
		)
		self.word.categories.add(category)

	def test_most_searched_collection_page_loads(self):
		response = self.client.get(reverse('most_searched_words'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Ko‘p qidirilgan so‘zlar')
		self.assertContains(response, self.word.word)

	def test_random_collection_page_loads(self):
		response = self.client.get(reverse('random_words'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Tasodifiy so‘zlar')

	def test_home_see_all_links_point_to_valid_routes(self):
		response = self.client.get(reverse('home'))

		self.assertContains(response, reverse('most_searched_words'))
		self.assertContains(response, reverse('random_words'))
