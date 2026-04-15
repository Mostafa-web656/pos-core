import os
import django

# عدّل pos_core إذا كان اسم مشروعك مختلف
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pos_core.settings")
django.setup()

from accounts.models import CustomUser, Shop

shops_data = [
    {"username": "shop1owner", "password": "123456", "shop_name": "Shop1"},
    {"username": "shop2owner", "password": "654321", "shop_name": "Shop2"},
    {"username": "shop3owner", "password": "111222", "shop_name": "Shop3"},
]

for data in shops_data:
    if not CustomUser.objects.filter(username=data["username"]).exists():
        user = CustomUser.objects.create_user(username=data["username"], password=data["password"])
        shop = Shop.objects.create(name=data["shop_name"], owner=user)
        print(f"تم إنشاء المحل: {shop.name} واليوزر: {user.username}")
    else:
        print(f"اليوزر {data['username']} موجود بالفعل، تم تخطيه.")
