from werkzeug.security import generate_password_hash

def hash_password():
    plain_password = input("Masukkan password: ")
    hashed = generate_password_hash(plain_password)
    print("\n=== HASHED PASSWORD ===")
    print(hashed)

if __name__ == "__main__":
    hash_password()
