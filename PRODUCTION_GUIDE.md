# 🚀 Production Deployment & Management Guide

This document contains all the steps required to deploy, manage, and maintain your "Drop Down" store in a real-world environment.

---

## 1. Initial Deployment (Render.com)
Your project is already configured for Render using the `render.yaml` blueprint.

1. **Connect GitHub**: Log in to [Render Dashboard](https://dashboard.render.com), click **New +** > **Blueprint**, and select your `drop-down` repo.
2. **Environment Variables**: Once the service is created, go to the **drop-web** service > **Environment** and add:
   - `CLOUDINARY_CLOUD_NAME`: From your Cloudinary dashboard.
   - `CLOUDINARY_API_KEY`: From your Cloudinary dashboard.
   - `CLOUDINARY_API_SECRET`: From your Cloudinary dashboard.
   - `PAYSTACK_SECRET_KEY`: Use your **Live** secret key from Paystack.
   - `SECRET_KEY`: (Render generates one, but you can paste your own).

---

## 2. Post-Deployment Setup (Critical)
Once Render says "Live", you must perform these steps:

### Create Admin Account
1. In Render, go to your **drop-web** service.
2. Click **Shell** in the left sidebar.
3. Run: `python manage.py createsuperuser`
4. Follow prompts to create your login.

### Initialize Store Data
1. Visit `https://drop-web.onrender.com/admin` and log in.
2. **Categories**: Create categories (e.g., "Men", "Women", "Wristwatches").
3. **Products**: Add your first products. Ensure you upload images (they will auto-save to Cloudinary).

---

## 3. Mobile App (Flutter)
The mobile app is now configured to point to `https://drop-web.onrender.com`.

### Build for Production
Run these commands in your terminal (inside the `mobile/` folder):
1. `flutter clean`
2. `flutter pub get`
3. `flutter build apk --release`

The file will be located at: `build/app/outputs/flutter-apk/app-release.apk`

---

## 4. Maintenance & Monitoring
- **Error Tracking**: Log in to [Sentry.io](https://sentry.io) to see if users are experiencing crashes.
- **Background Tasks**: Visit `https://drop-web.onrender.com/ht/` to check the health of your Database and Redis.
- **Worker Management**: Monitor background tasks (like emails) via the **drop-worker** logs in Render.

---

## 5. Scaling for the Future
- **Domain**: Add a custom domain in Render Settings (e.g., `www.dropdownstore.com`).
- **Database**: The "Free" database on Render expires after 90 days. Upgrade to the **Starter ($7/mo)** plan before then to keep your data forever.
- **Email**: For high volume, switch `EMAIL_HOST` in `.env` from Gmail to **SendGrid** or **Amazon SES**.

---

**Generated on:** June 2024
**Status:** Production Ready ✅
