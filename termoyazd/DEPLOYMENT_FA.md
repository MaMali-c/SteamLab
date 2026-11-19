# انتشار termoyazd برای استفاده استاد

این بسته، نسخه آماده‌سازی انتشار است. در این مرحله هیچ سایت جدیدی منتشر نشده، دسترسی سایت قبلی عمومی نشده و هیچ مخزن GitHub ساخته یا عمومی نشده است. دستورهای انتشار پایین را فقط پس از تصمیم شما برای عمومی‌کردن اجرا کنید.

## انتخاب معماری

**پیشنهاد برای ارائه دانشگاهی: Vercel به‌تنهایی.** نسخه موجود موتور واقعی Python/iapws/SciPy را با Pyodide در Web Worker اجرا می‌کند. استاد فقط مرورگر و اینترنت نیاز دارد؛ نصب Python، Node.js یا اجرای سرور لازم نیست. محاسبه در دستگاه بازدیدکننده انجام می‌شود. بارگذاری اولیه حدود ۳۶ مگابایت فایل علمی دارد و ممکن است چند ثانیه یا بیشتر طول بکشد. Safari و دستگاه واقعی موبایل باید قبل از ارائه نهایی بررسی شوند.

**گزینه درخواستی شما: Vercel + Render.** رابط روی Vercel و موتور FastAPI روی Render اجرا می‌شود. این گزینه برای ارائه API به برنامه‌های دیگر مناسب است و نیاز به تنظیم دقیق آدرس و CORS دارد. مخزن می‌تواند در هر دو روش خصوصی بماند. عمومی‌بودن برنامه مستلزم عمومی‌بودن کد نیست.

## وضعیت امکانات

یازده حلگر و ظاهر تیره و نمودارهای T–s / P–v / P–h حفظ شده‌اند. engine.py، thermo.py و plotting.py با نسخه مبنا به‌صورت SHA-256 یکسان‌اند. ورود/خروج Excel، محاسبات دسته‌ای، ذخیره تاریخچه و پایگاه داده در نسخه بررسی‌شده وجود ندارند. Copy results و خروجی PNG نمودار وجود دارد. برای این قابلیت‌های پیاده‌سازی‌نشده ادعای آزمون یا انتشار نمی‌شود.

## مرحله اول: قرار دادن کد روی GitHub خصوصی از مک

۱. ZIP را باز کنید. پوشه اصلی شامل frontend، backend و vercel.json است.
۲. در GitHub یک Repository خالی با نام termoyazd و **Visibility: Private** بسازید. README اولیه اضافه نکنید. آدرس HTTPS واقعی همان مخزن را کپی کنید.
۳. Terminal را باز کنید، `cd ` بنویسید و پوشه termoyazd را داخل آن بکشید و Enter بزنید.
۴. اگر `git --version` کار نمی‌کند، ابزارهای Apple را با `xcode-select --install` نصب کنید و پس از اتمام دوباره Terminal را باز کنید.
۵. دستورها را اجرا کنید؛ مقدار YOUR-REPOSITORY-URL را با URL واقعی کپی‌شده جایگزین کنید:

```bash
git init -b main
git add .
git commit -m "Prepare termoyazd production deployment"
git remote add origin YOUR-REPOSITORY-URL
git push -u origin main
```

اگر Git نام و ایمیل خواست، هویت Git خود را تنظیم کنید و commit را تکرار کنید. احراز هویت را در GitHub/مدیر اعتبارنامه خودتان انجام دهید؛ توکن را داخل کد یا این گفتگو قرار ندهید. روش جایگزین، GitHub Desktop و گزینه انتشار مخزن خصوصی است.

فایل‌های .env، .venv، node_modules، .runtime، کلیدها و خروجی‌های ساخت در .gitignore حذف شده‌اند. مقادیر نمونه .env.production.example رمز نیستند. فایل PDF فقط مرجع اعتبارسنجی است و در خروجی عمومی سایت کپی نمی‌شود.

## مسیر A: Vercel مستقل، بدون Render

پس از تأیید شما برای انتشار عمومی:

۱. وارد حساب Vercel شوید و GitHub را فقط برای مخزن خصوصی termoyazd مجاز کنید.
۲. یک Project برای همین مخزن تنظیم کنید. Root Directory را ریشه مخزن بگذارید. تنظیمات vercel.json این‌ها هستند:

| تنظیم | مقدار |
|---|---|
| Framework | Vite |
| Install Command | npm --prefix frontend ci |
| Build Command | npm run build |
| Output Directory | dist |
| Node | 22.x |
| VITE_BROWSER_ENGINE | true |
| VITE_API_BASE_URL | خالی / تعریف‌نشده |

۳. هیچ رمز یا API key در VITE_* قرار ندهید؛ این متغیرها داخل JavaScript عمومی ساخته می‌شوند.
۴. Git auto-deploy در vercel.json غیرفعال است تا push به‌تنهایی انتشار ایجاد نکند. برای انتشار دستی با CLI، با Node.js 22 نصب‌شده، از پوشه اصلی اجرا کنید:

```bash
npm --prefix frontend ci
npx vercel@latest login
npx vercel@latest link
npx vercel@latest pull --yes --environment=production
npx vercel@latest build --prod
```

تا این مرحله build محلی است. دستور بعدی **واقعاً نسخه production را منتشر می‌کند**؛ فقط بعد از تأیید انتشار اجرا شود:

```bash
npx vercel@latest deploy --prebuilt --prod
```

۵. فقط URL واقعی خروجی موفق Vercel را برای استاد بفرستید. در تنظیمات Deployment Protection مطمئن شوید Production برای بازدیدکننده معمولی قابل دسترسی است؛ رمز پروژه یا Vercel Authentication روی مسیر عمومی استاد فعال نباشد. این تغییر دسترسی را نیز فقط پس از تأیید عمومی‌کردن انجام دهید.
۶. با مرورگر ناشناس روی کامپیوتری که وارد حساب شما نیست آزمایش کنید: محاسبه، هر سه نمودار، Copy و PNG. وضعیت Loading scientific engine در بارگذاری اول طبیعی است.

## مسیر B: Vercel + FastAPI روی Render

این مسیر یک سرویس عمومی مستقل و در تنظیم فعلی Render یک پلن **پولی Starter** ایجاد می‌کند. هزینه واقعی را در حساب Render بررسی و تأیید کنید. هیچ سرویسی در این مرحله ایجاد نشده است. برای ارائه پایدار، پلن همیشه روشن انتخاب شده؛ Free ممکن است پس از بی‌فعالیتی خاموش شود.

۱. پس از تأیید انتشار/هزینه، در Render حساب GitHub را متصل و Blueprint همین مخزن خصوصی را با render.yaml وارد کنید. قبل از تأیید ساخت سرویس، پلن را بررسی کنید.
۲. runtime برابر Docker، Dockerfile برابر backend/Dockerfile و context برابر ریشه مخزن است. Python 3.14 و وابستگی‌های دقیق آزموده‌شده از requirements-production.txt نصب می‌شوند. health check برابر /api/health است.
۳. برای متغیر TERMOYAZD_CORS_ORIGINS، **origin دقیق frontend نهایی** را وارد کنید: پروتکل https و نام دامنه، بدون slash انتهایی یا مسیر. اگر دامنه نهایی را هنوز ندارید، ابتدا پروژه/دامنه frontend را رزرو کنید. بعد از تغییر این متغیر سرویس را restart/redeploy کنید.
۴. نام سرویس و URL واقعی Render را از داشبورد کپی کنید. TERMOYAZD_ALLOWED_HOSTS به‌طور پیش‌فرض از RENDER_EXTERNAL_HOSTNAME خوانده می‌شود. برای custom domain، hostname دقیق خود را نیز صریحاً تنظیم کنید؛ wildcard پذیرفته نمی‌شود.
۵. روی Vercel همان تنظیمات مسیر A را نگه دارید، ولی متغیرها را تغییر دهید:

```text
VITE_BROWSER_ENGINE=false
VITE_API_BASE_URL=origin واقعی HTTPS سرویس Render، بدون /api
```

۶. Vercel را دوباره build و پس از تأیید منتشر کنید. VITE_* تنظیم زمان build است؛ تغییر آن بدون rebuild کافی نیست. در این حالت فایل‌های سنگین Pyodide از خروجی frontend حذف می‌شوند.
۷. فقط دامنه frontend نهایی را در CORS مجاز کنید. Preview URLهای تصادفی Vercel به‌صورت wildcard مجاز نشده‌اند. برای staging از origin و سرویس جداگانه استفاده کنید. CORS سیستم احراز هویت یا محافظ DDoS نیست.
۸. autoDeployTrigger در Render برابر off است. انتشار بعدی دستی است. HTTPS را خود پلتفرم برقرار می‌کند؛ کلید TLS در مخزن نیست.

## اجرای production و آزمون از مک، پیش از انتشار

برای آزمون توسعه‌دهنده Python 3.14 و Node.js 22 لازم است؛ استاد به آن‌ها نیاز ندارد.

از پوشه اصلی:

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-ci.txt
(cd backend && ../.venv/bin/python -m pytest -q)
npm --prefix frontend ci
npm run build
python3.14 scripts/verify-static-output.py
node scripts/verify-browser-engine.mjs
```

آزمون WebAssembly واقعاً موتور Python/IF97 را اجرا می‌کند، اما آزمون تصویری مرورگر نیست.

برای API، در یک Terminal:

```bash
cd backend
TERMOYAZD_ENV=production \
TERMOYAZD_ALLOWED_HOSTS=localhost,127.0.0.1 \
TERMOYAZD_CORS_ORIGINS=https://professor.example.org \
PORT=8000 ../.venv/bin/python -m uvicorn app.main:app \
  --host 127.0.0.1 --port 8000 --workers 1 --no-proxy-headers
```

در Terminal دوم از پوشه اصلی:

```bash
python3.14 scripts/production_smoke.py \
  --api http://127.0.0.1:8000 --origin https://professor.example.org
TERMOYAZD_TEST_API=http://127.0.0.1:8000 npm --prefix frontend test
```

professor.example.org فقط origin آزمون است، سایت منتشرشده نیست. برای smoke test بعد از انتشار، `--api` و `--origin` را با آدرس‌های واقعی API و frontend جایگزین کنید.

## حدود و کنترل‌های اضافه‌شده

- حداکثر بدنه درخواست ۱۶٬۳۸۴ بایت، حتی برای درخواست chunked.
- هر درخواست محاسبه فقط یک حالت؛ آرایه/batch به‌صراحت رد می‌شود.
- حداکثر دو محاسبه علمی هم‌زمان در هر process؛ درخواست اضافی 503 و Retry-After می‌گیرد.
- یک worker سرور و سقف ۳۲ اتصال هم‌زمان در start-production.sh.
- در نسخه مرورگری سقف صف و درخواست‌های منتظر ۸ و بدنه پیام حدود ۱۶ کیلوبایت است. این محدودیت دستگاه بازدیدکننده است، نه کنترل امنیتی سرور.
- docs، redoc، openapi و debug در production خاموش‌اند؛ هدرهای nosniff و منع frame تنظیم شده‌اند.
- پاسخ محاسبه cache نمی‌شود؛ داده اشباع cache می‌شود.
- این محدودیت‌ها جایگزین rate limiting توزیع‌شده یا WAF برای ترافیک عمومی زیاد نیستند. deadline سخت برای متوقف‌کردن محاسبه CPU در این نسخه اضافه نشده است.

## انتشار فعلی و دسترسی استاد

سایت قبلی termoyazd وجود دارد، ولی هنگام بررسی دسترسی آن فقط برای مالک بود و بازدیدکننده خارجی نداشت. عمومی‌کردن همان سایت، مسیر ساده دیگری است که به GitHub/Vercel/Render نیاز ندارد. این کار نیز تا تأیید صریح شما انجام نمی‌شود. نتیجه آزمون‌های این بسته در deployment/TEST_RESULTS.md است؛ لینک جدیدی ساخته یا حدس زده نشده است.

مراجع تنظیمات: https://vercel.com/docs/project-configuration/vercel-json ، https://vercel.com/docs/project-configuration/git-configuration ، https://render.com/docs/blueprint-spec و https://render.com/docs/docker .
