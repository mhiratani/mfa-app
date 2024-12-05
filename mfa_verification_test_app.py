import pyotp
import qrcode
from io import StringIO

def generate_ascii_qr(data):
    qr = qrcode.QRCode(version=1, box_size=1, border=1)
    qr.add_data(data)
    qr.make(fit=True)

    # StringIOを使用してASCII QRコードを文字列として取得
    f = StringIO()
    qr.print_ascii(out=f)
    f.seek(0)
    return f.read()

def main():
    # シークレットキーを生成
    secret = pyotp.random_base32()
    print(f"シークレットキー: {secret}")

    # TOTPオブジェクトを作成
    totp = pyotp.TOTP(secret)

    # QRコードをASCII文字で生成
    qr_data = totp.provisioning_uri("テストユーザー", issuer_name="テストアプリ")
    ascii_qr = generate_ascii_qr(qr_data)

    print("以下のQRコードをMFAアプリ（Google AuthenticatorやAuthyなど）でスキャンしてください：")
    print(ascii_qr)

    print("\nQRコードが読み取れない場合は、以下のシークレットキーを手動で入力してください：")
    print(secret)

    # ユーザーに確認コードの入力を求める
    while True:
        user_input = input("\nMFAアプリに表示されている6桁のコードを入力してください: ")
        
        if totp.verify(user_input):
            print("検証成功！MFAが正しく設定されました。")
            break
        else:
            print("検証失敗。もう一度試してください。")

if __name__ == "__main__":
    print("===== テスト用MFA検証アプリ =====")
    main()
    print("===== テスト終了 =====")