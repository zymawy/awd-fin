from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing
import notifications.routing
combined_websocket_urlpatterns = (
    chat.routing.websocket_urlpatterns +
    notifications.routing.websocket_urlpatterns
)

application = ProtocolTypeRouter({
	# (http->django views is added by default)
	'websocket': AuthMiddlewareStack(
		URLRouter(
			combined_websocket_urlpatterns
		)
	),
})
