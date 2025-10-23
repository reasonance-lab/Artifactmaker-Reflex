import reflex as rx
from app.states.gallery_state import GalleryState


def gallery_page() -> rx.Component:
    return rx.el.div(
        _sidebar(),
        rx.el.main(
            rx.cond(GalleryState.has_entries, _gallery_content(), _empty_state()),
            class_name="flex-1 bg-gray-50 p-4 sm:p-6 lg:p-8",
        ),
        class_name="flex min-h-screen w-full font-['Inter'] bg-white",
    )


def _sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("book-marked", class_name="size-7"),
                    href="/",
                    class_name="flex items-center gap-2 font-bold text-xl",
                ),
                rx.el.h2(
                    GalleryState.selected_class_info.get("emoji", "")
                    + " "
                    + GalleryState.selected_class_info.get("name", ""),
                    class_name="text-xl font-bold tracking-tight",
                ),
                class_name="flex h-16 items-center border-b px-6 gap-4",
            ),
            rx.el.div(_navigation_controls(), class_name="flex-1 overflow-auto p-4"),
        ),
        class_name="flex flex-col min-h-0 border-r bg-white w-80",
    )


def _navigation_controls() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                f"{GalleryState.current_date_index + 1} of {GalleryState.total_dates}",
                class_name="text-sm font-medium text-gray-600",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("arrow-left", class_name="size-4"),
                    "Prev",
                    on_click=GalleryState.prev_date,
                    disabled=GalleryState.current_date_index <= 0,
                    class_name="flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md border bg-white hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors",
                ),
                rx.el.button(
                    "Next",
                    rx.icon("arrow-right", class_name="size-4"),
                    on_click=GalleryState.next_date,
                    disabled=GalleryState.current_date_index
                    >= GalleryState.total_dates - 1,
                    class_name="flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md border bg-white hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.el.select(
            rx.foreach(
                GalleryState.available_dates,
                lambda date: rx.el.option(date, value=date),
            ),
            value=GalleryState.current_date,
            on_change=GalleryState.set_current_date,
            size="3",
            class_name="w-full text-base",
            style={"--accent-color": GalleryState.accent_color},
        ),
    )


def _gallery_content() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            f"Entry for: {GalleryState.current_date}",
            class_name="text-2xl font-semibold text-gray-800 mb-6",
        ),
        rx.el.div(
            rx.cond(
                GalleryState.current_entry.get("images").length() > 0,
                _image_grid(),
                rx.fragment(),
            ),
            rx.cond(
                GalleryState.current_entry.get("videos").length() > 0,
                _video_section(),
                rx.fragment(),
            ),
            rx.cond(
                GalleryState.current_entry.get("audio_path"),
                _audio_section(),
                rx.fragment(),
            ),
            rx.cond(
                GalleryState.current_entry.get("typed_text") != "",
                _notes_section(),
                rx.fragment(),
            ),
            rx.cond(
                GalleryState.current_entry.get("transcript") != "",
                _transcript_section(),
                rx.fragment(),
            ),
            class_name="space-y-8",
        ),
    )


def _image_grid() -> rx.Component:
    return _content_card(
        "images",
        "Image Gallery",
        rx.el.div(
            rx.foreach(
                GalleryState.current_entry.get("images", []),
                lambda img_path: rx.el.div(
                    rx.el.image(
                        src=rx.get_upload_url(img_path.to_string()),
                        class_name="aspect-square w-full rounded-lg object-cover",
                    ),
                    class_name="overflow-hidden rounded-lg",
                ),
            ),
            class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4",
        ),
    )


def _video_section() -> rx.Component:
    return _content_card(
        "video",
        "Video Clips",
        rx.el.div(
            rx.foreach(
                GalleryState.current_entry.get("videos", []),
                lambda video_path: rx.el.video(
                    src=rx.get_upload_url(video_path.to_string()),
                    controls=True,
                    class_name="w-full rounded-lg",
                ),
            ),
            class_name="space-y-4",
        ),
    )


def _audio_section() -> rx.Component:
    return _content_card(
        "mic",
        "Audio Recording",
        rx.el.audio(
            src=rx.get_upload_url(
                GalleryState.current_entry.get("audio_path").to_string()
            ),
            controls=True,
            class_name="w-full",
        ),
    )


def _notes_section() -> rx.Component:
    return _content_card(
        "square-pen",
        "Notes",
        rx.el.p(
            GalleryState.current_entry.get("typed_text"),
            class_name="text-gray-700 whitespace-pre-wrap",
        ),
    )


def _transcript_section() -> rx.Component:
    return _content_card(
        "quote",
        "Transcript",
        rx.el.p(
            GalleryState.current_entry.get("transcript"),
            class_name="text-gray-700 whitespace-pre-wrap",
        ),
    )


def _content_card(icon: str, title: str, *children) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                icon, class_name="w-5 h-5", style={"color": GalleryState.accent_color}
            ),
            rx.el.h3(title, class_name="text-lg font-semibold text-gray-800"),
            class_name="flex items-center space-x-3 mb-4 border-b pb-3",
        ),
        *children,
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def _empty_state() -> rx.Component:
    return rx.el.div(
        rx.icon("folder-search", class_name="size-16 text-gray-400"),
        rx.el.h3(
            "No Entries Found", class_name="mt-4 text-xl font-semibold text-gray-700"
        ),
        rx.el.p(
            f"There are no entries for {GalleryState.selected_class_info.get('name', '')} yet.",
            class_name="mt-2 text-sm text-gray-500",
        ),
        rx.el.a(
            rx.el.button(
                "Create an Entry",
                class_name="mt-6 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white",
                style={"background_color": GalleryState.accent_color},
            ),
            href="/",
        ),
        class_name="flex flex-col items-center justify-center h-full text-center",
    )