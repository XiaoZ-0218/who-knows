import hashlib
import hmac
import json

from who_knows.deployhook import should_deploy, verify_signature


def test_verify_signature_accepts_matching_hmac():
    secret = "s3cret"
    body = b'{"ok":true}'
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert verify_signature(secret, body, "sha256=" + digest) is True


def test_verify_signature_rejects_mismatch():
    assert verify_signature("s3cret", b"{}", "sha256=deadbeef") is False


def test_should_deploy_only_main_push():
    payload = {"ref": "refs/heads/main"}
    assert should_deploy("push", payload) is True
    assert should_deploy("push", {"ref": "refs/heads/dev"}) is False
    assert should_deploy("ping", payload) is False
