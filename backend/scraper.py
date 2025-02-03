import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
import random
from difflib import SequenceMatcher
from user_agent_generator import generate_user_agent  # ✅ استدعاء مولد الـ User-Agent

# ✅ كلمات يجب استبعاد المنتجات التي تحتوي عليها
EXCLUDED_KEYWORDS = [
    'long sleeve', 'hoodie', 'sweatshirt', 'v-neck', 'vinyl shirt',
    'premium t-shirt', 'tank top', 'polo', 'raglan', 'shorts'
]

# ✅ إعداد الكوكيز
COOKIES = {
    "lc-main": "en_US",
    "i18n-prefs": "USD",
    "session-id": "130-7384185-5606739",
    "ubid-main": "131-5391624-1279526"
}

# ✅ مقارنة تشابه الكلمات بنسبة معينة (للسماح بأخطاء بسيطة)
def is_similar(a, b, threshold=0.7):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

# ✅ استخراج تفاصيل المنتج
import re

async def fetch_product_details(session, asin):
    try:
        url = f"https://www.amazon.com/dp/{asin}"
        async with session.get(url, headers=generate_user_agent(), cookies=COOKIES, timeout=10) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')

            # استخراج BSR
            bsr_list = []
            bsr_tags = soup.find_all('span', string=re.compile('Best Sellers Rank'))
            for tag in bsr_tags:
                bsr_text = tag.find_next('span').get_text(strip=True)
                bsr_matches = re.findall(r'#\d{1,3}(?:,\d{3})*', bsr_text)
                bsr_list.extend([bsr.replace('#', '') for bsr in bsr_matches])

            if not bsr_list:
                bsr_list = ['N/A']  # عرض N/A إذا لم يتم العثور على BSR

            # استخراج عدد التقييمات
            ratings_count_tag = soup.select_one('#acrCustomerReviewText')
            ratings_count = ratings_count_tag.text.split()[0] if ratings_count_tag else '0'

            # استخراج تاريخ النشر
            date_tag = soup.find('span', string=re.compile('Date First Available'))
            date_published = date_tag.find_next('span').text.strip() if date_tag else 'N/A'

            return bsr_list, ratings_count, date_published

    except Exception as e:
        print(f"❌ Error fetching product details for ASIN {asin}: {e}")
        return ['N/A'], '0', 'N/A'  # عرض البيانات الناقصة بدلاً من تجاهل المنتج

async def fetch_search_results(session, keyword, page):
    search_url = (
        f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
        f"&rh=n%3A7141123011%2Cp_6%3AATVPDKIKX0DER"
        f"&s=exact-aware-popularity-rank&dc&page={page}"
    )

    try:
        await asyncio.sleep(random.uniform(1, 3))  # تأخير عشوائي لتجنب الحظر
        async with session.get(search_url, headers=generate_user_agent(), cookies=COOKIES, timeout=15) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            return soup.find_all('div', {'data-asin': True})

    except Exception as e:
        print(f"❌ Error fetching page {page}: {e}")
        return []

# ✅ معالجة كل منتج
from nltk.corpus import wordnet  # ✅ استدعاء مكتبة WordNet للمرادفات

# ✅ دالة للحصول على مرادفات الكلمة
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower())
    return synonyms

# ✅ تعديل التحقق من الكلمات الرئيسية للسماح بالمرادفات
async def process_product(session, div, keyword):
    asin = div.get('data-asin')
    if not asin:
        return None

    title_tag = div.select_one('h2 a span') or div.select_one('.a-size-base-plus.a-color-base.a-text-normal')
    title = title_tag.text.strip() if title_tag else 'N/A'

    # استبعاد المنتجات التي تحتوي على كلمات محظورة
    if any(word.lower() in title.lower() for word in EXCLUDED_KEYWORDS):
        return None

    # ✅ التحقق من وجود الكلمات الرئيسية أو مرادفاتها
    required_keywords = keyword.lower().split()
    title_words = title.lower().split()

    for word in required_keywords:
        synonyms = get_synonyms(word)  # ✅ الحصول على المرادفات
        synonyms.add(word)  # إضافة الكلمة الأصلية مع المرادفات

        if not any(any(is_similar(synonym, title_word) for title_word in title_words) for synonym in synonyms):
            return None

    image_tag = div.select_one('img.s-image')
    image = image_tag['src'] if image_tag else ''

    product_link_tag = div.select_one('h2 a')
    product_link = f"https://www.amazon.com{product_link_tag['href']}" if product_link_tag else f"https://www.amazon.com/dp/{asin}"

    bsr, ratings, date_published = await fetch_product_details(session, asin)

    return {
        'asin': asin,
        'title': title,
        'bsr': bsr,
        'ratings': ratings,
        'date_published': date_published,
        'image': image,
        'link': product_link
    }


# ✅ الدالة الرئيسية لجلب البيانات من أمازون
async def scrape_amazon(keyword, pages=1):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page in range(1, pages + 1):
            print(f"🔍 Fetching page {page}...")
            product_containers = await fetch_search_results(session, keyword, page)
            print(f"✅ Page {page}: Found {len(product_containers)} products.")

            for div in product_containers:
                tasks.append(process_product(session, div, keyword))

        products = await asyncio.gather(*tasks)
        products = [product for product in products if product]  # حذف النتائج الفارغة

        print(f"🚀 Total products extracted: {len(products)}")
        return products

# ✅ لتشغيل السكريبت بشكل غير متزامن
def run_scraper(keyword, pages=1):
    return asyncio.run(scrape_amazon(keyword, pages))
