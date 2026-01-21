from django.shortcuts import render, get_object_or_404
from .models import Word, Category

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from .models import Word, Category

def home(request):
    most_searched = Word.objects.order_by('-search_count')[:10]
    random_words = Word.objects.order_by('?')[:6]
    common_misspelled = Word.objects.filter(categories__slug='kop-xato-qilinadigan-sozlar')[:6]
    interesting_categories = Category.objects.filter(slug__in=['tesha-tegmagan-sozlar', 'bahorni-soginganlar-uchun', 'shubami_yoki_shobami', 'konstitutsiyamizda-eng-kop-ishlatilgan-sozlar', 'tabrik-sozlar'])
    suggested_words = Word.objects.order_by('?')[:8]  # Random suggested
    return render(request, 'dictionary/home.html', {
        'most_searched': most_searched,
        'random_words': random_words,
        'common_misspelled': common_misspelled,
        'interesting_categories': interesting_categories,
        'suggested_words': suggested_words,
    })

def word_detail(request, slug):
    word = get_object_or_404(Word, slug=slug)
    word.search_count += 1
    word.save()
    return render(request, 'dictionary/word_detail.html', {'word': word})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    words = category.words.all()
    return render(request, 'dictionary/category_detail.html', {'category': category, 'words': words})

def words_by_letter_count(request, count):
    words = Word.objects.filter(letter_count=count)
    return render(request, 'dictionary/words_list.html', {'words': words, 'title': f'{count} ta harfli so‘zlar'})

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
    
    return render(request, 'dictionary/search_results.html', {'words': words, 'query': query})

def words_by_letter(request, letter):
    words = Word.objects.filter(word__istartswith=letter.upper())
    return render(request, 'dictionary/words_list.html', {'words': words, 'title': f'{letter.upper()} harfi bilan boshlanadigan so‘zlar'})
