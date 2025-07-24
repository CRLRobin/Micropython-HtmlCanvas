#v1.0
class HtmlCanvas:
    def __init__(self, width=800, height=600, scale=1.0):
        self.width = int(width * scale)
        self.height = int(height * scale)
        self.scale = scale
        self.elements = []
        self.scripts = []
        self.triggers = {}
        self.mouse_data = {"x": 0, "y": 0}
        self.key_data = {"key": ""}
        self.input_data = {}
        self.response = ""

    def _scale(self, val):
        return int(val * self.scale)

    def draw_text(self, text, x, y, font_size=16, color="black"):
        xs, ys = self._scale(x), self._scale(y)
        fs = self._scale(font_size)
        html = f'<div style="position:absolute; left:{xs}px; top:{ys}px; color:{color}; font-size:{fs}px;">{text}</div>'
        self.elements.append(html)

    def draw_image(self, src, x, y, width=200):
        xs, ys = self._scale(x), self._scale(y)
        w = self._scale(width)
        html = f'<img src="{src}" style="position:absolute; left:{xs}px; top:{ys}px;" width="{w}">'
        self.elements.append(html)

    def input_box(self, field_name, x, y, width=200, placeholder=""):
        xs, ys = self._scale(x), self._scale(y)
        w = self._scale(width)
        js = f"""
        function send_{field_name}() {{
            let val = document.getElementById('{field_name}').value;
            fetch('/input?field={field_name}&value=' + encodeURIComponent(val));
        }}
        """
        self.scripts.append(js)
        html = f'''
        <input type="text" id="{field_name}" placeholder="{placeholder}"
               style="position:absolute; left:{xs}px; top:{ys}px; width:{w}px;"
               onblur="send_{field_name}()">
        '''
        self.elements.append(html)

    def update_input(self, field, value):
        self.input_data[field] = value

    def get_input(self, field):
        return self.input_data.get(field, "")
    
    def upload_box(self, box_id, x, y, width=300, label="Upload", accept="*/*", save_to="uploads"):
        html = f'''
        <label for="{box_id}" style="position:absolute; left:{x}px; top:{y}px; font-size:16px;">{label}</label>
        <input type="file" id="{box_id}" name="{box_id}" accept="{accept}"
               style="position:absolute; left:{x}px; top:{y+25}px; width:{width}px;"
               onchange="send_upload_{box_id}()">
        '''
        script = f'''
        function send_upload_{box_id}() {{
            const fileInput = document.getElementById("{box_id}");
            const file = fileInput.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append("{box_id}", file);

            fetch("/", {{
                method: "POST",
                headers: {{
                    "X-Upload-Field": "{box_id}",
                    "X-Save-To": "{save_to}"
                }},
                body: formData
            }}).then(r => r.text()).then(html => {{
                document.body.innerHTML = html;
            }});
        }}
        '''
        self.elements.append(html)
        self.scripts.append(script)

    def button(self, label, x, y, trigger_name, img_src=None, width=200):
        xs, ys = self._scale(x), self._scale(y)
        w = self._scale(width)
        js = f"""
        function trigger_{trigger_name}() {{
            fetch('/trigger?name={trigger_name}')
              .then(r => r.text())
              .then(html => {{
                  document.body.innerHTML = html;
              }});
        }}
        """
        self.scripts.append(js)

        if img_src:
            html = f'''
            <button onclick="trigger_{trigger_name}()" style="position:absolute; left:{xs}px; top:{ys}px; border:none; padding:0; background:none;">
                <img src="{img_src}" width="{w}">
            </button>
            '''
        else:
            html = f'''
            <button onclick="trigger_{trigger_name}()" style="position:absolute; left:{xs}px; top:{ys}px;">
                {label}
            </button>
            '''
        self.elements.append(html)

    def on_trigger(self, name, func):
        self.triggers[name] = func

    def handle_trigger(self, name):
        if name in self.triggers:
            result = self.triggers[name]()
            if result is None:
                return "<html><body><h3>[Error] Trigger returned None</h3></body></html>"
            return result
        else:
            return f"<html><body><h3>No trigger found for '{name}'</h3></body></html>"

    def enable_mouse_tracking(self):
        js = """
        document.onclick = function(e) {
            fetch(`/input?mouseX=${e.pageX}&mouseY=${e.pageY}`);
        };
        """
        self.scripts.append(js)

    def enable_key_tracking(self):
        js = """
        document.onkeydown = function(e) {
            fetch(`/input?key=${e.key}`);
        };
        """
        self.scripts.append(js)

    def update_mouse(self, x, y):
        self.mouse_data["x"] = x
        self.mouse_data["y"] = y

    def update_key(self, key):
        self.key_data["key"] = key

    def get_mouse(self):
        return self.mouse_data

    def get_key(self):
        return self.key_data

    
    def old_render(self, title="page", refresh=False):
        script_block = "\n".join([f"<script>{s}</script>" for s in self.scripts])
        body = "\n".join(self.elements)

        refresh_script = ""
        if refresh:
            refresh_script = """
            <script>
            (function() {
              if (!sessionStorage.getItem("refreshed")) {
                sessionStorage.setItem("refreshed", "true");
                location.replace(location.href);
              }
            })();
            </script>
            """

        html = f"""
        <html>
        <head>
          <title>{title}</title>
          {refresh_script}
        </head>
        <body style="position:relative; width:{self.width}px; height:{self.height}px;">
          {body}
          {script_block}
        </body>
        </html>
        """
        return html
    
    def render(self, title="Bias Battle", refresh=False):
        script_block = "\n".join([f"<script>{s}</script>" for s in self.scripts])
        body = "\n".join(self.elements)

        refresh_script = ""
        if refresh:
            refresh_script = """
            <script>
            (function() {
                window.location.href = window.location.href;
            })();
            </script>
            """

        html = f"""
        <html>
        <head>
            <title>{title}</title>
            {refresh_script}
        </head>
        <body style="position:relative; width:{self.width}px; height:{self.height}px;">
            {body}
            {script_block}
        </body>
        </html>
        """
        return html




    def handle_request(self, req, client):
        try:
            if "GET /trigger?name=" in req:
                name = req.split("name=")[-1].split(" ")[0]
                html = self.handle_trigger(name)
                client.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n".encode())
                client.send(html.encode())
                return True

            elif "GET /input?mouseX=" in req:
                mx = int(req.split("mouseX=")[-1].split("&")[0])
                my = int(req.split("mouseY=")[-1].split(" ")[0])
                self.update_mouse(mx, my)
                print(f"[Mouse Event] x={mx}, y={my}")
                client.send("HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n".encode())
                client.send("Mouse event received".encode())
                return True

            elif "GET /input?key=" in req:
                key = req.split("key=")[-1].split(" ")[0]
                self.update_key(key)
                print(f"[Key Event] key='{key}'")
                client.send("HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n".encode())
                client.send("Key event received".encode())
                return True

            elif "GET /input?field=" in req and "value=" in req:
                field = req.split("field=")[-1].split("&")[0]
                value = req.split("value=")[-1].split(" ")[0]
                self.update_input(field, value)
                print(f"[Input Box] {field} = '{value}'")
                client.send("HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n".encode())
                client.send("Input box received".encode())
                return True
            elif "Content-Type: multipart/form-data" in req:
                boundary = req.split("boundary=")[1].split("\r\n")[0]
                parts = req.split(boundary)
                filename = None
                content = None

                for part in parts:
                    if "Content-Disposition" in part and "filename=" in part:
                        lines = part.split("\r\n")
                        for line in lines:
                            if "filename=" in line:
                                filename = line.split("filename=")[1].replace('"','').strip()
                            if line == "":
                                content_index = lines.index(line) + 1
                                content = "\r\n".join(lines[content_index:])
                                break

                save_to = "uploads"
                if "X-Save-To:" in req:
                    save_to = req.split("X-Save-To:")[1].split("\r\n")[0].strip()

                if not(save_to in os.listdir()):
                    os.mkdir(save_to)

                if filename and content:
                    path = f"{save_to}/{filename}"
                    with open(path, "wb") as f:
                        f.write(content.encode())

                    response_canvas = HtmlCanvas(800, 600)
                    response_canvas.draw_text(f"File '{filename}' saved to '{save_to}'", x=50, y=100, font_size=20, color="green")
                    html = response_canvas.render("Upload Success", force_refresh=False)
                    client.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n".encode())
                    client.send(html.encode())
                    client.close()

        except Exception as e:
            msg = "Exception: " + str(e)
            print("[Error]", msg)
            client.send("HTTP/1.0 500 ERROR\r\nContent-type: text/plain\r\n\r\n".encode())
            client.send(msg.encode())
            return True

        return False

    def handle_static_file(self, req, client, static_dir='static'):
        if f"GET /{static_dir}/" not in req:
            return False

        try:
            fname = req.split(f"GET /{static_dir}/")[-1].split(" ")[0]
            path = f"{static_dir}/{fname}"
            with open(path, "rb") as f:
                data = f.read()
            mime = "image/jpeg" if fname.lower().endswith(".jpg") else "application/octet-stream"
            client.send(f"HTTP/1.0 200 OK\r\nContent-Type: {mime}\r\n\r\n".encode())
            client.send(data)
        except:
            client.send("HTTP/1.0 404 NOT FOUND\r\nContent-Type: text/html\r\n\r\n".encode())
            client.send("<h1>Resource Not Found</h1>".encode())

        return True