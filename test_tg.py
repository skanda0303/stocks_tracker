from notifier import send_telegram_message
print("Attempting to send message...")
result = send_telegram_message("Diagnostic Test Message")
print(f"Result: {result}")
