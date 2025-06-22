from faker import Faker
from pymongo import MongoClient
import random
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Fake veri üretici
fake = Faker()

# MongoDB bağlantısı
client = MongoClient(MONGO_URI) 
db = client["Stellsky"]
users_collection = db["users"]

# Kullanıcı verisi üretici
def generate_user():
    return {
        "full_name": fake.name(),
        "username": fake.user_name(),
        "email": fake.email(),
        "bio": fake.sentence(nb_words=10),
        "profile_picture": fake.image_url(),
        "followers_count": random.randint(0, 10000),
        "following_count": random.randint(0, 1000),
        "posts_count": random.randint(0, 300),
        "is_verified": random.choice([True, False]),
        "created_at": fake.date_time_this_decade()
    }

# 100 kullanıcı verisi üret
users = [generate_user() for _ in range(100)]

# Toplu ekleme (bulk insert)
users_collection.insert_many(users)

print("100 fake user documents inserted into MongoDB.")
