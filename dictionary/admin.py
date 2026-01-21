from django.contrib import admin
from .models import Word, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_words_count')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('name',)
    ordering = ('name',)

    def get_words_count(self, obj):
        return obj.words.count()
    get_words_count.short_description = 'So\'zlar soni'




@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'letter_count', 'search_count', 'get_categories')
    search_fields = ('word', 'definition', 'pronunciation')
    list_filter = ('letter_count', 'categories')

    readonly_fields = ('search_count',)

    # 🔴 MUHIM QATOR
    exclude = ('slug',)

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('word', 'definition', 'pronunciation', 'categories')
        }),
    )

    def get_categories(self, obj):
        return ", ".join(c.name for c in obj.categories.all())
    get_categories.short_description = 'Kategoriyalar'
