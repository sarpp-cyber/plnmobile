def render_full_image(template_path, nama, tanggal, ulasan, rating):
    # Membuka gambar template
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # 1. Padam ulasan lama
    draw.rectangle([(120, 1280), (550, 1365)], fill=(27, 27, 27))
    draw.rectangle([(35, 1375), (600, 1515)], fill=(27, 27, 27))

    # 2. Pengendalian Fon Universal (Sesuai untuk Windows & Linux Streamlit Cloud)
    def dapatkan_fon(nama_fail, saiz):
        # Senarai percubaan laluan fon merentas OS
        laluan_fon = [
            nama_fail,
            f"/usr/share/fonts/truetype/dejavu/{nama_fail}",
            f"/usr/share/fonts/truetype/liberation/{nama_fail}",
            f"C:/Windows/Fonts/{nama_fail}"
        ]
        for path in laluan_fon:
            try:
                return ImageFont.truetype(path, saiz)
            except IOError:
                continue
        # Jika semua gagal, gunakan fon asas dengan tetapan saiz eksplisit
        try:
            return ImageFont.load_default(size=saiz)
        except TypeError:
            return ImageFont.load_default()

    font_nama = dapatkan_fon("DejaVuSans-Bold.ttf", 25)
    font_info = dapatkan_fon("DejaVuSans.ttf", 19)
    font_ulasan = dapatkan_fon("DejaVuSans.ttf", 21)

    # 3. Tulis Nama
    draw.text((125, 1288), str(nama), fill="#FFFFFF", font=font_nama)

    # 4. Lukis Bintang & Tarikh
    start_x = 135
    y_star = 1335
    star_size = 9
    spacing = 22
    for i in range(int(rating)):
        draw_star(draw, (start_x + i * spacing, y_star), star_size, "#8ab4f8")
    
    draw.text((start_x + int(rating) * spacing + 12, 1324), str(tanggal), fill="#8ab4f8", font=font_info)

    # 5. Tulis Ulasan dengan Pembungkusan Teks (Wrap)
    max_width = 540
    curr_y = 1385
    words = str(ulasan).split()
    lines = []
    curr_line = ""

    for w in words:
        test = f"{curr_line} {w}".strip()
        bbox = font_ulasan.getbbox(test)
        if (bbox[2] - bbox[0]) <= max_width:
            curr_line = test
        else:
            lines.append(curr_line)
            curr_line = w
    if curr_line:
        lines.append(curr_line)

    for line in lines[:4]:
        draw.text((40, curr_y), line, fill="#D0D0D0", font=font_ulasan)
        curr_y += 33

    return img.convert("RGB")