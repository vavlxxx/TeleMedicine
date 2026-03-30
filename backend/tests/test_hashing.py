from src.utils.security import hash_password, hash_token, verify_password


def test_hash_password_and_verify() -> None:
    plain = "StrongPass!123"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)


def test_hash_token() -> None:
    token = "sample-token"
    hashed = hash_token(token)
    assert hashed
    assert hashed != token
