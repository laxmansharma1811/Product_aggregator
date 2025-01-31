from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('select_product/<int:product_id>/', select_product, name='select_product'),
    path('comparison/', comparison, name='comparison'),
    path('analysis/', analysis, name='analysis'),
    path('search/', ProductSearchView.as_view(), name='product_search'),
    path('save-to-csv/', save_to_csv, name='save_to_csv'),
    path('hukut/', search_products, name='search_products'),
    path('save-hukut/', save_hukut_to_csv, name='save_hukut'),
    path('profile/', profile_view, name='profile-view'),
    path('product/<int:product_id>/historical/', product_historical_data, name='product_historical_data'),
    path('change-password/', change_password, name='change_password'),
    path('about-us/', about_us, name='about_us'),
    path('how-it-works/', how_it_works, name='how_it_works'),
    path('faqs/', faqs, name='faqs'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
