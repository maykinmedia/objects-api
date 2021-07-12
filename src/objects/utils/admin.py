class EditInlineAdminMixin:
    extra = 0
    show_change_link = True
    show_add_link = True
    template = "admin/edit_inline/tabular_add_and_edit.html"

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
