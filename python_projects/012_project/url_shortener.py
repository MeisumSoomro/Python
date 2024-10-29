import string
import random
import sqlite3
from datetime import datetime

class URLShortener:
    def __init__(self, db_name='url_shortener.db'):
        self.db_name = db_name
        self.create_table()
        
    def create_table(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS urls
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             original_url TEXT NOT NULL,
             short_code TEXT UNIQUE NOT NULL,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             clicks INTEGER DEFAULT 0)
        ''')
        conn.commit()
        conn.close()
        
    def generate_short_code(self, length=6):
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            if not self.code_exists(code):
                return code
                
    def code_exists(self, code):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('SELECT 1 FROM urls WHERE short_code = ?', (code,))
        exists = c.fetchone() is not None
        conn.close()
        return exists
        
    def shorten_url(self, original_url):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Check if URL already exists
        c.execute('SELECT short_code FROM urls WHERE original_url = ?', (original_url,))
        result = c.fetchone()
        
        if result:
            return result[0]
            
        short_code = self.generate_short_code()
        c.execute('''
            INSERT INTO urls (original_url, short_code)
            VALUES (?, ?)
        ''', (original_url, short_code))
        
        conn.commit()
        conn.close()
        return short_code
        
    def get_original_url(self, short_code):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''
            UPDATE urls SET clicks = clicks + 1
            WHERE short_code = ?
        ''', (short_code,))
        
        c.execute('SELECT original_url FROM urls WHERE short_code = ?', (short_code,))
        result = c.fetchone()
        
        conn.commit()
        conn.close()
        
        return result[0] if result else None
        
    def get_stats(self, short_code):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''
            SELECT original_url, created_at, clicks
            FROM urls WHERE short_code = ?
        ''', (short_code,))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'original_url': result[0],
                'created_at': result[1],
                'clicks': result[2]
            }
        return None

def main():
    shortener = URLShortener()
    
    while True:
        print("\nURL Shortener Menu:")
        print("1. Shorten URL")
        print("2. Get Original URL")
        print("3. View URL Stats")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            url = input("Enter URL to shorten: ")
            short_code = shortener.shorten_url(url)
            print(f"Shortened URL code: {short_code}")
            
        elif choice == '2':
            code = input("Enter short code: ")
            original_url = shortener.get_original_url(code)
            if original_url:
                print(f"Original URL: {original_url}")
            else:
                print("Short code not found!")
                
        elif choice == '3':
            code = input("Enter short code: ")
            stats = shortener.get_stats(code)
            if stats:
                print("\nURL Statistics:")
                print(f"Original URL: {stats['original_url']}")
                print(f"Created at: {stats['created_at']}")
                print(f"Total clicks: {stats['clicks']}")
            else:
                print("Short code not found!")
                
        elif choice == '4':
            break
            
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main() 