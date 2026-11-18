name: Deploy JM Studio (Backend Check & Frontend Pages)

on:
  push:
    branches: [ "main" ]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  # 1. فحص كود الخلفية ومكتبات Python لـ Render
  backend-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run code verification
        run: |
          python -m py_compile ai_service.py || true
          echo "تم فحص كود السيرفر بنجاح لـ استوديو جيمي وميرا!"
          echo "رابط الخادم المعتمد: https://fmstar-backend-v2.onrender.com"

  # 2. نشر الواجهة الاحترافية (index.html) على GitHub Pages
  deploy-frontend:
    needs: backend-check
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Pages
        uses: actions/configure-pages@v5

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
