"""
Observer Pattern Implementation for E-Commerce Backend

The Observer pattern defines a one-to-many dependency between objects so that when one object
(state) changes, all its dependents (observers) are notified and updated automatically.

This implementation is used for:
- Order status changes (email notifications, inventory updates, analytics)
- Product stock level changes
- User registration events
"""

from abc import ABC, abstractmethod
from typing import List, Any, Dict
import logging

logger = logging.getLogger(__name__)


class Observer(ABC):
    """
    Abstract Observer class that defines the interface for objects that should be notified
    of changes in a subject.

    This is the base class for all observers in the system.
    """

    @abstractmethod
    def update(self, subject: 'Subject', event_data: Dict[str, Any]) -> None:
        """
        Called when the subject notifies this observer of a change.

        Args:
            subject: The subject that triggered the notification
            event_data: Dictionary containing event-specific data
        """
        pass


class Subject:
    """
    Subject class that maintains a list of observers and notifies them of state changes.

    This class implements the core functionality of the observer pattern:
    - Registering/unregistering observers
    - Notifying all observers when state changes
    """

    def __init__(self):
        """Initialize the subject with an empty list of observers."""
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to this subject.

        Args:
            observer: The observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
            logger.debug(f"Observer {observer.__class__.__name__} attached to {self.__class__.__name__}")

    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from this subject.

        Args:
            observer: The observer to detach
        """
        try:
            self._observers.remove(observer)
            logger.debug(f"Observer {observer.__class__.__name__} detached from {self.__class__.__name__}")
        except ValueError:
            logger.warning(f"Observer {observer.__class__.__name__} not found in observers list")

    def notify(self, event_data: Dict[str, Any]) -> None:
        """
        Notify all attached observers of a state change.

        Args:
            event_data: Dictionary containing event-specific data to pass to observers
        """
        logger.info(f"{self.__class__.__name__} notifying {len(self._observers)} observers")
        for observer in self._observers:
            try:
                observer.update(self, event_data)
            except Exception as e:
                logger.error(f"Error notifying observer {observer.__class__.__name__}: {str(e)}")


# Order-specific observers
class OrderStatusObserver(ABC):
    """
    Abstract base class for observers that react to order status changes.

    This provides a more specific interface for order-related observers.
    """

    @abstractmethod
    def on_order_status_changed(self, order, old_status: str, new_status: str) -> None:
        """
        Called when an order's status changes.

        Args:
            order: The order instance that changed
            old_status: The previous order status
            new_status: The new order status
        """
        pass


class EmailNotificationObserver(OrderStatusObserver, Observer):
    """
    Observer that sends email notifications when order status changes.

    OBSERVER PATTERN IMPLEMENTATION:
    - This class implements the Observer interface
    - It gets notified when order status changes
    - It performs email notification as a side effect of the status change
    """

    def update(self, subject, event_data: Dict[str, Any]) -> None:
        """
        Observer pattern: Called by the subject when notified of changes.
        """
        if event_data.get('event_type') == 'order_status_changed':
            order = event_data.get('order')
            old_status = event_data.get('old_status')
            new_status = event_data.get('new_status')
            self.on_order_status_changed(order, old_status, new_status)

    def on_order_status_changed(self, order, old_status: str, new_status: str) -> None:
        """
        Handle order status changes by sending appropriate email notifications.
        """
        from .utils import send_order_confirmation  # Import here to avoid circular imports

        try:
            if new_status == 'processing':
                # Send processing confirmation email
                logger.info(f"Sending processing confirmation for order {order.oid}")
                # Could implement send_processing_notification(order.oid) here

            elif new_status == 'shipped':
                # Send shipping confirmation email
                logger.info(f"Sending shipping notification for order {order.oid}")
                # Could implement send_shipping_notification(order.oid) here

            elif new_status == 'delivered':
                # Send delivery confirmation email
                logger.info(f"Sending delivery confirmation for order {order.oid}")
                # Could implement send_delivery_notification(order.oid) here

            elif new_status == 'cancelled':
                # Send cancellation confirmation email
                logger.info(f"Sending cancellation notification for order {order.oid}")
                # Could implement send_cancellation_notification(order.oid) here

        except Exception as e:
            logger.error(f"Failed to send email notification for order {order.oid}: {str(e)}")


class InventoryObserver(OrderStatusObserver, Observer):
    """
    Observer that manages inventory when order status changes.

    OBSERVER PATTERN IMPLEMENTATION:
    - This class implements the Observer interface
    - It gets notified when order status changes
    - It performs inventory management as a side effect of the status change
    """

    def update(self, subject, event_data: Dict[str, Any]) -> None:
        """
        Observer pattern: Called by the subject when notified of changes.
        """
        if event_data.get('event_type') == 'order_status_changed':
            order = event_data.get('order')
            old_status = event_data.get('old_status')
            new_status = event_data.get('new_status')
            self.on_order_status_changed(order, old_status, new_status)

    def on_order_status_changed(self, order, old_status: str, new_status: str) -> None:
        """
        Handle inventory management based on order status changes.
        """
        try:
            if new_status == 'cancelled' and old_status in ['pending', 'processing']:
                # Restore inventory when order is cancelled
                logger.info(f"Restoring inventory for cancelled order {order.oid}")
                for order_item in order.order_items.all():
                    if order_item.product:
                        order_item.product.stock_count += order_item.quantity
                        order_item.product.save()
                        logger.debug(f"Restored {order_item.quantity} units of {order_item.product.title}")

            elif new_status == 'delivered':
                # Could implement additional inventory tracking here
                # e.g., update sales statistics, reorder point checks, etc.
                logger.info(f"Order {order.oid} delivered - updating inventory analytics")

        except Exception as e:
            logger.error(f"Failed to update inventory for order {order.oid}: {str(e)}")


class AnalyticsObserver(OrderStatusObserver, Observer):
    """
    Observer that tracks analytics when order status changes.

    OBSERVER PATTERN IMPLEMENTATION:
    - This class implements the Observer interface
    - It gets notified when order status changes
    - It performs analytics tracking as a side effect of the status change
    """

    def update(self, subject, event_data: Dict[str, Any]) -> None:
        """
        Observer pattern: Called by the subject when notified of changes.
        """
        if event_data.get('event_type') == 'order_status_changed':
            order = event_data.get('order')
            old_status = event_data.get('old_status')
            new_status = event_data.get('new_status')
            self.on_order_status_changed(order, old_status, new_status)

    def on_order_status_changed(self, order, old_status: str, new_status: str) -> None:
        """
        Track analytics based on order status changes.
        """
        try:
            # Track conversion metrics
            if new_status == 'delivered':
                logger.info(f"Order {order.oid} completed - tracking conversion analytics")
                # Could integrate with analytics service here
                # e.g., Google Analytics, Mixpanel, custom analytics, etc.

            elif new_status == 'cancelled':
                logger.info(f"Order {order.oid} cancelled - tracking cancellation analytics")
                # Track cancellation reasons, patterns, etc.

            # Track order lifecycle metrics
            logger.info(f"Order {order.oid} status changed: {old_status} -> {new_status}")

        except Exception as e:
            logger.error(f"Failed to track analytics for order {order.oid}: {str(e)}")


# Product-specific observers
class ProductStockObserver(Observer):
    """
    Observer that monitors product stock changes.

    OBSERVER PATTERN IMPLEMENTATION:
    - This class implements the Observer interface
    - It gets notified when product stock changes
    - It performs stock-related actions as a side effect of the change
    """

    def update(self, subject, event_data: Dict[str, Any]) -> None:
        """
        Observer pattern: Called by the subject when notified of changes.
        """
        if event_data.get('event_type') == 'stock_changed':
            product = event_data.get('product')
            old_stock = event_data.get('old_stock')
            new_stock = event_data.get('new_stock')
            self.on_stock_changed(product, old_stock, new_stock)

    def on_stock_changed(self, product, old_stock: int, new_stock: int) -> None:
        """
        Handle product stock changes.
        """
        try:
            # Low stock alert
            if new_stock <= 5 and old_stock > 5:
                logger.warning(f"Low stock alert: {product.title} has only {new_stock} units remaining")
                # Could send email to vendor/admin here

            # Out of stock alert
            elif new_stock == 0 and old_stock > 0:
                logger.warning(f"Out of stock: {product.title} is now unavailable")
                # Could update product status, notify vendors, etc.

            # Restock alert
            elif new_stock > 0 and old_stock == 0:
                logger.info(f"Restocked: {product.title} is back in stock with {new_stock} units")

        except Exception as e:
            logger.error(f"Failed to handle stock change for product {product.title}: {str(e)}")


# Global observer registry
class ObserverRegistry:
    """
    Registry to manage observers globally.

    This class provides a centralized way to register and manage observers
    across the application.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._observers: Dict[str, List[Observer]] = {}
            self._initialized = True

    def register_observer(self, event_type: str, observer: Observer) -> None:
        """
        Register an observer for a specific event type.

        Args:
            event_type: The type of event to observe (e.g., 'order_status_changed')
            observer: The observer instance to register
        """
        if event_type not in self._observers:
            self._observers[event_type] = []
        if observer not in self._observers[event_type]:
            self._observers[event_type].append(observer)
            logger.debug(f"Registered observer {observer.__class__.__name__} for event {event_type}")

    def unregister_observer(self, event_type: str, observer: Observer) -> None:
        """
        Unregister an observer from a specific event type.

        Args:
            event_type: The event type
            observer: The observer to unregister
        """
        if event_type in self._observers:
            try:
                self._observers[event_type].remove(observer)
                logger.debug(f"Unregistered observer {observer.__class__.__name__} from event {event_type}")
            except ValueError:
                logger.warning(f"Observer {observer.__class__.__name__} not found for event {event_type}")

    def notify_observers(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Notify all observers registered for a specific event type.

        Args:
            event_type: The event type to notify
            event_data: Data to pass to the observers
        """
        if event_type in self._observers:
            logger.info(f"Notifying {len(self._observers[event_type])} observers for event {event_type}")
            for observer in self._observers[event_type]:
                try:
                    observer.update(None, event_data)
                except Exception as e:
                    logger.error(f"Error notifying observer {observer.__class__.__name__}: {str(e)}")