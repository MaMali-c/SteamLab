# راهنمای انتشار termoyazd

مستند کامل و به‌روز: [Deployment guide](docs/DEPLOYMENT.md).

پوشه ریشه برنامه در سرویس میزبانی باید **termoyazd** باشد، چون نام مخزن SteamLab است و برنامه در زیرپوشه قرار دارد.

دو مسیر وجود دارد: نسخه ایستا با Python مرورگری که سرور جدا نمی‌خواهد، یا React روی Vercel و FastAPI روی Render. برای مسیر دوم، آدرس واقعی HTTPS سرور و CORS دقیق لازم است. متغیرهای VITE عمومی‌اند و نباید رمز در آن‌ها گذاشت.

برای آماده‌سازی روی مک، پس از نصب Node:

```bash
cd SteamLab/termoyazd
npm --prefix frontend ci
npm run build
npm --prefix frontend run preview -- --port 4173
```

این فقط پیش‌نمایش محلی است؛ لینک عمومی بعد از انتشار واقعی و آزمون آدرس صادرشده توسط میزبان قابل ارائه است. در این مرحله هیچ آدرس سایت تأییدنشده ادعا نمی‌شود.
