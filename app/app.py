import reflex as rx
from app.components.recorder import recorder_page
from app.components.gallery import gallery_page
from app.states.gallery_state import GalleryState

app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(recorder_page, route="/")
app.add_page(gallery_page, route="/gallery/[class_slug]", on_load=GalleryState.on_load)