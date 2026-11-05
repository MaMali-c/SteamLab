# بسته نهایی شخصی — ۶ نوامبر ۲۰۲۶

- نام محمدعلی شمشیری در پایین همه صفحات.
- نمودار تعاملی فشار اشباع آب برحسب دما، تنظیم بازه و واحد فشار، مقیاس لگاریتمی و نمایش نقطه انتخابی.
- ۱۱۲ تست خودکار موفق روی مک؛ گزارش بسته در `final-test-results.xml`.
- بررسی ظاهری نمودار جدید در Chrome انجام نشده است؛ اتصال مرورگر برقرار نبود.
- کد کامل، راهنما، تست‌ها، داده‌های مرجع و PDF اصلی داخل بسته هستند.
- یادداشت‌های زیر مربوط به نسخه اولیه‌اند؛ نمودار فشار بخار بعداً اضافه شده است.

# V1.0.0 (نسخه اول)

Implemented and tested:

- Bilingual English (Persian) user-facing labels, notes and domain errors.
- Real TP/PX/TX calculations with undefined single-phase quality.
- An explicit saturation-ambiguity flow and conservative critical-quality guard.
- Traceable 19-record PDF sample; 1D interpolation and visible calculation steps.
- Separate IF97 reference validation and historical PDF comparison.
- Input preservation across page navigation, physically consistent unit changes,
  stale-result handling and removal of results after failed calculations.
- Navy/blue and light appearances, with wrapping layouts for small screens.
- Complete source, Persian macOS guide, English README, scientific documentation,
  automated tests and a configured (not remotely executed) CI workflow.

Validated locally with Python 3.12.14 on Linux, iapws 1.5.5 and Streamlit 1.66.1.
103 pytest tests and all 51 scalar official-reference checks passed.
Chromium desktop and mobile viewport checks completed without JavaScript errors.
No direct macOS execution is claimed.

Not implemented: PH/PS input, Plotly diagrams, bilinear interpolation, full-PDF OCR,
equipment/Rankine analysis, PDF/Excel/CSV export controls and multi-state comparison.
The CSV files supplied under docs/validation are developer-generated validation
artifacts, not a user-facing export feature.
