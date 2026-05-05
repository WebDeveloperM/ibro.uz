import json

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

def home(request):
    most_searched = Word.objects.order_by('-search_count')[:10]
    random_words = Word.objects.order_by('?')[:6]
    common_misspelled = Word.objects.filter(categories__slug='kop-xato-qilinadigan-sozlar')[:6]
    interesting_categories = Category.objects.filter(slug__in=['tesha-tegmagan-sozlar', 'bahorni-soginganlar-uchun', 'shubami_yoki_shobami', 'konstitutsiyamizda-eng-kop-ishlatilgan-sozlar', 'tabrik-sozlar'])
    suggested_words = Word.objects.order_by('?')[:8]  # Random suggested
    context = {
        'most_searched': most_searched,
        'random_words': random_words,
        'common_misspelled': common_misspelled,
        'interesting_categories': interesting_categories,
        'suggested_words': suggested_words,
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
    word = get_object_or_404(Word, slug=slug)
    word.search_count += 1
    word.save(update_fields=['search_count'])
    description = word.definition
    if word.pronunciation:
        description = f"{word.word} - /{word.pronunciation}/. {word.definition}"
    context = {'word': word}
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
                'url': build_absolute_url(reverse('word_detail', args=[word.slug])),
                'inDefinedTermSet': f"{settings.SITE_URL}/",
            }
        ],
    ))
    return render(request, 'dictionary/word_detail.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    words = category.words.all()
    description = category.description or f"{category.name} kategoriyasidagi o'zbekcha so'zlar va ularning izohlari ro'yxati."
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
                'url': build_absolute_url(reverse('category_detail', args=[category.slug])),
            }
        ],
    ))
    return render(request, 'dictionary/category_detail.html', context)

def words_by_letter_count(request, count):
    words = Word.objects.filter(letter_count=count)
    title = f'{count} ta harfli so‘zlar'
    context = {'words': words, 'title': title}
    context.update(build_seo_context(
        request,
        title=f"{title} | {settings.SITE_NAME}",
        description=f"{count} ta harfdan iborat o'zbekcha so'zlar ro'yxati va lug'at natijalari.",
    ))
    return render(request, 'dictionary/words_list.html', context)

def search(request):
    query = request.GET.get('q', '').strip()
    
    # Check if it's an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        words = []
        if query:
            # Fuzzy search logic
            words = Word.objects.filter(
                Q(word__icontains=query) |  # Contains query
                Q(definition__icontains=query) |  # Definition contains query
                Q(word__istartswith=query)  # Starts with query (higher priority)
            ).distinct()[:10]  # Limit results for performance
        
        # Return JSON response for AJAX
        results = []
        for word in words:
            results.append({
                'word': word.word,
                'definition': word.definition[:100] + '...' if len(word.definition) > 100 else word.definition,
                'url': f'/word/{word.slug}/',
                'letter_count': word.letter_count,
            })
        return JsonResponse({'results': results})
    
    # Regular search for form submission
    words = []
    if query:
        words = Word.objects.filter(
            Q(word__icontains=query) |
            Q(definition__icontains=query)
        ).distinct()

    context = {'words': words, 'query': query}
    context.update(build_seo_context(
        request,
        title=f'Qidiruv natijalari: {query or "so‘z"} | {settings.SITE_NAME}',
        description=f'"{query}" bo‘yicha topilgan o‘zbekcha so‘zlar va izohlar natijasi.',
        robots='noindex,follow',
    ))
    return render(request, 'dictionary/search_results.html', context)

def words_by_letter(request, letter):
    words = Word.objects.filter(word__istartswith=letter.upper())
    title = f'{letter.upper()} harfi bilan boshlanadigan so‘zlar'
    context = {'words': words, 'title': title}
    context.update(build_seo_context(
        request,
        title=f"{title} | {settings.SITE_NAME}",
        description=f"{letter.upper()} harfi bilan boshlanadigan o'zbekcha so'zlar ro'yxati va lug'at natijalari.",
    ))
    return render(request, 'dictionary/words_list.html', context)


def most_searched_words(request):
    words = Word.objects.order_by('-search_count', 'word')
    title = 'Ko‘p qidirilgan so‘zlar'
    context = {'words': words, 'title': title}
    context.update(build_seo_context(
        request,
        title=f"{title} | {settings.SITE_NAME}",
        description="Ibro.uz foydalanuvchilari eng ko‘p qidirgan o‘zbekcha so‘zlar va ularning izohlari.",
    ))
    return render(request, 'dictionary/words_list.html', context)


def random_words(request):
    words = Word.objects.order_by('?')[:50]
    title = 'Tasodifiy so‘zlar'
    context = {'words': words, 'title': title}
    context.update(build_seo_context(
        request,
        title=f"{title} | {settings.SITE_NAME}",
        description="Tasodifiy tanlangan o‘zbekcha so‘zlar va ularning izohlarini ko‘ring.",
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
