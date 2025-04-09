import os

class Config:
    SECRET_KEY = os.environ.get('raja') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://quick_aid_z1m4_user:WWKP1FQUA1j0kGt6t0DxobF1Saz9uY1U@dpg-cvllce8gjchc738junp0-a.oregon-postgres.render.com/quick_aid_z1m4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
