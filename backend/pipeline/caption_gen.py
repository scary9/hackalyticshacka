import os

def _fallback_caption(context: str) -> str:
    options = [
        "No way that just happened 😤🔥 unreal clip",
        "The clutch of the year 💀 I can't believe it",
        "He actually pulled it off 😤 this is insane",
        "Bro said hold my controller 🔥💀 crazy clip",
        "This clip goes crazy 😤🔥 you had to be there"
    ]
    import hashlib
    index = int(hashlib.md5(context.encode()).hexdigest(), 16) % len(options)
    return options[index]

def generate_caption(context: str, platform: str = "tiktok") -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": f"Write a single punchy TikTok caption under 150 characters for a gaming highlight clip. Use hype language. Include 2-3 emojis. No hashtags. Context: {context}. Reply with just the caption, nothing else."
                }]
            )
            text = message.content[0].text.strip()
            if len(text) > 150:
                text = text[:147] + "..."
            return text
        except Exception:
            return _fallback_caption(context)
    return _fallback_caption(context)
