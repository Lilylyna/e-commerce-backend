"""
Django management command to create test data for API testing
Usage: python manage.py create_test_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
from core.models import Category, Vendor, Product, Coupon
import io

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates test data (categories, vendors, products, coupons) for API testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test data...'))
        
        # Create a minimal fake image for testing
        # This creates a 1x1 pixel PNG image
        fake_image = SimpleUploadedFile(
            name='test.png',
            content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82',
            content_type='image/png'
        )
        
        # Create or get a test user
        test_user, created = User.objects.get_or_create(
            username='testvendor',
            defaults={
                'email': 'vendor@test.com',
                'is_active': True
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created test user: {test_user.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Using existing user: {test_user.username}'))
        
        # Create Category
        category, created = Category.objects.get_or_create(
            title='Electronics',
            defaults={
                'image': fake_image
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {category.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'Using existing category: {category.title}'))
        
        # Create Vendor
        vendor, created = Vendor.objects.get_or_create(
            user=test_user,
            defaults={
                'title': 'Test Electronics Store',
                'image': fake_image,
                'description': 'A test vendor for API testing',
                'address': '123 Test St',
                'contact': 'test@vendor.com',
                'chat_response_time': '24 hours'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created vendor: {vendor.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'Using existing vendor: {vendor.title}'))
        
        # Create Products
        products_data = [
            {
                'title': 'Test Laptop',
                'price': 999.99,
                'old_price': 1199.99,
                'stock_count': 10,
                'status': 'published',
                'description': 'A high-performance test laptop'
            },
            {
                'title': 'Test Smartphone',
                'price': 599.99,
                'old_price': 699.99,
                'stock_count': 20,
                'status': 'published',
                'description': 'A modern test smartphone'
            },
            {
                'title': 'Test Headphones',
                'price': 99.99,
                'stock_count': 50,
                'status': 'published',
                'description': 'Quality test headphones'
            },
        ]
        
        created_count = 0
        for product_data in products_data:
            # Create a new fake image for each product
            product_image = SimpleUploadedFile(
                name=f"{product_data['title'].lower().replace(' ', '_')}.png",
                content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82',
                content_type='image/png'
            )
            
            # Extract description if it exists
            description = product_data.pop('description', 'Test product description')
            
            product, created = Product.objects.get_or_create(
                title=product_data['title'],
                vendor=vendor,
                defaults={
                    **product_data,
                    'category': category,
                    'image': product_image,
                    'description': description
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.title}'))
            else:
                # Update stock if product exists
                product.stock_count = product_data['stock_count']
                product.save()
                self.stdout.write(self.style.WARNING(f'Updated product: {product.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'Total products: {created_count} new, {len(products_data) - created_count} existing'))
        
        # Create Coupons
        now = timezone.now()
        coupons_data = [
            {
                'code': 'SAVE10',
                'discount_type': 'percentage',
                'discount_value': 10.00,
                'minimum_purchase': 50.00,
                'max_usage': 100,
                'valid_from': now - timedelta(days=1),
                'valid_to': now + timedelta(days=365),
                'active': True
            },
            {
                'code': 'FIXED20',
                'discount_type': 'fixed',
                'discount_value': 20.00,
                'minimum_purchase': 100.00,
                'max_usage': 50,
                'valid_from': now - timedelta(days=1),
                'valid_to': now + timedelta(days=180),
                'active': True
            },
            {
                'code': 'EXPIRED',
                'discount_type': 'percentage',
                'discount_value': 15.00,
                'minimum_purchase': 0.00,
                'max_usage': 10,
                'valid_from': now - timedelta(days=30),
                'valid_to': now - timedelta(days=1),  # Expired
                'active': True
            }
        ]
        
        created_coupons = 0
        for coupon_data in coupons_data:
            coupon, created = Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults=coupon_data
            )
            if created:
                created_coupons += 1
                self.stdout.write(self.style.SUCCESS(f'Created coupon: {coupon.code}'))
            else:
                self.stdout.write(self.style.WARNING(f'Coupon already exists: {coupon.code}'))
        
        self.stdout.write(self.style.SUCCESS(f'Total coupons: {created_coupons} new, {len(coupons_data) - created_coupons} existing'))
        
        self.stdout.write(self.style.SUCCESS('\n[OK] Test data creation complete!'))
        self.stdout.write(self.style.SUCCESS('\nYou can now test the APIs with: python manage.py test_apis'))

