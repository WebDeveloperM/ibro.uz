import json
import random

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import Truncator

from .models import Word, Category


def build_absolute_url(path):
    return f"{settings.SITE_URL}{path}"


def build_seo_context(request, *, title, description, robots='index,follow', og_type='website', structured_data=None):
    current_path = request.path if request.path.startswith('/') else f"/{request.path}"
    canonical_url = build_absolute_url(current_path)
    logo_url = build_absolute_url(static('images/logo.png'))
    schemas = [
        {
            '@context': 'https://schema.org',
            '@type': 'WebSite',
            'name': settings.SITE_NAME,
            'url': f"{settings.SITE_URL}/",
            'potentialAction': {
                '@type': 'SearchAction',
                'target': f"{settings.SITE_URL}{reverse('search')}?q={{search_term_string}}",
                'query-input': 'required name=search_term_string',
            },
        }
    ]
    if structured_data:
        schemas.extend(structured_data)

    return {
        'seo': {
            'title': title,
            'description': Truncator(description).chars(160),
            'canonical_url': canonical_url,
            'robots': robots,
            'og_type': og_type,
            'image_url': logo_url,
            'structured_data_json': json.dumps(schemas, ensure_ascii=False),
        }
    }


def _random_words_qs(n):
    """So'zlar jadvalidan n ta tasodifiy yozuvni samarali tanlaydi."""
    ids = list(Word.objects.values_list('id', flat=True))
    sample_ids = random.sample(ids, min(n, len(ids)))
    return Word.objects.filter(id__in=sample_ids).only('word', 'slug')


def home(request):
    most_searched = Word.objects.only('word', 'slug').order_by('-search_count')[:10]
    random_words = _random_words_qs(6)
    common_misspelled = (
        Word.objects.filter(categories__slug='kop-xato-qilinadigan-sozlar')
        .only('word', 'slug')[:6]
    )
    context = {
        'most_searched': most_searched,
        'random_words': random_words,
        'common_misspelled': common_misspelled,
    }
    context.update(build_seo_context(
        request,
        title="Ibro.uz | O'zbekcha imlo va izohli lug'at",
        description="Ibro.uz orqali o'zbekcha so'zlarning to'g'ri imlosi, ma'nosi, talaffuzi va kategoriyalar bo'yicha lug'at natijalarini toping.",
        structured_data=[
            {
                '@context': 'https://schema.org',
                '@type': 'Organization',
                'name': settings.SITE_NAME,
                'url': f"{settings.SITE_URL}/",
                'logo': build_absolute_url(static('images/logo.png')),
            }
        ],
    ))
    return render(request, 'dictionary/home.html', context)


def word_detail(request, slug):
    word = get_object_or_404(
        Word.objects.prefetch_related('categories'), slug=slug
    )
    word.search_count += 1
    word.save(update_fields=['search_count'])
    description = word.definition
    if word.pronunciation:
        description = f"{word.word} - /{word.pronunciation}/. {word.definition}"
    context = {'word': word}
    word_url = build_absolute_url(reverse('word_detail', args=[word.slug]))
    context.update(build_seo_context(
        request,
        title=f"{word.word} ma'nosi va imlosi | {settings.SITE_NAME}",
        description=description,
        og_type='article',
        structured_data=[
            {
                '@context': 'https://schema.org',
                '@type': 'DefinedTerm',
                'name': word.word,
                'description': word.definition,
                'url': word_url,
                'inDefinedTermSet': f"{settings.SITE_URL}/",
            },
            {
                '@context': 'https://schema.org',
                '@type': 'BreadcrumbList',
                'itemListElement': [
                    {'@type': 'ListItem', 'position': 1, 'name': 'Bosh sahifa', 'item': f"{settings.SITE_URL}/"},
                    {'@type': 'ListItem', 'position': 2, 'name': word.word, 'item': word_url},
                ],
            },
        ],
    ))
    return render(request, 'dictionary/word_detail.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    words = category.words.only('word', 'slug', 'letter_count')
    description = category.description or f"{category.name} kategoriyasidagi o'zbekcha so'zlar va ularning izohlari ro'yxati."
    category_url = build_absolute_url(reverse('category_detail', args=[category.slug]))
    context = {'category': category, 'words': words}
    context.update(build_seo_context(
        request,
        title=f"{category.name} | {settings.SITE_NAME}",
        description=description,
        structured_data=[
            {
                '@context': 'https://schema.org',
                '@type': 'CollectionPage',
                'name': category.name,
                'description': description,
                'url': category_url,
            },
            {
                '@context': 'https://schema.org',
                '@type': 'BreadcrumbList',
                'itemListElement': [
                    {'@type': 'ListItem', 'position': 1, 'name': 'Bosh sahifa', 'item': f"{settings.SITE_URL}/"},
                    {'@type': 'ListItem', 'position': 2, 'name': category.name, 'item': category_url},
                ],
            },
        ],
    ))
    return render(request, 'dictionary/category_detail.html', context)


def words_by_letter_count(request, count):
    words = Word.objects.filter(letter_count=count).only('word', 'slug')
    title = f'{count} ta harfli so’zlar'
    context = {'words': words, 'title': title}
    context.update(build_seo_context(
        request,
        title=f"{title} | {settings.SITE_NAME}",
        description=f"{count} ta harfdan iborat o'zbekcha so'zlar ro'yxati va lug'at natijalari.",
    ))
    return render(request, 'dictionary/words_list.html', context)


def search(request):
    query = request.GET.get('q', '').strip()
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if is_ajax:
        results = []
        if query:
            words = (
                Word.objects.filter(
                    Q(word__icontains=query) | Q(definition__icontains=query)
                )
                .only('word', 'definition', 'slug', 'letter_count')
                .distinct()[:10]
            )
            for word in words:
                results.append({
                    'word': word.word,
                    'definition': word.definition[:100] + '...' if len(word.definition) > 100 else word.definition,
                    'url': f'/word/{word.slug}/',
                    'letter_count': word.letter_count,
                })
        return JsonResponse({'results': results})

    words = []
    if query:
        words = (
            Word.objects.filter(
                Q(word__icontains=query) | Q(definition__icontains=query)
            )
            .only('word', 'definition', 'slug')
            .distinct()
        )

    context = {'words': words, 'query': query}
    context.update(build_seo_context(
        request,
        title=f'Qidiruv natijalari: {query or "so’z"} | {settings.SITE_NAME}',
        description=f'"{query}" bo’yicha topilgan o’zbekcha so’zlar va izohlar natijasi.',
        robots='noindex,follow',
    ))
    return render(request, 'dictionary/search_results.html', context)


def words_by_letter(request, letter):
    words = Word.objects.filter(word__istartswith=letter.upper()).only('word', 'slug')
    title = f'{letter.upper()} harfi bilan boshlanadigan so’zlar'
    context = {'words': words, 'title': title}
    context.update(build_seo_context(
        request,
        title=f"{title} | {settings.SITE_NAME}",
        description=f"{letter.upper()} harfi bilan boshlanadigan o'zbekcha so'zlar ro'yxati va lug'at natijalari.",
    ))
    return render(request, 'dictionary/words_list.html', context)


def most_searched_words(request):
    words = Word.objects.only('word', 'slug').order_by('-search_count', 'word')
    title = 'Ko’p qidirilgan so’zlar'
    context = {'words': words, 'title': title}
    context.update(build_seo_context(
        request,
        title=f"{title} | {settings.SITE_NAME}",
        description="Ibro.uz foydalanuvchilari eng ko'p qidirgan o'zbekcha so'zlar va ularning izohlari.",
    ))
    return render(request, 'dictionary/words_list.html', context)


def random_words(request):
    words = _random_words_qs(50)
    title = 'Tasodifiy so’zlar'
    context = {'words': words, 'title': title}
    context.update(build_seo_context(
        request,
        title=f"{title} | {settings.SITE_NAME}",
        description="Tasodifiy tanlangan o'zbekcha so'zlar va ularning izohlarini ko'ring.",
    ))
    return render(request, 'dictionary/words_list.html', context)


def robots_txt(request):
    content = '\n'.join([
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /search/',
        f'Sitemap: {build_absolute_url(reverse("django.contrib.sitemaps.views.sitemap"))}',
    ])
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


def google_site_verification(request, filename):
    content = f'google-site-verification: {filename}.html'
    return HttpResponse(content, content_type='text/html; charset=utf-8')
