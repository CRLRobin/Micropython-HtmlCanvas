# 📘 HtmlCanvas Library – v1.0

Interactive rendering library for ESP32/MicroPython environments.
Provides HTML UI components with trigger logic and modular page construction.

---

## 🛠 Supported Components

### `draw_text(text, x, y, font_size=16, color="black")`
Render text on the canvas at a specified position.

### `button(label, x, y, trigger_name, img_src=None, width=150)`
Create a clickable button. Optionally includes an image.

### `input_box(box_id, x, y, width=250, placeholder="")`
Render a text input field. Retrieve content with `get_input(id)`.

### `upload_box(box_id, x, y, width=300, label="Upload", accept="*/*", save_to="uploads")`
Add file upload input. Automatically triggers upload to server using POST.
- Accepts MIME filters (e.g. `"image/*"` or `".json"`)
- Uploaded file is saved to specified `save_to` directory

---

## 🔁 Trigger Binding

### `on_trigger(trigger_name, callback)`
Bind a button to a Python function or lambda. Executes callback when triggered.

---

## 🌐 Page Rendering

### `render(title="Untitled", refresh=False)`
Generate HTML from current canvas state.
- If `refresh=True`, forces automatic page reload (once) using URL hash control
- Ensures consistent page updates during transitions

---

## 💡 Usage Example

```python
canvas = HtmlCanvas(800, 600)

canvas.draw_text("Enter your name:", x=50, y=40)
canvas.input_box("username", x=50, y=80, placeholder="Type here")
canvas.button("Submit", x=300, y=80, trigger_name="submit")
canvas.on_trigger("submit", lambda: next_page().render("Next", refresh=True))

html = canvas.render("Welcome Page", refresh=False)