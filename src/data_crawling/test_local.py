from main import handler

# Test Medium article
event = {
    "user": "Paul Iusztin",
    "link": "https://medium.com/decodingml/an-end-to-end-framework-for-production-ready-llm-systems-by-building-your-llm-twin-2cc6bb01141f"
}

result = handler(event, None)
print(result)

# Test GitHub repository
event = {
    "user": "Paul Iusztin",
    "link": "https://github.com/decodingml/llm-twin-course"
}

result = handler(event, None)
print(result)