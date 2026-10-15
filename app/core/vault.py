import base64
import hashlib
import hmac
import os
import pty
import re
import select
import shutil
import socket
import subprocess
import tempfile
import time
from typing import Optional, Tuple, List, Dict, Any

from app.core.config import settings

try:
    from cryptography.fernet import Fernet
    _HAS_FERNET = True
except ImportError:
    _HAS_FERNET = False


def _derive_vault_key_bytes() -> bytes:
    """
    派生 32 字节的服务器凭据加密主密钥：
    优先读取环境变量 SERVER_VAULT_SECRET_KEY，未设置时基于 API_KEY 或固定应用盐值通过 PBKDF2-HMAC-SHA256 派生。
    """
    raw_secret = (
        os.getenv("SERVER_VAULT_SECRET_KEY")
        or getattr(settings, "SERVER_VAULT_SECRET_KEY", "")
        or getattr(settings, "API_KEY", "")
        or "agent-control-default-vault-master-key-2026"
    )
    salt = b"agent-control-server-vault-v1-salt"
    return hashlib.pbkdf2_hmac("sha256", raw_secret.encode("utf-8"), salt, 100_000, dklen=32)


def encrypt_secret(plain_text: Optional[str]) -> Optional[str]:
    """
    将明文密码或私钥加密为密文存储（数据库只存密文，绝不落盘明文）。
    支持 Fernet (AES-128-CBC + HMAC-SHA256) 与标准库兼容回退。
    """
    if plain_text is None or plain_text == "":
        return None
    key_bytes = _derive_vault_key_bytes()
    if _HAS_FERNET:
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        token = Fernet(fernet_key).encrypt(plain_text.encode("utf-8"))
        return "fernet:" + token.decode("utf-8")

    # 标准库回退：随机 16 字节 nonce + CTR 异或流 + HMAC-SHA256 完整性签名
    nonce = os.urandom(16)
    data = plain_text.encode("utf-8")
    stream = bytearray()
    counter = 0
    while len(stream) < len(data):
        block = hmac.new(key_bytes, nonce + counter.to_bytes(4, "big"), hashlib.sha256).digest()
        stream.extend(block)
        counter += 1
    cipher_bytes = bytes(a ^ b for a, b in zip(data, stream[: len(data)]))
    mac = hmac.new(key_bytes, nonce + cipher_bytes, hashlib.sha256).digest()
    payload = base64.urlsafe_b64encode(nonce + mac + cipher_bytes).decode("utf-8")
    return "stdv1:" + payload


def decrypt_secret(cipher_text: Optional[str]) -> Optional[str]:
    """
    在受控后端进程内存中解密服务器密码或私钥。
    严禁将返回值直接序列化到任何 HTTP 响应或日志中。
    """
    if not cipher_text:
        return None
    key_bytes = _derive_vault_key_bytes()
    if cipher_text.startswith("fernet:"):
        raw_token = cipher_text[len("fernet:") :].encode("utf-8")
        if _HAS_FERNET:
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            return Fernet(fernet_key).decrypt(raw_token).decode("utf-8")
        raise RuntimeError("Decrypting fernet token requires cryptography package")
    elif cipher_text.startswith("stdv1:"):
        raw = base64.urlsafe_b64decode(cipher_text[len("stdv1:") :].encode("utf-8"))
        nonce, mac, cipher_bytes = raw[:16], raw[16:48], raw[48:]
        expected_mac = hmac.new(key_bytes, nonce + cipher_bytes, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("Vault cipher integrity check failed")
        stream = bytearray()
        counter = 0
        while len(stream) < len(cipher_bytes):
            block = hmac.new(key_bytes, nonce + counter.to_bytes(4, "big"), hashlib.sha256).digest()
            stream.extend(block)
            counter += 1
        plain_bytes = bytes(a ^ b for a, b in zip(cipher_bytes, stream[: len(cipher_bytes)]))
        return plain_bytes.decode("utf-8")
    else:
        # 兼容未带前缀的 Fernet Token
        if _HAS_FERNET:
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            return Fernet(fernet_key).decrypt(cipher_text.encode("utf-8")).decode("utf-8")
        raise ValueError("Unsupported cipher format")


def mask_secret(cipher_text: Optional[str]) -> str:
    """对外展示固定掩码，绝不暴露密码长度或真实字符"""
    return "********" if cipher_text else ""


def redact_sensitive_output(text: Optional[str], secrets_to_redact: Optional[List[Optional[str]]] = None) -> str:
    """
    对命令输出、错误堆栈、审计日志进行敏感词清洗，确保密码或私钥绝不泄露至 Agent 上下文。
    """
    if not text:
        return ""
    cleaned = text
    for sec in (secrets_to_redact or []):
        if sec and len(sec.strip()) >= 3:
            s = sec.strip()
            cleaned = cleaned.replace(s, "[REDACTED_SECRET]")
    # 过滤常见密码提示回显
    cleaned = re.sub(r"(?i)(password|passphrase)\s*for\s*[^\r\n:]+:\s*", "", cleaned)
    cleaned = re.sub(r"(?i)[^\r\n]*'s password:\s*", "", cleaned)
    return cleaned


def test_tcp_and_ssh_banner(host: str, port: int = 22, timeout: float = 5.0) -> Dict[str, Any]:
    """
    测试目标服务器 IP:Port 的 TCP 连通性与 SSH 协议握手 Banner。
    """
    start_ts = time.time()
    try:
        with socket.create_connection((host, int(port)), timeout=timeout) as sock:
            sock.settimeout(timeout)
            banner = ""
            try:
                raw_banner = sock.recv(256)
                banner = raw_banner.decode("utf-8", errors="ignore").strip()
            except Exception:
                banner = "TCP Connected (No immediate SSH banner)"
            latency_ms = round((time.time() - start_ts) * 1000, 2)
            return {
                "reachable": True,
                "status": "online",
                "latency_ms": latency_ms,
                "banner": banner or "TCP Connected",
                "message": f"端口连通正常 ({latency_ms} ms)" + (f" · {banner}" if banner else ""),
            }
    except Exception as exc:
        latency_ms = round((time.time() - start_ts) * 1000, 2)
        return {
            "reachable": False,
            "status": "unreachable",
            "latency_ms": latency_ms,
            "banner": "",
            "message": f"连接失败: {str(exc)}",
        }


def _run_ssh_or_scp_with_pty(
    argv: List[str],
    password: Optional[str] = None,
    private_key: Optional[str] = None,
    timeout: int = 60,
) -> Tuple[int, str, float]:
    """
    使用伪终端 (PTY) 安全执行 ssh / scp 命令：
    - 密码通过 PTY 文件描述符在内存态直接注入，绝不出现在命令行参数 (ps aux) 或环境变量中；
    - 私钥通过 0600 权限临时文件挂载并在执行完毕后立即销毁；
    - 所有输出自动剥离密码提示并清洗敏感凭据。
    """
    start_ts = time.time()
    temp_key_path = None
    secrets_list = [password, private_key]

    try:
        final_argv = list(argv)
        if private_key and private_key.strip():
            fd, temp_key_path = tempfile.mkstemp(prefix="ac_ssh_key_", suffix=".pem")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                key_content = private_key.strip() + "\n"
                f.write(key_content)
            os.chmod(temp_key_path, 0o600)
            # 在 ssh / scp 命令后插入 -i <temp_key_path>
            final_argv = [final_argv[0], "-i", temp_key_path] + final_argv[1:]

        master_fd, slave_fd = pty.openpty()
        proc = subprocess.Popen(
            final_argv,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
             env={**os.environ, "LANG": "en_US.UTF-8", "LC_ALL": "en_US.UTF-8"},
        )
        os.close(slave_fd)

        output_chunks: List[bytes] = []
        password_sent = False
        deadline = time.time() + max(timeout, 5)

        try:
            while True:
                remaining = deadline - time.time()
                if remaining <= 0:
                    proc.kill()
                    output_chunks.append(b"\n[ERROR] Remote execution timed out.")
                    break

                rlist, _, _ = select.select([master_fd], [], [], min(0.2, remaining))
                if master_fd in rlist:
                    try:
                        data = os.read(master_fd, 4096)
                    except OSError:
                        break
                    if not data:
                        break
                    output_chunks.append(data)
                    decoded_tail = b"".join(output_chunks[-3:]).decode("utf-8", errors="ignore")
                    if (
                        not password_sent
                        and password is not None
                        and re.search(r"(?i)(password|passphrase)\s*:", decoded_tail)
                    ):
                        os.write(master_fd, (password + "\n").encode("utf-8"))
                        password_sent = True
                else:
                    if proc.poll() is not None:
                        break
        finally:
            try:
                os.close(master_fd)
            except OSError:
                pass

        exit_code = proc.wait(timeout=5)
        duration_sec = round(time.time() - start_ts, 3)
        raw_output = b"".join(output_chunks).decode("utf-8", errors="replace")
        clean_output = redact_sensitive_output(raw_output, secrets_list).strip()
        return exit_code, clean_output, duration_sec

    finally:
        if temp_key_path and os.path.exists(temp_key_path):
            try:
                os.remove(temp_key_path)
            except OSError:
                pass


def execute_remote_command(
    host: str,
    port: int,
    username: str,
    command: str,
    password_cipher: Optional[str] = None,
    private_key_cipher: Optional[str] = None,
    workdir: Optional[str] = None,
    timeout: int = 60,
) -> Dict[str, Any]:
    """
    免密托管执行远程服务器 Shell 命令。
    """
    password = decrypt_secret(password_cipher) if password_cipher else None
    private_key = decrypt_secret(private_key_cipher) if private_key_cipher else None

    remote_cmd = command.strip()
    if workdir and workdir.strip():
        safe_wd = workdir.strip()
        remote_cmd = f"cd {sh_quote(safe_wd)} && {remote_cmd}"

    ssh_bin = shutil.which("ssh") or "/usr/bin/ssh"
    ssh_opts = [
        ssh_bin,
        "-p",
        str(port or 22),
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "LogLevel=ERROR",
    ]
    if not password and not private_key:
        ssh_opts += ["-o", "BatchMode=yes"]

    ssh_opts.append(f"{username}@{host}")
    ssh_opts.append(remote_cmd)

    exit_code, output, duration_sec = _run_ssh_or_scp_with_pty(
        ssh_opts, password=password, private_key=private_key, timeout=timeout
    )
    return {
        "success": exit_code == 0,
        "exit_code": exit_code,
        "output": output,
        "duration_sec": duration_sec,
    }


def transfer_remote_file(
    direction: str,
    host: str,
    port: int,
    username: str,
    local_path: str,
    remote_path: str,
    password_cipher: Optional[str] = None,
    private_key_cipher: Optional[str] = None,
    recursive: bool = False,
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    免密托管上传 (upload) 或下载 (download) 服务器文件/目录 (基于 SCP + PTY 注入)。
    direction: 'upload' | 'download'
    """
    password = decrypt_secret(password_cipher) if password_cipher else None
    private_key = decrypt_secret(private_key_cipher) if private_key_cipher else None

    scp_bin = shutil.which("scp") or "/usr/bin/scp"
    scp_argv = [
        scp_bin,
        "-P",
        str(port or 22),
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "LogLevel=ERROR",
    ]
    if recursive:
        scp_argv.append("-r")
    if not password and not private_key:
        scp_argv += ["-o", "BatchMode=yes"]

    remote_spec = f"{username}@{host}:{remote_path}"
    if direction == "upload":
        scp_argv += [local_path, remote_spec]
    elif direction == "download":
        scp_argv += [remote_spec, local_path]
    else:
        raise ValueError(f"Unsupported transfer direction: {direction}")

    exit_code, output, duration_sec = _run_ssh_or_scp_with_pty(
        scp_argv, password=password, private_key=private_key, timeout=timeout
    )
    return {
        "success": exit_code == 0,
        "direction": direction,
        "local_path": local_path,
        "remote_path": remote_path,
        "exit_code": exit_code,
        "output": output,
        "duration_sec": duration_sec,
    }


def sh_quote(s: str) -> str:
    """安全转义 Shell 单引号参数"""
    return "'" + s.replace("'", "'\"'\"'") + "'"
