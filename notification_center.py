class NotificationCenter:
    def __init__(self):
        self._observers = {}

    def add_observer(self, notification_name, callback):
        """Register a callback for a notification name."""
        if notification_name not in self._observers:
            self._observers[notification_name] = []
        self._observers[notification_name].append(callback)

    def post_notification(self, notification_name, data=None):
        """Post a notification, calling all registered callbacks with the given data."""
        for callback in self._observers.get(notification_name, []):
            callback(data)