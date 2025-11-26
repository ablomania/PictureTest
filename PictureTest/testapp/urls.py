from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('dashboard', views.dashboard, name='dashboard_page'),
    path('setup_page/<int:test_id>', views.setup_pages, name='setup_pages_page'),
    path('setup_tests', views.setup_tests, name='setup_tests_page'),
    path('add_test', views.add_test, name='add_test_page'),
    path('edit_test/<int:test_id>', views.edit_test, name='edit_test_page'),
    path('add_page/<int:test_id>', views.add_page, name='add_page_page'), 
    path('edit_page/<int:test_id>/<int:page_id>', views.edit_page, name='edit_page_page'),
    path('start_test/<int:test_id>', views.start_test, name='start_test_page'),
    path('view_test/<int:test_id>/<int:page_number>', views.test_page, name='view_test_page'),
    path('test_done/<int:test_id>', views.test_done, name="test_done_page"),
    path('view_test2/<int:test_id>', views.test_page2, name="view_test_2"),
    path('add_instruction/<int:test_id>', views.add_instruction, name="new_instruction"),
    path('edit_instruction/<int:instruct_id>', views.edit_instruction, name="edit_instruction_page"),
    path('set_password/<int:test_id>', views.add_password, name="set_password"),
    path('reset_password/<int:test_id>', views.reset_password, name="reset_password_page"),
    path('trash', views.trash, name='trash_page'),
 ]