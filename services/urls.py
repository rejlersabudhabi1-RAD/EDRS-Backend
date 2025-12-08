from django.urls import path, include
from . import views

app_name = 'services'

# Category URLs
category_patterns = [
    path('', views.ServiceCategoryListView.as_view(), name='category-list'),
    path('<slug:slug>/', views.ServiceCategoryDetailView.as_view(), name='category-detail'),
]

# Industry URLs
industry_patterns = [
    path('', views.ServiceIndustryListView.as_view(), name='industry-list'),
    path('<uuid:pk>/', views.ServiceIndustryDetailView.as_view(), name='industry-detail'),
]

# Service-specific URLs (nested under services)
service_nested_patterns = [
    # Service features
    path('<slug:service_slug>/features/', views.ServiceFeatureListCreateView.as_view(), name='service-features'),
    path('<slug:service_slug>/features/<uuid:pk>/', views.ServiceFeatureDetailView.as_view(), name='service-feature-detail'),
    
    # Service benefits
    path('<slug:service_slug>/benefits/', views.ServiceBenefitListCreateView.as_view(), name='service-benefits'),
    path('<slug:service_slug>/benefits/<uuid:pk>/', views.ServiceBenefitDetailView.as_view(), name='service-benefit-detail'),
    
    # Service process
    path('<slug:service_slug>/process/', views.ServiceProcessListCreateView.as_view(), name='service-process'),
    path('<slug:service_slug>/process/<uuid:pk>/', views.ServiceProcessDetailView.as_view(), name='service-process-detail'),
    
    # Service industries
    path('<slug:service_slug>/industries/', views.ServiceIndustryMappingView.as_view(), name='service-industries'),
    
    # Service testimonials
    path('<slug:service_slug>/testimonials/', views.ServiceTestimonialListCreateView.as_view(), name='service-testimonials'),
    path('<slug:service_slug>/testimonials/<uuid:pk>/', views.ServiceTestimonialDetailView.as_view(), name='service-testimonial-detail'),
]

# Inquiry URLs
inquiry_patterns = [
    path('', views.ServiceInquiryListView.as_view(), name='inquiry-list'),
    path('create/', views.ServiceInquiryCreateView.as_view(), name='inquiry-create'),
    path('<uuid:pk>/', views.ServiceInquiryDetailView.as_view(), name='inquiry-detail'),
]

# Main URL patterns
urlpatterns = [
    # Service categories
    path('categories/', include(category_patterns)),
    
    # Industries
    path('industries/', include(industry_patterns)),
    
    # Service inquiries
    path('inquiries/', include(inquiry_patterns)),
    
    # Services
    path('', views.ServiceListView.as_view(), name='service-list'),
    path('featured/', views.FeaturedServicesView.as_view(), name='featured-services'),
    path('stats/', views.service_stats_view, name='service-stats'),
    path('public-stats/', views.public_service_stats_view, name='public-service-stats'),
    path('search-options/', views.service_search_options_view, name='search-options'),
    path('<slug:slug>/', views.ServiceDetailView.as_view(), name='service-detail'),
    
    # Nested service URLs
    path('', include(service_nested_patterns)),
]