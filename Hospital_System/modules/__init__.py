import qrcode

img = qrcode.make("Hospital System QR Test")
img.save("test_qr.png")

print("QR berhasil dibuat")
