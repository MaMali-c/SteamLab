# نصب و اجرای termoyazd روی ویندوز

این راهنما برای **Windows 10/11، ترجیحاً نسخه ۶۴ بیتی x64** و PowerShell نوشته شده است. اجرای واقعی روی ویندوز در محیط فعلی انجام نشده؛ دستورها با ساختار پروژه و مستندات رسمی ابزارها تطبیق داده شده‌اند. موتور علمی یا رابط برنامه برای این راهنما تغییر نکرده‌اند.

## ۱. نصب پیش‌نیازها

- **Python 3.14 پایدار** از [python.org](https://www.python.org/downloads/windows/). از نسخه آزمایشی استفاده نکنید. [راهنمای رسمی Python در ویندوز](https://docs.python.org/3.14/using/windows.html) نصب‌کننده‌های موجود را توضیح می‌دهد.
- **Node.js نسخه 22 یا 24** از [nodejs.org](https://nodejs.org/en/download/)، متناسب با معماری دستگاه. npm همراه آن نصب می‌شود. محدوده پروژه Node 22 تا قبل از 25 است؛ نسخه بالاتر را صرفاً به دلیل جدیدتر بودن انتخاب نکنید.
- **Git اختیاری** است؛ می‌توانید به جای آن ZIP مخزن را دریافت کنید.

بعد از نصب، PowerShell را ببندید و دوباره باز کنید:

~~~powershell
py -3.14 --version
node --version
npm.cmd --version
~~~

اگر دستور py پیدا نشد ولی Python 3.14 نصب است، با دستور python --version نسخه را بررسی و در مرحله ساخت محیط، از python -m venv .venv استفاده کنید.

در این راهنما عمداً از npm.cmd و مسیر مستقیم python.exe استفاده می‌کنیم؛ اجرای Activate.ps1 یا تغییر Execution Policy لازم نیست.

## ۲. دریافت پروژه

**روش Git:**

~~~powershell
git clone https://github.com/MaMali-c/SteamLab.git
Set-Location .\SteamLab\termoyazd
~~~

**روش بدون Git:** در [صفحه مخزن](https://github.com/MaMali-c/SteamLab) روی **Code → Download ZIP** بزنید، فایل را با **Extract All** باز کنید و وارد پوشه termoyazd شوید. مثلاً اگر ZIP را در Downloads باز کرده‌اید:

~~~powershell
Set-Location "$env:USERPROFILE\Downloads\SteamLab-main\termoyazd"
~~~

مسیر را متناسب با محل واقعی فایل تغییر دهید. در این پوشه باید frontend، backend و package.json را ببینید:

~~~powershell
Get-ChildItem
~~~

فایل start.command راه‌انداز macOS است؛ برای ویندوز از مراحل زیر استفاده کنید.

## ۳. نصب وابستگی‌ها؛ فقط بار اول یا پس از تغییر وابستگی‌ها

همه دستورها از داخل پوشه termoyazd اجرا می‌شوند:

~~~powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
npm.cmd --prefix frontend ci
~~~

اگر هر مرحله خطا داد، همان خطا را برطرف کنید و بعد ادامه دهید. برای نصب اولیه اینترنت لازم است. محیط مجازی macOS/Linux را به ویندوز کپی نکنید؛ آن را روی خود ویندوز بسازید. requirements-dev شامل وابستگی‌های برنامه و آزمون‌های Python است. نسخه‌های دقیق محیط مرجع CI نیز جداگانه در backend/requirements-ci.txt ثبت شده‌اند.

## ۴. اجرای بک‌اند در پنجره اول

در PowerShell اول، از داخل termoyazd:

~~~powershell
$env:TERMOYAZD_ENV = "development"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
~~~

صبر کنید پیام آماده‌شدن Uvicorn ظاهر شود و این پنجره را باز نگه دارید.

در پنجره دوم، سلامت سرویس را بررسی کنید:

~~~powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
~~~

پاسخ باید شامل شناسه برنامه termoyazd باشد. مستند تعاملی API در حالت توسعه در آدرس http://127.0.0.1:8000/docs در دسترس است.

## ۵. اجرای فرانت‌اند در پنجره دوم

در پنجره دوم نیز به همان پوشه termoyazd بروید. سپس:

~~~powershell
$env:VITE_BROWSER_ENGINE = "false"
$env:VITE_API_TARGET = "http://127.0.0.1:8000"
npm.cmd --prefix frontend run dev -- --port 5173 --strictPort
~~~

بعد از نمایش پیام آماده‌شدن Vite، آدرس **http://localhost:5173** را در مرورگر باز کنید. برای کنترل اتصال واقعی رابط به بک‌اند، آدرس http://localhost:5173/api/health را نیز باز کنید.

در این مسیر، Vite درخواست‌های /api را به FastAPI می‌فرستد؛ نیاز نیست تنظیم امنیتی CORS را ضعیف کنید. هر دو پنجره باید باز بمانند. برای توقف، در هر پنجره Ctrl+C بزنید.

## ۶. آزمایش یک محاسبه واقعی

در رابط، زوج T + P را انتخاب کنید و **T=300 °C، P=500 kPa** بدهید. خروجی تقریبی مورد انتظار:

| خاصیت | مقدار تقریبی | واحد |
|---|---:|---|
| h | 3064.5962 | kJ/kg |
| u | 2803.2948 | kJ/kg |
| s | 7.461448 | kJ/(kg·K) |
| v | 0.5226028 | m³/kg |

این مقادیر از [پاسخ واقعی ثبت‌شده FastAPI](../examples/T_P.response.json) آمده‌اند؛ آزمایش روی ویندوز هنوز مستقلاً تأیید نشده است.

برای ارسال مستقیم درخواست، در یک پنجره سوم:

~~~powershell
$payload = @{
    input_pair = "T_P"
    values = @{ T = 300; P = 500 }
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri http://127.0.0.1:8000/api/calculate -Method Post -ContentType "application/json" -Body $payload
~~~

## ۷. اجرای دوباره در روزهای بعد

نصب وابستگی‌ها را معمولاً تکرار نکنید. در پوشه termoyazd، بک‌اند را طبق مرحله ۴ و فرانت‌اند را طبق مرحله ۵ اجرا کنید. اگر فایل وابستگی‌ها تغییر کرده است، مرحله نصب مربوط را تکرار کنید.

## ۸. ساخت نسخه تولید و پیش‌نمایش موتور مرورگری

این مسیر همان Python علمی را داخل مرورگر اجرا می‌کند و به بک‌اند جدا نیاز ندارد. از پوشه termoyazd:

~~~powershell
$env:VITE_BROWSER_ENGINE = "true"
Remove-Item Env:VITE_API_BASE_URL -ErrorAction SilentlyContinue
npm.cmd run build
npm.cmd --prefix frontend run preview -- --port 4173
~~~

آدرس پیش‌نمایش **http://localhost:4173** است. ساخت اولیه فایل‌های runtime پین‌شده را دانلود و checksum آن‌ها را بررسی می‌کند؛ دسترسی اینترنت لازم است. اولین بارگذاری runtime در مرورگر تقریباً ۳۶ مگابایت است. فایل dist/index.html را با دوبارکلیک باز نکنید؛ از سرور HTTP پیش‌نمایش استفاده کنید.

این پیش‌نمایش، انتشار عمومی نیست. برای استفاده استاد بدون نصب Python/Node، نسخه ساخته‌شده باید واقعاً میزبانی شود؛ [راهنمای انتشار](DEPLOYMENT.md) را ببینید.

## ۹. آزمون‌های اختیاری

با بک‌اند روشن روی پورت 8000، در پنجره سوم و از پوشه termoyazd:

~~~powershell
Push-Location backend
..\.venv\Scripts\python.exe -m pytest -q
Pop-Location
$env:TERMOYAZD_TEST_API = "http://127.0.0.1:8000"
npm.cmd --prefix frontend test
node scripts/verify-browser-engine.mjs
~~~

برای آزمون Pyodide ابتدا ساخت نسخه مرورگری را انجام دهید تا فایل‌های runtime آماده باشند. برخی آزمون‌های رابط، از جمله آزمون نمودار، به API واقعی نیاز دارند. موفقیت روی macOS یا CI لینوکسی، مدرک اجرای ویندوز نیست؛ نتیجه اجرای محلی را جداگانه ثبت کنید.

## رفع خطا

| خطا | راه‌حل |
|---|---|
| py یا node شناخته نمی‌شود | نصب و PATH را بررسی کنید؛ ترمینال را پس از نصب دوباره باز کنید |
| npm.ps1 cannot be loaded | دستورهای همین راهنما با npm.cmd را اجرا کنید |
| Activate.ps1 مسدود است | فعال‌سازی لازم نیست؛ مستقیم .venv\Scripts\python.exe را اجرا کنید |
| پورت 8000 اشغال است | بک‌اند را با --port 8001 اجرا و VITE_API_TARGET را به http://127.0.0.1:8001 تغییر دهید؛ فرانت‌اند را دوباره راه بیندازید |
| پورت 5173 اشغال است | در دستور Vite از --port 5174 استفاده و http://localhost:5174 را باز کنید |
| صفحه باز است ولی محاسبه خطا دارد | سلامت بک‌اند، سپس /api/health از آدرس فرانت‌اند و مقدار VITE_API_TARGET را بررسی کنید |
| No module named ... | وابستگی را با همان python.exe داخل .venv نصب کنید |
| دریافت runtime یا checksum خطا دارد | اتصال و دسترسی به منبع رسمی را بررسی کنید؛ بررسی checksum را حذف نکنید |
| کیفیت یا حالت نامعتبر | واحد و دامنه علمی را بررسی کنید؛ هر خطا، مشکل نصب نیست |

دستورهای bash start.command، source و نحوه VAR=value command مربوط به راهنمای macOS/Linux هستند و نباید عیناً در PowerShell استفاده شوند.

## منابع رسمی

[Python روی Windows](https://docs.python.org/3.14/using/windows.html) · [دریافت Node.js](https://nodejs.org/en/download/) · [نصب npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm/) · [Execution Policies در PowerShell](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies)

[راهنمای کامل فارسی](../README_FA.md) · [راهنمای توسعه](DEVELOPMENT.md)
