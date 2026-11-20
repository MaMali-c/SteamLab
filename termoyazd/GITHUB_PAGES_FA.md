# GitHub Pages و موتور مرورگری

GitHub Pages فقط فایل ایستا میزبانی می‌کند و نمی‌تواند FastAPI اجرا کند. termoyazd می‌تواند همان موتور علمی Python را با Pyodide در مرورگر اجرا کند؛ بنابراین نسخه ایستای واقعی ممکن است.

از پوشه `SteamLab/termoyazd`:

```bash
npm --prefix frontend ci
VITE_BROWSER_ENGINE=true VITE_BASE_PATH=/SteamLab/ npm run build
```

خروجی بسته‌بندی‌شده `dist/` است. مسیر پایه برای سایت پروژه این مخزن `/SteamLab/` است؛ برای دامنه اختصاصی ریشه، `/` را استفاده کنید. بار اول فایل‌های runtime حجم قابل توجهی دارند.

قالب workflow در `.github/workflows/pages.yml` **داخل پوشه termoyazd** فعال نیست. برای انتشار واقعی باید یک workflow در `.github/workflows/` ریشه مخزن ساخته و مسیرهای کاری به `termoyazd` اصلاح شود، سپس Pages فعال و خروجی واقعی بررسی شود. این مستند به خودی خود چیزی منتشر نمی‌کند.

[جزئیات انتشار و جایگزین‌ها](docs/DEPLOYMENT.md)
