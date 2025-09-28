from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('dashboard', views.dashboard, name='dashboard_page'),
    path('setup_page/<int:type_id>/<int:test_id>', views.setup_pages, name='setup_pages_page'),
    path('setup_tests/<int:type_id>', views.setup_tests, name='setup_tests_page'),
    path('setup_types', views.setup_types, name='setup_types_page'),
    path('add_test/<int:type_id>', views.add_test, name='add_test_page'),
    path('edit_test/<int:type_id>/<int:test_id>', views.edit_test, name='edit_test_page'),
    path('delete_test/<int:type_id>/<int:test_id>', views.delete_test, name='delete_test_page'),
    path('add_type', views.add_type, name='add_type_page'),
    path('edit_type/<int:type_id>', views.edit_type, name='edit_type_page'),
    path('delete_type/<int:type_id>', views.delete_type, name='delete_type_page'),
    path('add_page/<int:type_id>/<int:test_id>', views.add_page, name='add_page_page'), 
    path('edit_page/<int:type_id>/<int:test_id>/<int:page_id>', views.edit_page, name='edit_page_page'),
    path('delete_page/<int:type_id>/<int:test_id>/<int:page_id>', views.delete_page, name='delete_page_page'),
    path('start_test/<int:test_id>', views.start_test, name='start_test_page'),
    path('view_test/<int:test_id>/<int:page_number>', views.test_page, name='view_test_page'),
    path('test_done/<int:test_id>', views.test_done, name="test_done_page"),
    path('view_test2/<int:test_id>', views.test_page2, name="view_test_2")
]