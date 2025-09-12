#!/usr/bin/env python3
"""
Test script to check image URL validation
"""
import requests

def test_image_url(url):
    """Test if an image URL is accessible"""
    try:
        print(f"🔍 Testing: {url}")
        
        # Basic validation
        if not url or not url.startswith(('http://', 'https://')):
            print("   ❌ Invalid URL format")
            return False
        
        # Try to access the image
        response = requests.head(url, timeout=10, allow_redirects=True)
        
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        # Check if it's actually an image
        content_type = response.headers.get('content-type', '').lower()
        is_image = any(img_type in content_type for img_type in ['image/', 'jpeg', 'png', 'gif', 'webp'])
        
        if response.status_code == 200 and is_image:
            print("   ✅ Valid image URL")
            return True
        else:
            print(f"   ❌ Not accessible or not an image")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Test some example URLs"""
    test_urls = [
        "https://wilo.com/media/image/1.jpg",
        "https://example.com/invalid-url",
        "not-a-url",
        "https://wilo.com/some-page.html"
    ]
    
    print("🧪 TESTING IMAGE URL VALIDATION")
    print("=" * 50)
    
    for url in test_urls:
        test_image_url(url)
        print()

if __name__ == "__main__":
    main()
