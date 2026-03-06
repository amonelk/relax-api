import secrets
import string

def generate_secure_sk(length=32):
    """
    生成一个安全的随机字符串作为 SK。
    包含大小写字母和数字，避免易混淆字符（如 l, 1, O, 0）。
    """
    # 定义字符集 (去掉容易混淆的字符)
    alphabet = string.ascii_letters + string.digits
    # 过滤掉 l, 1, O, 0 (可选)
    alphabet = ''.join(c for c in alphabet if c not in 'l1O0')
    
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# 使用示例
sk = generate_secure_sk(32)
print(f"生成的 SK: {sk}")