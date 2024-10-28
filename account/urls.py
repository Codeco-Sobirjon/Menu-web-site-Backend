from django.urls import path
from account import views

urlpatterns = [
    path('login_user/',views.UserLoginView.as_view()),
    path('logout_user/',views.UserLogoutView.as_view()),
    path('profile_user/',views.UserProfilesView.as_view()),
    
    path('restaurant_object/',views.RestaurantView.as_view()),
    
    path('lists_catalog/',views.CatalogListViews.as_view()),
    path('details_catalog/<int:id>/',views.CatalogDetailViews.as_view()),
    
    path('lists_product/',views.ProductListViews.as_view()),
    path('filters_product/',views.ProductFilterView.as_view()),
    path('details_product/<int:id>/',views.ProductDetailViews.as_view()),
    
    path('lists_servant/',views.CustomUserListViews.as_view()),
    path('details_servant/<int:id>/',views.CustomUserDetailViews.as_view()),

    path('product_save/',views.ProductSaveView.as_view()),
    path('filters_product_save/',views.ProductSaveFilterView.as_view()),
    path('product_save_details/<int:id>/',views.ProductSaveDetailsView.as_view()),
    
    path('catalog_product/<int:id>/',views.CatalogProductView.as_view()),

]