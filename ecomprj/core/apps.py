from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Initialize observers when the Django app is ready.

        OBSERVER PATTERN IMPLEMENTATION:
        - This method is called when Django starts up
        - It registers all the observers that should listen for events
        - This ensures observers are set up before any model changes occur
        """
        # Import here to avoid circular imports
        from .patterns import (
            ObserverRegistry,
            EmailNotificationObserver,
            InventoryObserver,
            AnalyticsObserver,
            ProductStockObserver
        )

        # Get the global observer registry
        registry = ObserverRegistry()

        # OBSERVER PATTERN: Register observers for order events
        # These observers will be notified when order status changes
        registry.register_observer('order_status_changed', EmailNotificationObserver())
        registry.register_observer('order_status_changed', InventoryObserver())
        registry.register_observer('order_status_changed', AnalyticsObserver())

        # OBSERVER PATTERN: Register observers for product stock events
        # These observers will be notified when product stock levels change
        registry.register_observer('stock_changed', ProductStockObserver())

        print("Observer Pattern: All observers registered successfully!")