from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Category, Word


class CanonicalDomainSitemap(Sitemap):
    def get_domain(self, site=None):
        return urlparse(settings.SITE_URL).netloc


class StaticViewSitemap(CanonicalDomainSitemap):
    changefreq = 'daily'
    priority = 1.0
    protocol = 'https'

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)


class CategorySitemap(CanonicalDomainSitemap):
    changefreq = 'weekly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return Category.objects.only('slug', 'name', 'updated_at').order_by('name')

    def location(self, item):
        return reverse('category_detail', args=[item.slug])

    def lastmod(self, item):
        return item.updated_at


class WordSitemap(CanonicalDomainSitemap):
    changefreq = 'weekly'
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Word.objects.only('slug', 'word', 'updated_at').order_by('word')

    def location(self, item):
        return reverse('word_detail', args=[item.slug])

    def lastmod(self, item):
        return item.updated_at