# usuarios/views.py
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from .models import Usuario
from .forms import UsuarioForm

class UsuarioListView(ListView):
    model = Usuario
    #template_name = 'usuarios_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        """
        Permite filtrar los usuarios por el parámetro 'estado' en la URL, por ejemplo: ?estado=activo
        """
        qs = super().get_queryset()
        estado = self.request.GET.get('estado')
        if estado:
            # Mapea los valores externos a los internos, por ejemplo:
            if estado == 'inscrito':
                estado_filtrado = 'activo'
            elif estado == 'matriculado':
                estado_filtrado = 'activo'  # O el valor que corresponda
            else:
                estado_filtrado = estado
            qs = qs.filter(estado=estado_filtrado)
        return qs

class UsuarioDetailView(DetailView):
    model = Usuario
    #template_name = 'usuarios_detail.html'
    context_object_name = 'usuario'
    pk_url_kwarg = 'usuario_id'

class UsuarioUpdateView(UpdateView):
    model = Usuario
    form_class = UsuarioForm
    #template_name = 'usuarios_edit.html'
    context_object_name = 'usuario'
    pk_url_kwarg = 'usuario_id'

    def get_success_url(self):
        return reverse('usuarios:detail', kwargs={'usuario_id': self.object.id})

class UsuarioDeleteView(DeleteView):
    model = Usuario
    #template_name = 'usuarios_confirm_delete.html'
    context_object_name = 'usuario'
    pk_url_kwarg = 'usuario_id'
    success_url = reverse_lazy('usuarios:list')
