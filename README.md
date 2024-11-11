# Django Authentication API

Django ve Djoser tabanlı kapsamlı bir kimlik doğrulama ve kullanıcı yönetimi API'si.

## Özellikler

- JWT tabanlı kimlik doğrulama
- Email doğrulama ve aktivasyon
- Şifre sıfırlama ve değiştirme
- Kapsamlı profil yönetimi
- Avatar yükleme ve yönetimi
- IP tabanlı rate limiting
- CORS ve güvenlik önlemleri
- Admin yönetim paneli
- API dokümantasyonu (Swagger/ReDoc)

## Teknolojiler

- Python 3.10+
- Django 4.2.7
- Django REST Framework
- Djoser
- MySQL
- Redis
- MailHog (Development)

## Kurulum

1. Repository'yi klonlayın:
```bash
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME
```

2. Virtual environment oluşturun:
```bash
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
myenv\Scripts\activate     # Windows
```

3. Gereksinimleri yükleyin:
```bash
pip install -r requirements/development.txt
```

4. .env dosyasını oluşturun:
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

5. MySQL veritabanını oluşturun:
```bash
mysql -u root -p
CREATE DATABASE django_auth_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. Migrasyonları uygulayın:
```bash
python manage.py migrate
```

7. Süper kullanıcı oluşturun:
```bash
python manage.py createsuperuser
```

8. MailHog'u başlatın (Docker ile):
```bash
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

9. Uygulamayı çalıştırın:
```bash
python manage.py runserver
```

## API Dokümantasyonu

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Development

1. Development branch'inde çalışın:
```bash
git checkout development
```

2. Yeni özellik eklerken:
```bash
git checkout -b feature/your-feature-name
# Değişiklikleri yapın
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature-name
```

3. Pull Request oluşturun:
- feature -> development
- development -> main (release için)

## Test

```bash
# Tüm testleri çalıştır
python manage.py test

# Coverage raporu
coverage run manage.py test
coverage report
```

## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.