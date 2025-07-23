import os
import socket
import network
from htmlcanvas import HtmlCanvas

# ⚙️ 設定初始資料夾與圖片路徑
os.chdir("/sd/BiasBattle")
DB_DIR = "database"

# 📡 建立 AP 模式
def setup_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    pwd = "12345678"
    ap.config(essid="BiasBattle", authmode=network.AUTH_WPA_WPA2_PSK, password=pwd)
    print("AP模式啟動")
    print("SSID: BiasBattle")
    print("PASSWORD:", pwd)
    print("IP:", ap.ifconfig()[0])

# 🔧 建立網頁元件
def build_page():
    canvas = HtmlCanvas(width=800, height=600, scale=1.0)

    # 📝 文字標題
    canvas.draw_text("Welcome to Bias Battle!", x=50, y=30, font_size=22, color="maroon")

    # 🖼️ 圖片展示
    canvas.draw_image(f"{DB_DIR}/Karina.jpg", x=100, y=100, width=200)
    canvas.draw_image(f"{DB_DIR}/Winter.jpg", x=400, y=100, width=200)

    # 🔘 按鈕（圖片作為按鈕 & 文字按鈕）
    canvas.button("Karina.jpg", x=120, y=360, trigger_name="choose_karina",
                  img_src=f"{DB_DIR}/Karina.jpg", width=250)
    canvas.button("Winter.jpg", x=420, y=360, trigger_name="choose_winter")

    # 🧑 輸入框（名字）
    canvas.input_box("username", x=50, y=540, width=300, placeholder="輸入你的名字")

    # 🖱️ 滑鼠與鍵盤監聽
    canvas.enable_mouse_tracking()
    canvas.enable_key_tracking()

    # 🧠 按鈕對應的 Python 回傳函式
    def handle_choice(photo):
        name = canvas.get_input("username")
        mouse = canvas.get_mouse()
        key = canvas.get_key()
        print(mouse, key, name)
        return f"""
        <html><body>
        <h2>你好, {name}!</h2>
        <h3>你選擇了：{photo}</h3>
        <p>滑鼠點擊座標：{mouse['x']}, {mouse['y']}</p>
        <p>最近按下的鍵：{key['key']}</p>
        </body></html>
        """

    canvas.on_trigger("choose_karina", lambda: handle_choice("Karina.jpg"))
    canvas.on_trigger("choose_winter", lambda: handle_choice("Winter.jpg"))

    return canvas


# 🚀 啟動 ESP Web Server
setup_ap()
canvas = build_page()

addr = socket.getaddrinfo("0.0.0.0", 8080)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(1)
print("伺服器已啟動於 port 8080")

while True:
    client, _ = server.accept()
    req = client.recv(1024).decode()

    if canvas.handle_static_file(req, client, static_dir=DB_DIR):
        pass
    elif canvas.handle_request(req, client):
        pass
    else:
        html = canvas.render("Bias Battle Full Demo")
        client.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
        client.send(html)

    client.close()