import reflex as rx
from app.states.recorder_state import RecorderState
from app import classes


def recorder_page() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            _hero_section(),
            rx.el.form(
                rx.el.div(
                    rx.el.div(
                        _class_selector(),
                        _date_selector(),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-8",
                    ),
                    _gallery_links(),
                    _file_uploaders(),
                    _voice_recorder(),
                    _notes_and_transcript_section(),
                    class_name="space-y-8",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("save", class_name="mr-2"),
                        "Save Artifact",
                        on_click=RecorderState.save_entry_event,
                        class_name="flex items-center justify-center px-8 py-3 rounded-xl text-white font-semibold transition-colors shadow-sm w-full sm:w-auto",
                        style={"background_color": RecorderState.accent_color},
                    ),
                    class_name="mt-12 flex justify-end",
                ),
                on_submit=lambda: RecorderState.save_entry_event,
                width="100%",
            ),
            class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20",
        ),
        _recorder_script(),
        class_name="font-['Inter'] bg-gray-50 min-h-screen",
    )


def _hero_section() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "Classroom Artifact Maker",
            class_name="text-4xl md:text-5xl font-bold text-gray-800 tracking-tight",
        ),
        rx.el.p(
            "Capture and organize your classroom moments. Upload photos, videos, record audio, and write notes.",
            class_name="mt-4 text-lg text-gray-600 max-w-3xl",
        ),
        class_name="text-center lg:text-left mb-12 md:mb-16",
    )


def _gallery_links() -> rx.Component:
    return rx.el.div(
        _form_section_header("layout-grid", "View Galleries"),
        rx.el.div(
            rx.foreach(
                list(classes.CLASS_INFO.values()),
                lambda class_info: rx.el.a(
                    rx.el.button(
                        class_info["emoji"],
                        class_info["name"],
                        rx.icon("arrow-right", class_name="ml-2 size-4"),
                        class_name="flex items-center justify-center text-sm font-medium rounded-lg w-full transition-colors",
                        style={
                            "background-color": class_info["accent_color"] + "20",
                            "color": class_info["accent_color"],
                            "padding": "10px",
                        },
                    ),
                    href=f"/gallery?class={class_info['slug']}",
                ),
            ),
            class_name="grid grid-cols-1 sm:grid-cols-3 gap-4",
        ),
    )


def _class_selector() -> rx.Component:
    return rx.el.div(
        _form_section_header("school", "Class"),
        rx.el.select(
            rx.foreach(
                list(classes.CLASS_INFO.values()),
                lambda class_info: rx.el.option(
                    f"{class_info['emoji']} {class_info['name']}",
                    value=class_info["slug"],
                ),
            ),
            value=RecorderState.selected_class_slug,
            on_change=RecorderState.set_selected_class_slug,
            size="3",
            class_name="w-full text-base",
            style={"--accent-color": RecorderState.accent_color},
        ),
    )


def _date_selector() -> rx.Component:
    return rx.el.div(
        _form_section_header("calendar-days", "Date"),
        rx.el.input(
            type="date",
            default_value=RecorderState.entry_date,
            on_change=RecorderState.set_entry_date,
            class_name="w-full p-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2",
            style={"--tw-ring-color": RecorderState.accent_color},
        ),
    )


def _file_uploaders() -> rx.Component:
    return rx.el.div(
        _form_section_header("file-up", "Media Uploads"),
        rx.el.div(
            _file_upload_component(
                id="image_upload",
                icon="image",
                text="Upload Images",
                accept={"image/*": classes.SUPPORTED_IMAGES},
                on_upload=RecorderState.handle_image_upload,
                files_var=RecorderState.image_files,
            ),
            _file_upload_component(
                id="video_upload",
                icon="video",
                text="Upload Videos",
                accept={"video/*": classes.SUPPORTED_VIDEOS},
                on_upload=RecorderState.handle_video_upload,
                files_var=RecorderState.video_files,
            ),
            class_name="grid grid-cols-1 sm:grid-cols-2 gap-4",
        ),
    )


def _file_upload_component(
    id: str,
    icon: str,
    text: str,
    accept: dict,
    on_upload: rx.event.EventType,
    files_var: rx.Var[list[str]],
) -> rx.Component:
    return rx.el.div(
        rx.upload.root(
            rx.el.div(
                rx.icon(
                    icon,
                    class_name="w-8 h-8 mb-2",
                    style={"color": RecorderState.accent_color},
                ),
                rx.el.p(text, class_name="text-sm font-medium text-gray-700"),
                class_name="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors",
            ),
            id=id,
            multiple=True,
            accept=accept,
            class_name="w-full",
        ),
        rx.el.button(
            "Upload",
            on_click=on_upload(rx.upload_files(upload_id=id)),
            size="1",
            class_name="mt-2 w-full",
            style={
                "background_color": RecorderState.accent_color + "1A",
                "color": RecorderState.accent_color,
            },
        ),
        rx.el.div(
            rx.foreach(
                rx.selected_files(id),
                lambda file: rx.el.div(
                    rx.icon("file", class_name="w-4 h-4 mr-2"),
                    rx.el.span(file, class_name="text-xs truncate"),
                    class_name="flex items-center bg-gray-100 p-1 rounded-md",
                ),
            ),
            class_name="mt-2 space-y-1",
        ),
        class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm",
    )


def _voice_recorder() -> rx.Component:
    return rx.el.div(
        _form_section_header("mic", "Voice Recording"),
        rx.el.div(
            rx.match(
                RecorderState.recording_status,
                (
                    "idle",
                    rx.el.button(
                        rx.icon("play", class_name="mr-2"),
                        "Start Recording",
                        on_click=RecorderState.start_recording,
                        style={"background_color": RecorderState.accent_color},
                        class_name="flex items-center justify-center px-6 py-3 rounded-xl text-white font-semibold transition-colors shadow-sm w-full",
                    ),
                ),
                (
                    "recording",
                    rx.el.div(
                        rx.el.button(
                            rx.icon("square", class_name="mr-2"),
                            "Stop Recording",
                            on_click=RecorderState.stop_recording,
                            class_name="flex items-center justify-center px-6 py-3 rounded-xl bg-red-500 text-white font-semibold transition-colors shadow-sm w-full",
                        ),
                        rx.el.div(
                            rx.icon(
                                "radio", class_name="w-5 h-5 text-red-500 animate-pulse"
                            ),
                            rx.el.span(
                                "Recording...", class_name="text-sm text-gray-600"
                            ),
                            class_name="flex items-center space-x-2 mt-3 justify-center",
                        ),
                        class_name="w-full",
                    ),
                ),
                (
                    "processing",
                    rx.el.div(
                        rx.spinner(class_name="mr-2"),
                        "Processing...",
                        class_name="flex items-center justify-center px-6 py-3 rounded-xl bg-yellow-500 text-white font-semibold w-full",
                    ),
                ),
                ("unsupported", _troubleshooting_card("unsupported")),
                ("permission_denied", _troubleshooting_card("permission_denied")),
                ("error", _troubleshooting_card("error")),
                rx.el.div(
                    "Unknown state", class_name="text-red-500 p-4 bg-red-50 rounded-lg"
                ),
            ),
            class_name="p-4 bg-white rounded-xl border border-gray-200 shadow-sm flex justify-center items-center flex-col",
        ),
        on_mount=rx.call_script(
            "checkRecorderSupport()", callback=RecorderState.set_recording_status
        ),
    )


def _notes_and_transcript_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            _form_section_header("square-pen", "Notes"),
            rx.el.textarea(
                placeholder="Type your notes here...",
                default_value=RecorderState.typed_text,
                on_change=RecorderState.set_typed_text,
                rows=8,
                class_name="w-full p-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2",
                style={"--tw-ring-color": RecorderState.accent_color},
            ),
        ),
        rx.el.div(
            _form_section_header("quote", "Transcript"),
            rx.el.div(
                rx.el.p(
                    RecorderState.transcript,
                    class_name="text-gray-700 whitespace-pre-wrap text-sm",
                ),
                class_name="w-full p-3 min-h-[100px] bg-gray-100 border border-gray-200 rounded-lg",
            ),
        ),
        class_name="space-y-8",
    )


def _recorder_script() -> rx.Component:
    return rx.script("""
let mediaRecorder;
let audioChunks = [];

window.checkRecorderSupport = function() {
    if (!navigator.mediaDevices || !window.MediaRecorder) {
        console.error('MediaRecorder API not supported.');
        return 'unsupported';
    }
    return 'idle';
}

window.startRecording = async function() {
    if (window.checkRecorderSupport() === 'unsupported') {
        return 'unsupported';
    }
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };
        mediaRecorder.onstop = async () => {
            if (audioChunks.length === 0) {
                console.error('No audio data recorded.');
                return 'error'; 
            }
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const file = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });

            // Use a specific event handler for processing the audio blob
            const process_event = window.reflex_handlers.process_audio_and_transcribe;
            if (process_event) {
                // Create a temporary file object for the backend
                const temp_file = {
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    lastModified: file.lastModified,
                };
                // Use rx.upload to send the file to the backend
                const files = [file];
                const uploadController = new rx.UploadController(process_event, files);
                await uploadController.start();
            } else {
                console.error('Reflex event handler for audio processing not found.');
            }
            audioChunks = [];
        };
        mediaRecorder.start();
        return 'recording';
    } catch (err) {
        console.error('Error starting recording:', err.name, err.message);
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            return 'permission_denied';
        }
        return 'error';
    }
}

window.stopRecording = function() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
}
""")


def _troubleshooting_card(error_type: str) -> rx.Component:
    messages = {
        "unsupported": {
            "icon": "server-off",
            "title": "Browser Not Supported",
            "body": "Your browser does not support the required MediaRecorder API for voice recording. Please use a modern browser like Chrome, Firefox, or Safari.",
            "color": "orange",
        },
        "permission_denied": {
            "icon": "mic-off",
            "title": "Microphone Access Denied",
            "body": "Microphone access is required for voice recording. Please allow access in your browser's settings and refresh the page.",
            "color": "red",
        },
        "error": {
            "icon": "alert-triangle",
            "title": "Recording Error",
            "body": "An unexpected error occurred. Please try again or check your browser's console for more details.",
            "color": "red",
        },
    }
    message = messages.get(error_type, messages["error"])
    return rx.el.div(
        rx.icon(
            message["icon"], class_name="size-8 mb-2", style={"color": message["color"]}
        ),
        rx.el.h4(
            message["title"],
            class_name=f"text-lg font-semibold text-{message['color']}-700",
        ),
        rx.el.p(message["body"], class_name="text-sm text-gray-600 text-center"),
        class_name="flex flex-col items-center justify-center p-4 space-y-2",
    )


def _form_section_header(icon: str, title: str) -> rx.Component:
    return rx.el.div(
        rx.icon(
            icon, class_name="w-5 h-5", style={"color": RecorderState.accent_color}
        ),
        rx.el.h3(title, class_name="text-lg font-semibold text-gray-800"),
        class_name="flex items-center space-x-3 mb-4",
    )