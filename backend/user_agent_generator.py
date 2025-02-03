import random

# إعداد بيانات لأنظمة التشغيل والمتصفحات
OPERATING_SYSTEMS = [
    'Windows NT 10.0; Win64; x64',
    'Macintosh; Intel Mac OS X 10_15_7',
    'X11; Linux x86_64',
    'Windows NT 6.1; WOW64',
    'iPhone; CPU iPhone OS 14_2 like Mac OS X',
    'Android 11; Mobile',
    'iPad; CPU OS 13_2_3 like Mac OS X'
]

BROWSERS = [
    ('Chrome', 'Safari/537.36', 80, 122),
    ('Firefox', 'Gecko/20100101 Firefox', 45, 120),
    ('Safari', 'Version', 10, 15),
    ('Edge', 'Edg', 80, 110)
]

# توليد User-Agent عشوائي
def generate_random_user_agent():
    os = random.choice(OPERATING_SYSTEMS)
    browser, engine, min_ver, max_ver = random.choice(BROWSERS)
    version = f"{random.randint(min_ver, max_ver)}.0.{random.randint(0, 9999)}.{random.randint(0, 99)}"

    if browser == 'Safari':
        return f"Mozilla/5.0 ({os}) AppleWebKit/605.1.15 (KHTML, like Gecko) {engine}/{version} Mobile/15E148 Safari/604.1"
    elif browser == 'Firefox':
        return f"Mozilla/5.0 ({os}; rv:{version}) {engine}/{version}"
    elif browser == 'Edge':
        return f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} {engine}/{version}"
    else:  # Chrome
        return f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) {browser}/{version} {engine}"

# إنشاء 1000 User-Agent
USER_AGENTS = [generate_random_user_agent() for _ in range(1000)]

# دالة توليد User-Agent عشوائي عند الطلب
def generate_user_agent():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9'
    }
