class MixinOwner:
    """Примесь владельца обьекта"""

    def form_valid(self, form):
        data = form.save()
        user = self.request.user
        data.owner = user
        data.save()
        return super().form_valid(form)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        return queryset.filter(owner=user)
