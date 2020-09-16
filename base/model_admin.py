from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at',)

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()
